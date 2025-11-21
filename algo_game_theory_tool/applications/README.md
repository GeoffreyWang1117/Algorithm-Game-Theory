# 算法博弈论实际应用框架

这个目录包含从教学练习到实际可部署系统的完整实现。

## 概述

将第12章的5个应用场景从教学练习升级为完整的核心算法实现。

### 当前状态

✅ **已完成**: Citi Bike 共享单车再平衡系统
⏳ **计划中**:
- 广告拍卖系统 (GSP)
- 医院-住院医匹配 (NRMP)
- 成本分摊系统 (Shapley Value)
- 频谱拍卖系统 (FCC)

## 目录结构

```
applications/
├── README.md                    # 本文档
│
├── bike_sharing/                # ✅ Citi Bike 再平衡系统
│   ├── README.md                # 详细文档
│   ├── requirements.txt         # Python 依赖
│   │
│   ├── configs/                 # 配置文件
│   │   ├── data_config.yaml     # 数据下载配置
│   │   ├── model_config.yaml    # ML模型配置
│   │   └── incentive_config.yaml # 激励机制配置
│   │
│   ├── data/                    # 数据目录（gitignore）
│   │   ├── raw/                 # 原始数据
│   │   └── processed/           # 处理后数据
│   │
│   ├── models/                  # 训练好的模型（gitignore）
│   │
│   ├── data_pipeline.py         # 数据下载和ETL
│   ├── demand_model.py          # 需求预测模型
│   ├── incentive_optimizer.py   # 激励优化算法
│   └── run_demo.py              # 完整演示
│
├── ad_auction/                  # ⏳ 广告拍卖系统（计划）
├── hospital_matching/           # ⏳ 医院匹配（计划）
├── cost_sharing/                # ⏳ 成本分摊（计划）
└── spectrum_auction/            # ⏳ 频谱拍卖（计划）
```

## Citi Bike 再平衡系统

### 功能特点

1. **数据管道**
   - 自动下载 Citi Bike 公开数据（S3）
   - 数据清洗和验证
   - 时序聚合和特征工程

2. **需求预测**
   - XGBoost/Random Forest 模型
   - 时空特征工程（滞后、滚动统计）
   - 模型评估和持久化

3. **激励优化**
   - 静态定价（Simple & Fast）
   - 动态定价（Predictive，考虑未来需求）
   - 凸优化（CVXPY，最优解）

4. **用户响应模型**
   - Logistic 选择模型
   - 参数估计和校准
   - 蒙特卡洛模拟

### 快速开始

```bash
# 1. 安装依赖
cd applications/bike_sharing
pip install -r requirements.txt

# 2. 运行演示（使用模拟数据）
python run_demo.py
```

演示输出：
- 每小时激励优化结果
- ROI 和成本分析
- 策略对比（静态 vs 动态）
- 可视化图表（`outputs/figures/`）

### 使用真实数据

```bash
# 下载最近3个月的 Citi Bike 数据
python data_pipeline.py --months 3

# 训练需求预测模型
python demand_model.py

# 运行激励优化
python incentive_optimizer.py
```

### 核心算法

**1. 需求预测模型**

```python
from demand_model import DemandPredictor

predictor = DemandPredictor.load('models/demand_predictor.pkl')

# 预测单个站点
forecast = predictor.predict(
    station_id='6726.08',
    timestamp='2024-06-20 08:00:00',
    horizon=24  # 预测未来24小时
)
```

**2. 激励优化**

```python
from incentive_optimizer import IncentiveOptimizer, Station

optimizer = IncentiveOptimizer()
optimizer.strategy = 'dynamic'  # or 'static', 'optimization'

# 创建站点状态
stations = [
    Station('downtown', capacity=100, current_bikes=15, net_flow_forecast=-10),
    # ...
]

# 优化激励
incentives, simulation = optimizer.optimize(stations)

print(f"ROI: {simulation['roi']:.2f}x")
print(f"Net Savings: ${simulation['net_savings']:.2f}")
```

### 关键结果

基于模拟数据（20个站点，24小时）：

| 策略 | 激励成本 | 节省成本 | ROI | 参与率 |
|------|---------|---------|-----|--------|
| 无激励 | $0 | $0 | - | 0% |
| 静态定价 | $1,200 | $2,280 | 1.9x | 18% |
| 动态定价 | $1,500 | $3,600 | 2.4x | 25% |

