#!/usr/bin/env python3
"""
OKX智能盯盘系统 V2
功能：信号检测 + 价格警报 + 持仓监控 + 异常检测
"""

import os
import json
import time
import hmac
import base64
import hashlib
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode, quote

# ============ 配置 ============
CONFIG = {
    "leverage": 3,
    "symbols": ["BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP"],
    "timeframe": "1H",
    # SMC+SNR参数
    "swing_lb": 30,
    "pivot_lb": 2,
    "snr_thresh": 0.08,
    "stop_loss_pct": 0.033,
    "take_profit_pct": 0.084,
    "trend_period": 30,
    # 仓位管理
    "position_pct": 0.20,
    "max_positions": 2,
    "min_order_usdt": 3,
    # 警报阈值
    "price_alert_threshold": 0.02,  # 2%价格变动警报
    "balance_change_threshold": 0.05,  # 5%余额变动警报
}

ALERT_LOG = "/Users/zhangkuo/.openclaw/workspace/alert_log.json"
TRADE_LOG = "/Users/zhangkuo/.openclaw/workspace/trade_log.json"

class OKXMonitor:
    def __init__(self):
        self.api_key = os.environ.get("OKX_API_KEY")
        self.api_secret = os.environ.get("OKX_API_SECRET")
        self.passphrase = os.environ.get("OKX_PASSPHRASE")
        self.base_url = "https://www.okx.com"
        self.last_prices = {}
        self.last_balance = None
        
    def _get_timestamp(self):
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    def _sign(self, timestamp, method, request_path, body=''):
        message = timestamp + method.upper() + request_path + body
        mac = hmac.new(self.api_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
        return base64.b64encode(mac.digest()).decode('utf-8')
    
    def _request(self, method, path, body=None):
        if not all([self.api_key, self.api_secret, self.passphrase]):
            return None
        timestamp = self._get_timestamp()
        headers = {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': self._sign(timestamp, method, path, json.dumps(body) if body else ''),
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
        try:
            url = self.base_url + path
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            else:
                response = requests.post(url, headers=headers, json=body, timeout=10)
            return response.json()
        except Exception as e:
            print(f"❌ Request error: {e}")
            return None
    
    # ============ 功能1: 价格警报 ============
    def check_price_alerts(self):
        """监控价格突破支撑/阻力位"""
        alerts = []
        for symbol in CONFIG['symbols']:
            df = self.get_klines(symbol, limit=100)
            if df is None or len(df) < 50:
                continue
            
            # 计算支撑阻力
            df = self.calculate_signals(df)
            latest = df.iloc[-1]
            current_price = latest['close']
            
            # 检查是否突破
            if symbol in self.last_prices:
                last_price = self.last_prices[symbol]
                price_change = abs(current_price - last_price) / last_price
                
                # 突破支撑位向下
                if current_price < latest['support'] and last_price >= latest['support']:
                    alerts.append({
                        'type': 'breakdown',
                        'symbol': symbol,
                        'price': current_price,
                        'level': latest['support'],
                        'message': f'🚨 {symbol} 跌破支撑位 ${latest["support"]:.2f}'
                    })
                
                # 突破阻力位向上
                elif current_price > latest['resistance'] and last_price <= latest['resistance']:
                    alerts.append({
                        'type': 'breakout',
                        'symbol': symbol,
                        'price': current_price,
                        'level': latest['resistance'],
                        'message': f'🚀 {symbol} 突破阻力位 ${latest["resistance"]:.2f}'
                    })
                
                # 大幅波动警报
                elif price_change > CONFIG['price_alert_threshold']:
                    direction = '上涨' if current_price > last_price else '下跌'
                    alerts.append({
                        'type': 'volatility',
                        'symbol': symbol,
                        'price': current_price,
                        'change_pct': price_change * 100,
                        'message': f'⚠️ {symbol} 大幅{direction} {price_change*100:.2f}%'
                    })
            
            self.last_prices[symbol] = current_price
        
        return alerts
    
    # ============ 功能2: 持仓监控 ============
    def monitor_positions(self):
        """监控持仓SL/TP状态"""
        positions = self.get_positions()
        alerts = []
        
        for pos in positions.values():
            if float(pos.get('pos', 0)) == 0:
                continue
            
            symbol = pos['instId']
            entry_price = float(pos.get('avgPx', 0))
            current_price = float(pos.get('markPx', 0))
            pos_side = pos['posSide']  # long or short
            
            # 计算盈亏
            if pos_side == 'long':
                pnl_pct = (current_price - entry_price) / entry_price
                # 检查止损
                if pnl_pct <= -CONFIG['stop_loss_pct']:
                    alerts.append({
                        'type': 'stop_loss',
                        'symbol': symbol,
                        'side': pos_side,
                        'pnl_pct': pnl_pct * 100,
                        'message': f'⛔ {symbol} 多头触及止损 {pnl_pct*100:.2f}%'
                    })
                # 检查止盈
                elif pnl_pct >= CONFIG['take_profit_pct']:
                    alerts.append({
                        'type': 'take_profit',
                        'symbol': symbol,
                        'side': pos_side,
                        'pnl_pct': pnl_pct * 100,
                        'message': f'✅ {symbol} 多头达到止盈 {pnl_pct*100:.2f}%'
                    })
            else:
                pnl_pct = (entry_price - current_price) / entry_price
                if pnl_pct <= -CONFIG['stop_loss_pct']:
                    alerts.append({
                        'type': 'stop_loss',
                        'symbol': symbol,
                        'side': pos_side,
                        'pnl_pct': pnl_pct * 100,
                        'message': f'⛔ {symbol} 空头触及止损 {pnl_pct*100:.2f}%'
                    })
                elif pnl_pct >= CONFIG['take_profit_pct']:
                    alerts.append({
                        'type': 'take_profit',
                        'symbol': symbol,
                        'side': pos_side,
                        'pnl_pct': pnl_pct * 100,
                        'message': f'✅ {symbol} 空头达到止盈 {pnl_pct*100:.2f}%'
                    })
        
        return alerts
    
    # ============ 功能3: 异常检测 ============
    def detect_anomalies(self):
        """检测账户异常变动"""
        alerts = []
        current_balance = self.get_account_balance()
        
        if current_balance > 0 and self.last_balance is not None:
            balance_change = abs(current_balance - self.last_balance) / self.last_balance
            
            if balance_change > CONFIG['balance_change_threshold']:
                direction = '增加' if current_balance > self.last_balance else '减少'
                alerts.append({
                    'type': 'balance_anomaly',
                    'balance': current_balance,
                    'change_pct': balance_change * 100,
                    'message': f'🔔 账户余额异常{direction} {balance_change*100:.2f}%，当前: ${current_balance:.2f}'
                })
        
        self.last_balance = current_balance
        return alerts
    
    # ============ 原有方法 ============
    def get_klines(self, symbol, limit=100):
        path = f"/api/v5/market/candles?instId={symbol}&bar={CONFIG['timeframe']}&limit={limit}"
        data = self._request('GET', path)
        if data and data.get('code') == '0':
            df = pd.DataFrame(data['data'], columns=['timestamp', 'open', 'high', 'low', 'close', 'vol', 'volCcy', 'volCcyQuote', 'confirm'])
            df[['open', 'high', 'low', 'close', 'vol']] = df[['open', 'high', 'low', 'close', 'vol']].astype(float)
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
            return df.iloc[::-1].reset_index(drop=True)
        return None
    
    def calculate_signals(self, df):
        cfg = CONFIG
        df = df.copy()
        swing_w = cfg["swing_lb"] * 2 + 1
        df['swing_high'] = df['high'].rolling(window=swing_w, center=True).max()
        df['swing_low'] = df['low'].rolling(window=swing_w, center=True).min()
        pivot_w = cfg["pivot_lb"] * 2 + 1
        df['pivot_high'] = df['high'].rolling(window=pivot_w, center=True).max()
        df['pivot_low'] = df['low'].rolling(window=pivot_w, center=True).min()
        df['resistance'] = df.loc[df['high'] == df['pivot_high'], 'high'].reindex(df.index).ffill().bfill()
        df['support'] = df.loc[df['low'] == df['pivot_low'], 'low'].reindex(df.index).ffill().bfill()
        return df.dropna()
    
    def get_account_balance(self):
        data = self._request('GET', '/api/v5/account/balance')
        if data and data.get('code') == '0':
            for detail in data['data'][0].get('details', []):
                if detail['ccy'] == 'USDT':
                    return float(detail['availBal'])
        return 0
    
    def get_positions(self):
        data = self._request('GET', '/api/v5/account/positions')
        if data and data.get('code') == '0':
            return {p['instId']: p for p in data['data']}
        return {}
    
    def log_alert(self, alert):
        """记录警报"""
        alerts = []
        if os.path.exists(ALERT_LOG):
            with open(ALERT_LOG, 'r') as f:
                alerts = json.load(f)
        alert['timestamp'] = datetime.now().isoformat()
        alerts.append(alert)
        with open(ALERT_LOG, 'w') as f:
            json.dump(alerts[-100:], f, indent=2)  # 保留最近100条
    
    def run_monitoring_cycle(self):
        """运行完整监控周期"""
        print(f"\n[{datetime.now()}] 🔍 开始监控...")
        
        all_alerts = []
        
        # 1. 价格警报
        price_alerts = self.check_price_alerts()
        all_alerts.extend(price_alerts)
        
        # 2. 持仓监控
        position_alerts = self.monitor_positions()
        all_alerts.extend(position_alerts)
        
        # 3. 异常检测
        anomaly_alerts = self.detect_anomalies()
        all_alerts.extend(anomaly_alerts)
        
        # 输出并记录警报
        if all_alerts:
            print(f"\n🚨 检测到 {len(all_alerts)} 个警报:")
            for alert in all_alerts:
                print(f"  {alert['message']}")
                self.log_alert(alert)
        else:
            print("  ✅ 一切正常")
        
        return all_alerts

if __name__ == '__main__':
    monitor = OKXMonitor()
    monitor.run_monitoring_cycle()
