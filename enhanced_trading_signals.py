#!/usr/bin/env python3
"""
增强交易信号系统 - 6大功能
1. 买入信号 2. 卖出信号 3. 止盈提醒 4. 止损提醒 5. 挂单评估 6. Top5标的推荐
"""

import os
import sys
sys.path.insert(0, '/Users/zhangkuo/.openclaw/workspace/skills/universal-market-monitor')

import pandas as pd
import numpy as np
from datetime import datetime
from monitor import OKXMonitor, CONFIG

class EnhancedTradingSignals(OKXMonitor):
    def __init__(self):
        super().__init__()
        self.all_symbols = [
            "BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP",
            "XRP-USDT-SWAP", "DOGE-USDT-SWAP", "ADA-USDT-SWAP",
            "AVAX-USDT-SWAP", "LINK-USDT-SWAP", "MATIC-USDT-SWAP",
            "DOT-USDT-SWAP", "UNI-USDT-SWAP", "ATOM-USDT-SWAP"
        ]
    
    # ============ 功能1&2: 买卖信号 ============
    def generate_trading_signals(self, symbol):
        """生成交易信号"""
        df = self.get_klines(symbol, limit=150)
        if df is None or len(df) < 50:
            return None
        
        df = self.calculate_signals(df)
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        signals = []
        
        # 买入信号: 接近支撑+看涨形态+趋势向上
        if (prev['dist_to_sup'] < CONFIG['snr_thresh'] and 
            prev['bullish'] and 
            prev['close'] > prev['ema']):
            
            entry = latest['close']
            stop_loss = entry * (1 - CONFIG['stop_loss_pct'])
            take_profit = entry * (1 + CONFIG['take_profit_pct'])
            
            signals.append({
                'type': 'BUY',
                'symbol': symbol,
                'entry_price': entry,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': self._calculate_confidence(df, 'long'),
                'reason': f"价格接近支撑位(${prev['support']:.4f})+看涨形态+EMA上方"
            })
        
        # 卖出信号: 接近阻力+看跌形态+趋势向下
        elif (prev['dist_to_res'] < CONFIG['snr_thresh'] and 
              prev['bearish'] and 
              prev['close'] < prev['ema']):
            
            entry = latest['close']
            stop_loss = entry * (1 + CONFIG['stop_loss_pct'])
            take_profit = entry * (1 - CONFIG['take_profit_pct'])
            
            signals.append({
                'type': 'SELL',
                'symbol': symbol,
                'entry_price': entry,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': self._calculate_confidence(df, 'short'),
                'reason': f"价格接近阻力位(${prev['resistance']:.4f})+看跌形态+EMA下方"
            })
        
        return signals[0] if signals else None
    
    def _calculate_confidence(self, df, direction):
        """计算信号置信度"""
        score = 50  # 基础分
        
        # 趋势强度
        latest = df.iloc[-1]
        if direction == 'long' and latest['close'] > latest['ema']:
            score += 15
        elif direction == 'short' and latest['close'] < latest['ema']:
            score += 15
        
        # 成交量确认
        if latest['volume'] > latest['avg_vol'] * 1.5:
            score += 10
        
        # 波动率适中
        volatility = df['close'].pct_change().std() * 100
        if 1 < volatility < 5:
            score += 10
        
        return min(score, 95)
    
    # ============ 功能3&4: 止盈止损提醒 ============
    def check_exit_signals(self, positions):
        """检查离场信号"""
        alerts = []
        
        for pos in positions.values():
            if float(pos.get('pos', 0)) == 0:
                continue
            
            symbol = pos['instId']
            entry = float(pos.get('avgPx', 0))
            mark = float(pos.get('markPx', 0))
            side = pos['posSide']
            pnl_pct = float(pos.get('uplRatio', 0)) * 100
            
            # 获取K线判断反转
            df = self.get_klines(symbol, limit=50)
            if df is not None and len(df) > 10:
                latest = df.iloc[-1]
                
                # 止盈提醒: 盈利5%+反转信号
                if pnl_pct >= 5:
                    reversal = False
                    if side == 'long' and latest['bearish']:
                        reversal = True
                    elif side == 'short' and latest['bullish']:
                        reversal = True
                    
                    if reversal:
                        alerts.append({
                            'type': 'TAKE_PROFIT_SUGGEST',
                            'symbol': symbol,
                            'side': side,
                            'pnl_pct': pnl_pct,
                            'suggestion': '建议减仓50%锁定利润，出现反转信号'
                        })
                
                # 止损提醒: 亏损3%+结构破坏
                if pnl_pct <= -3:
                    structure_broken = False
                    if side == 'long' and mark < latest['support']:
                        structure_broken = True
                    elif side == 'short' and mark > latest['resistance']:
                        structure_broken = True
                    
                    if structure_broken:
                        alerts.append({
                            'type': 'STOP_LOSS_SUGGEST',
                            'symbol': symbol,
                            'side': side,
                            'pnl_pct': pnl_pct,
                            'suggestion': '建议止损离场，结构已破坏'
                        })
        
        return alerts
    
    # ============ 功能5: 挂单评估 ============
    def evaluate_pending_orders(self, orders):
        """评估挂单位置合理性"""
        evaluations = []
        
        for order in orders:
            symbol = order['instId']
            order_price = float(order['px'])
            order_side = order['side']  # buy or sell
            
            df = self.get_klines(symbol, limit=100)
            if df is None:
                continue
            
            df = self.calculate_signals(df)
            latest = df.iloc[-1]
            current = latest['close']
            support = latest['support']
            resistance = latest['resistance']
            
            evaluation = {
                'symbol': symbol,
                'order_price': order_price,
                'current_price': current,
                'side': order_side
            }
            
            # 评估逻辑
            if order_side == 'buy':
                if abs(order_price - support) / support < 0.01:
                    evaluation['rating'] = '✅ 优秀'
                    evaluation['comment'] = f'挂单位置接近支撑位(${support:.4f})，合理'
                elif order_price > current * 1.02:
                    evaluation['rating'] = '⚠️ 偏高'
                    evaluation['comment'] = f'挂单高于现价2%以上，可能无法成交'
                elif order_price < support * 0.98:
                    evaluation['rating'] = '❌ 过低'
                    evaluation['comment'] = f'挂单远低于支撑位，需等待深跌'
                else:
                    evaluation['rating'] = '➖ 一般'
                    evaluation['comment'] = '位置中性，可接受'
            else:  # sell
                if abs(order_price - resistance) / resistance < 0.01:
                    evaluation['rating'] = '✅ 优秀'
                    evaluation['comment'] = f'挂单位置接近阻力位(${resistance:.4f})，合理'
                elif order_price < current * 0.98:
                    evaluation['rating'] = '⚠️ 偏低'
                    evaluation['comment'] = f'挂单低于现价2%以上，可能无法成交'
                else:
                    evaluation['rating'] = '➖ 一般'
                    evaluation['comment'] = '位置中性，可接受'
            
            evaluations.append(evaluation)
        
        return evaluations
    
    # ============ 功能6: Top5标的推荐 ============
    def scan_top5_opportunities(self):
        """扫描全市场，推荐Top5交易标的"""
        print(f"\n🔍 扫描 {len(self.all_symbols)} 个交易标的...")
        
        opportunities = []
        
        for symbol in self.all_symbols:
            try:
                signal = self.generate_trading_signals(symbol)
                if signal and signal['confidence'] >= 60:
                    opportunities.append(signal)
            except Exception as e:
                continue
        
        # 按置信度排序
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)
        top5 = opportunities[:5]
        
        return top5
    
    def format_top5_report(self, top5):
        """格式化Top5报告"""
        report = []
        report.append("\n" + "="*80)
        report.append("🏆 TOP 5 交易机会推荐")
        report.append("="*80)
        
        for i, opp in enumerate(top5, 1):
            stars = "⭐" * (opp['confidence'] // 20)
            report.append(f"\n{i}. 【{opp['type']}】{opp['symbol']}")
            report.append(f"   推荐指数: {opp['confidence']}/100 {stars}")
            report.append(f"   建议挂单: ${opp['entry_price']:.4f}")
            report.append(f"   止损价格: ${opp['stop_loss']:.4f}")
            report.append(f"   止盈价格: ${opp['take_profit']:.4f}")
            report.append(f"   推荐原因: {opp['reason']}")
        
        report.append("\n" + "="*80)
        return "\n".join(report)

# 测试运行
if __name__ == '__main__':
    signals = EnhancedTradingSignals()
    
    # 测试Top5扫描
    top5 = signals.scan_top5_opportunities()
    if top5:
        print(signals.format_top5_report(top5))
    else:
        print("暂无高置信度交易机会")