### 技术亮点

1. **时空特征工程**
   - 周期性编码（sin/cos）
   - 多尺度滞后特征
   - 滚动统计窗口

2. **博弈论应用**
   - 激励兼容性约束
   - 用户效用函数建模
   - 纳什均衡分析

3. **优化算法**
   - 凸优化（CVXPY）
   - 约束满足（预算、容量）
   - 多目标权衡

4. **可扩展性**
   - 配置驱动设计
   - 模块化架构
   - 易于添加新策略

## 开发路线图

### 短期（已完成）

- [x] Citi Bike 再平衡系统
  - [x] 数据管道
  - [x] 需求预测模型
  - [x] 激励优化算法
  - [x] 演示程序
  - [x] 文档

### 中期（1-3个月）

- [ ] 广告拍卖系统 (GSP)
  - [ ] 数据集成（iPinYou, Criteo）
  - [ ] CTR 预估模型
  - [ ] GSP 拍卖机制实现
  - [ ] 预算优化

- [ ] 医院-住院医匹配 (NRMP)
  - [ ] 合成数据生成器
  - [ ] Deferred Acceptance 算法
  - [ ] Couples 问题处理
  - [ ] 稳定性验证

### 长期（3-6个月）

- [ ] 成本分摊系统
  - [ ] Shapley Value 计算（精确 + 近似）
  - [ ] 云计算成本数据集成
  - [ ] 拼车成本分摊应用

- [ ] 频谱拍卖系统
  - [ ] FCC 数据集成
  - [ ] 组合拍卖 WDP 求解器
  - [ ] VCG 定价机制
  - [ ] 拍卖格式对比

## 数据集资源

### Citi Bike（已集成）
- **来源**: https://citibikenyc.com/system-data
- **格式**: CSV (骑行记录)
- **规模**: 200万+ 骑行/月
- **开放**: ✅ 完全公开

### iPinYou（计划用于广告拍卖）
- **来源**: https://contest.ipinyou.com/
- **格式**: TSV (竞价日志)
- **规模**: 1000万+ 展示
- **开放**: ✅ 研究用途

### NRMP统计（计划用于医院匹配）
- **来源**: https://www.nrmp.org/
- **格式**: 聚合统计
- **规模**: 4万+ 参与者/年
- **开放**: ⚠️ 仅聚合数据（隐私保护）

### FCC拍卖（计划用于频谱拍卖）
- **来源**: https://www.fcc.gov/
- **格式**: CSV/XML
- **规模**: 数十亿美元交易
- **开放**: ✅ 公开记录

## 贡献指南

想要贡献新的应用实现？

1. **Fork 仓库**
2. **创建应用目录**
   ```bash
   mkdir applications/your_application
   cd applications/your_application
   ```

3. **遵循标准结构**
   - `README.md` - 详细文档
   - `requirements.txt` - 依赖
   - `configs/` - 配置文件
   - 核心算法文件
   - `run_demo.py` - 演示程序

4. **文档要求**
   - 问题描述和动机
   - 数据来源和格式
   - 算法设计和实现
   - 使用示例
   - 评估结果

5. **提交 Pull Request**

## 学术引用

本实现参考的学术论文：

### Bike Sharing
- Freund et al. (2019). "Data-Driven Rebalancing Methods for Bike-Share Systems"
- Pfrommer et al. (2014). "Dynamic Vehicle Redistribution and Online Price Incentives"
- Singla et al. (2015). "Incentivizing Users for Balancing Bike Sharing Systems"

### Ad Auctions
- Edelman et al. (2007). "Internet Advertising and the Generalized Second-Price Auction"
- Varian (2007). "Position Auctions"

### Matching Theory
- Roth & Peranson (1999). "The Redesign of the Matching Market for American Physicians"
- Abdulkadiroğlu & Sönmez (2003). "School Choice"

### Spectrum Auctions
- Milgrom (2004). "Putting Auction Theory to Work"
- Cramton (2013). "Spectrum Auction Design"

## 许可证

MIT License

## 联系方式

- GitHub Issues: 问题反馈
- Discussions: 技术讨论
- Email: 商业合作

---

**注意**: 本项目仅用于教育和研究目的。实际部署需要与相关机构合作并遵守法规。
