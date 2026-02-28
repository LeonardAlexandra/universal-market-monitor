---
name: universal-market-monitor
displayName: Universal Market Monitor
description: Multi-exchange market monitoring system with price alerts, position tracking, and anomaly detection.
metadata:
  {
    "openclaw":
      {
        "requires": { "pip": ["requests", "pandas", "numpy"] },
        "env": ["OKX_API_KEY", "OKX_API_SECRET", "OKX_PASSPHRASE"],
      },
  }
---

# Universal Market Monitor

通用市场监控系统，支持多交易所API接入，提供实时价格警报、持仓监控和异常检测功能。

## Features

- **价格突破警报**: 监控支撑/阻力位突破，大幅波动提醒
- **持仓SL/TP监控**: 自动追踪止损止盈状态
- **账户异常检测**: 余额异常变动警报
- **多交易所支持**: 当前支持OKX，可扩展Binance等

## Quick Start

```bash
# Set environment variables
export OKX_API_KEY="your-api-key"
export OKX_API_SECRET="your-api-secret"
export OKX_PASSPHRASE="your-passphrase"

# Run monitor
python3 monitor.py
```

## Configuration

Edit `config.json`:

```json
{
  "symbols": ["BTC-USDT-SWAP", "ETH-USDT-SWAP"],
  "price_alert_threshold": 0.02,
  "balance_change_threshold": 0.05
}
```

## Alerts

Monitor outputs alerts for:
- Support/resistance breakouts
- Stop-loss / take-profit triggers
- Balance anomalies
- High volatility events

## Author

LeonardAlexandra
