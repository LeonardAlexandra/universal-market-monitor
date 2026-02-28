# Universal Market Monitor

通用市场监控系统 - 支持多交易所的实时盯盘工具

## 🚀 Features

### 基础监控
| 功能 | 描述 |
|------|------|
| 📊 **价格警报** | 支撑/阻力位突破检测，大幅波动提醒 |
| 🎯 **持仓监控** | 自动追踪SL/TP状态，盈亏实时监控 |
| 🔔 **异常检测** | 账户余额异常变动警报 |

### 增强交易信号 (V2新增)
| 功能 | 描述 | 触发条件 |
|------|------|---------|
| 🟢 **买入信号** | 推荐做多机会 | 接近支撑+看涨形态+趋势向上，置信度≥65 |
| 🔴 **卖出信号** | 推荐做空机会 | 接近阻力+看跌形态+趋势向下，置信度≥65 |
| 💰 **止盈提醒** | 建议锁定利润 | 盈利5%+出现反转信号 |
| ⛔ **止损提醒** | 建议止损离场 | 亏损3%+结构破坏 |
| 📋 **挂单评估** | 评估挂单位置合理性 | 对比支撑/阻力位 |
| 🏆 **Top5推荐** | 全市场最佳机会扫描 | 每小时扫描12个标的，推荐≥70分机会 |

### 飞书通知 (V2新增)
- 实时推送高置信度交易信号
- 每小时Top5机会自动发送
- 持仓风险及时提醒

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

### 基础监控
```bash
python3 monitor.py
```

### 带飞书通知的完整监控（推荐）
```bash
python3 monitor_with_feishu.py
```

### 单独扫描Top5机会
```bash
python3 enhanced_trading_signals.py
```

## 📱 飞书通知配置

系统会自动在以下情况发送飞书消息：
- ✅ Top5推荐：每小时扫描，有≥70分机会时
- ✅ 进场信号：置信度≥65的买入信号
- ✅ 止损/止盈：触发风险管理条件时

## 📝 Alert Types

### 基础警报
- `breakout`: 突破阻力位向上
- `breakdown`: 跌破支撑位向下
- `stop_loss`: 触及止损
- `take_profit`: 达到止盈
- `volatility`: 大幅波动
- `balance_anomaly`: 余额异常变动

### 交易信号 (V2)
- `BUY`: 推荐买入信号
- `SELL`: 推荐卖出信号
- `TAKE_PROFIT_SUGGEST`: 建议止盈
- `STOP_LOSS_SUGGEST`: 建议止损
- `PENDING_ORDER_ADVICE`: 挂单位置建议

## 🔧 File Structure

```
universal-market-monitor/
├── README.md                      # 项目说明
├── SKILL.md                       # OpenClaw skill规范
├── _meta.json                     # Skill元数据
├── config.json                    # 配置文件
├── monitor.py                     # 基础监控程序
├── enhanced_trading_signals.py    # 增强交易信号系统
├── feishu_notifier.py            # 飞书通知模块
└── monitor_with_feishu.py        # 集成飞书通知的完整监控
```

## 🔄 Version History

### v1.0.0 (Initial)
- 基础监控功能（价格、持仓、异常）
- OKX API接入
- 支撑/阻力计算

### v2.0.0 (Current)
- 新增6大交易信号功能
- 飞书实时通知
- Top5机会扫描
- 挂单智能评估
- 双账户监控支持

## ⚠️ Risk Warning

- 交易有风险，投资需谨慎
- 信号仅供参考，不构成投资建议
- 建议先使用模拟盘测试
- 小额资金验证策略有效性
- API权限需谨慎设置（建议只开启读取+交易，关闭提现）

## 📄 License

MIT

## 👤 Author

LeonardAlexandra
