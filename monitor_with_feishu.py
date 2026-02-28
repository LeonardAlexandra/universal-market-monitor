#!/usr/bin/env python3
"""
飞书通知版监控系统 - 每小时Top5 + 实时信号推送
"""
import os
import sys
sys.path.insert(0, '/Users/zhangkuo/.openclaw/workspace/skills/universal-market-monitor')
sys.path.insert(0, '/Users/zhangkuo/.openclaw/workspace')

from datetime import datetime
from integrated_monitor_v2 import IntegratedMonitor
from feishu_notifier import FeishuNotifier

class MonitorWithFeishu(IntegratedMonitor):
    def __init__(self):
        super().__init__()
        self.notifier = FeishuNotifier()
        self.last_top5_notify = None
        
    def run_full_monitoring(self):
        """运行完整监控并发送飞书通知"""
        print(f"\n{'#'*60}")
        print(f"# 🚀 飞书通知版监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*60}")
        
        all_alerts = []
        entry_signals = []
        
        # 监控两个账户
        for account_type in ['test', 'main']:
            try:
                alerts = self.monitor_account(account_type)
                all_alerts.extend(alerts)
                
                # 收集进场信号
                for alert in alerts:
                    if alert.get('source') == 'entry_signal':
                        entry_signals.append(alert)
            except Exception as e:
                print(f"❌ {self.accounts[account_type]['name']} 错误: {e}")
        
        # 发送进场信号通知（高置信度）
        for signal in entry_signals:
            if self.notifier.should_notify_entry(signal):
                print(f"\n📱 发送飞书通知: {signal['symbol']} 进场信号")
                self.notifier.send_trade_alert('ENTRY_SIGNAL', signal)
        
        # 每小时检查一次Top5（00-10分钟之间）
        current_minute = datetime.now().minute
        if current_minute <= 10:
            print(f"\n🏆 执行Top5扫描...")
            top5 = self.signal_generator.scan_top5_opportunities()
            
            if self.notifier.should_notify_top5(top5):
                report = self.signal_generator.format_top5_report(top5)
                print(f"\n📱 发送飞书Top5通知")
                self.notifier.send_trade_alert('TOP5_OPPORTUNITY', report)
                self.last_top5_notify = datetime.now()
            else:
                print("  暂无高置信度机会（需≥70分），跳过通知")
        
        # 汇总报告
        print(f"\n{'='*60}")
        print("📋 监控汇总")
        print(f"{'='*60}")
        
        if all_alerts:
            print(f"\n🚨 共 {len(all_alerts)} 个信号/警报:")
            for alert in all_alerts:
                print(f"  {self.format_alert(alert)}")
        else:
            print("\n✅ 无紧急信号，市场平静")
        
        print(f"\n{'#'*60}")
        print(f"# 下次检查: 5分钟后")
        if self.last_top5_notify:
            print(f"# 上次Top5通知: {self.last_top5_notify.strftime('%H:%M')}")
        print(f"{'#'*60}\n")
        
        return all_alerts

if __name__ == '__main__':
    monitor = MonitorWithFeishu()
    monitor.run_full_monitoring()
