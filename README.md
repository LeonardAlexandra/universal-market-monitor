# Universal Market Monitor

通用市场监控系统 - 支持多交易所的实时盯盘工具

## 🚀 Features

| 功能 | 描述 |
|------|------|
| 📊 **价格警报** | 支撑/阻力位突破检测，大幅波动提醒 |
| 🎯 **持仓监控** | 自动追踪SL/TP状态，盈亏实时监控 |
| 🔔 **异常检测** | 账户余额异常变动警报 |
| 🔌 **多交易所** | 当前支持OKX，可扩展其他交易所 |

## 📦 Installation

```bash
git clone https://github.com/LeonardAlexandra/universal-market-monitor.git
cd universal-market-monitor
pip install requests pandas numpy
```

## ⚙️ Configuration

1. 设置API密钥环境变量：
```bash
export OKX_API_KEY="your-api-key"
export OKX_API_SECRET="your-api-secret"
export OKX_PASSPHRASE="your-passphrase"
```

2. 编辑 `config.json` 自定义参数

## 🎮 Usage

```bash
python3 monitor.py
```

输出示例：
```
[2026-03-01 01:00:00] 🔍 开始监控...
🚨 检测到 2 个警报:
  🚀 BTC-USDT-SWAP 突破阻力位 $65,000
  ✅ BTC-USDT-SWAP 多头达到止盈 +8.5%
```

## 📝 Alert Types

- `breakout`: 突破阻力位向上
- `breakdown`: 跌破支撑位向下
- `stop_loss`: 触及止损
- `take_profit`: 达到止盈
- `volatility`: 大幅波动
- `balance_anomaly`: 余额异常变动

## 🔧 Customization

修改 `monitor.py` 中的 `CONFIG` 字典：

```python
CONFIG = {
    "symbols": ["BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP"],
    "price_alert_threshold": 0.02,  # 2%价格变动触发警报
    "balance_change_threshold": 0.05,  # 5%余额变动触发警报
}
```

## ⚠️ Risk Warning

- 交易有风险，投资需谨慎
- 建议先使用模拟盘测试
- 小额资金验证策略有效性

## 📄 License

MIT

## 👤 Author

LeonardAlexandra
