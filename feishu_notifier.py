#!/usr/bin/env python3
"""
飞书通知模块 - 用于交易信号和监控警报
"""
import os
import json
from datetime import datetime

class FeishuNotifier:
    def __init__(self):
        # 使用当前会话的feishu通道
        self.enabled = True
    
    def send_trade_alert(self, alert_type, content):
        """发送交易信号通知"""
        if not self.enabled:
            return False
        
        # 构建消息内容
        message = self._format_message(alert_type, content)
        
        # 输出到标准输出（OpenClaw会自动转发到feishu）
        print(f"\n{'='*60}")
        print(f"🚀 FEISHU_ALERT_START")
        print(message)
        print(f"🚀 FEISHU_ALERT_END")
        print(f"{'='*60}\n")
        
        return True
    
    def _format_message(self, alert_type, content):
        """格式化消息"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if alert_type == 'TOP5_OPPORTUNITY':
            return f"""
【交易机会推荐】{timestamp}

{content}

建议操作：评估后决定是否挂单
风险提示：仅供参考，不构成投资建议
"""
        elif alert_type == 'ENTRY_SIGNAL':
            signal = content
            direction = "🟢买入" if signal['type'] == 'BUY' else "🔴卖出"
            stars = "⭐" * (signal['confidence'] // 20)
            
            return f"""
【进场信号】{timestamp} {stars}

币种: {signal['symbol']}
方向: {direction}
置信度: {signal['confidence']}/100
建议挂单: ${signal['entry_price']:.4f}
止损价格: ${signal['stop_loss']:.4f}
止盈价格: ${signal['take_profit']:.4f}
推荐理由: {signal['reason']}

账户: {signal.get('account', '未知')}
"""
        elif alert_type == 'EXIT_SIGNAL':
            return f"""
【离场提醒】{timestamp}

{content['message']}
盈亏: {content.get('pnl_pct', 0):+.2f}%
建议: {content.get('suggestion', '关注市场')}

账户: {content.get('account', '未知')}
"""
        elif alert_type == 'PENDING_ORDER_ADVICE':
            return f"""
【挂单位置建议】{timestamp}

{content}

请检查当前挂单是否需要调整
"""
        else:
            return f"""
【监控通知】{timestamp}

{str(content)}
"""
    
    def should_notify_top5(self, top5_list):
        """判断是否应该发送Top5通知"""
        if not top5_list:
            return False
        
        # 有置信度>=70的机会才通知
        high_confidence = [s for s in top5_list if s['confidence'] >= 70]
        return len(high_confidence) > 0
    
    def should_notify_entry(self, signal):
        """判断是否应该发送进场信号"""
        if not signal:
            return False
        # 置信度>=65且是买入信号（更谨慎）
        return signal['confidence'] >= 65 and signal['type'] == 'BUY'

# 测试
if __name__ == '__main__':
    notifier = FeishuNotifier()
    
    # 测试消息
    test_signal = {
        'type': 'BUY',
        'symbol': 'BTC-USDT-SWAP',
        'confidence': 75,
        'entry_price': 65000,
        'stop_loss': 63000,
        'take_profit': 70000,
        'reason': '突破阻力位+放量上涨',
        'account': '主账户'
    }
    
    notifier.send_trade_alert('ENTRY_SIGNAL', test_signal)
