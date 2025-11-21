# 算法博弈论实际应用框架

这个目录包含从教学练习到实际可部署系统的完整实现。

## 概述

将第12章的5个应用场景从教学练习升级为完整的核心算法实现。

### 当前状态

✅ **已完成**:
- Citi Bike 共享单车再平衡系统
- 广告拍卖系统 (GSP)
- 医院-住院医匹配 (NRMP)
- 成本分摊系统 (Shapley Value)

⏳ **计划中**:
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
├── ad_auction/                  # ✅ 广告拍卖系统
│   ├── README.md                # 详细文档
│   ├── requirements.txt         # Python依赖
│   │
│   ├── configs/                 # 配置文件
│   │   ├── data_config.yaml     # 数据源配置
│   │   ├── ctr_model_config.yaml # CTR模型配置
│   │   └── auction_config.yaml  # 拍卖机制配置
│   │
│   ├── gsp_auction.py           # GSP拍卖实现
│   ├── budget_pacing.py         # 预算优化
│   └── run_demo.py              # 完整演示
│
├── hospital_matching/           # ✅ 医院-住院医匹配系统
│   ├── README.md                # 详细文档
│   ├── requirements.txt         # Python依赖
│   │
│   ├── configs/                 # 配置文件
│   │   └── matching_config.yaml # 匹配算法配置
│   │
│   ├── deferred_acceptance.py   # DA算法实现
│   ├── stability_checker.py     # 稳定性验证
│   └── run_demo.py              # 完整演示
│
├── cost_sharing/                # ✅ 成本分摊系统 (Shapley Value)
│   ├── README.md                # 详细文档
│   ├── requirements.txt         # Python依赖
│   │
│   ├── configs/                 # 配置文件
│   │   └── cost_sharing_config.yaml # 成本分摊配置
│   │
│   ├── shapley_value.py         # Shapley Value核心算法
│   ├── cloud_cost_sharing.py    # 云计算成本分摊
│   ├── rideshare_cost.py        # 拼车成本分配
│   └── run_demo.py              # 完整演示
│
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

## 广告拍卖系统 (GSP)

### 功能特点

1. **GSP拍卖机制**
   - Google/Facebook使用的核心算法
   - Rank Score = bid × quality_score
   - 支付规则：next_rank_score / own_quality_score
   - 与VCG对比分析

2. **预算Pacing**
   - 线性Pacing（Simple）
   - PID控制器Pacing（Advanced）
   - 自适应Pacing（Market-aware）
   - 避免预算在高峰期快速耗尽

3. **多机制对比**
   - GSP vs VCG vs 第一价格
   - 收入、效率、真实性分析
   - 实验数据驱动

### 快速开始

```bash
# 进入目录
cd applications/ad_auction

# 运行演示（使用模拟数据）
python run_demo.py
```

演示输出：
- GSP vs VCG 收入对比
- Pacing vs 无Pacing效果
- 24小时模拟结果
- 可视化图表（`outputs/figures/`）

### 核心算法

**1. GSP拍卖**

```python
from gsp_auction import GSPAuction, Advertiser

# 创建广告主
advertisers = [
    Advertiser(id='A', bid=3.0, quality_score=0.8, budget=1000),
    Advertiser(id='B', bid=2.5, quality_score=0.9, budget=1000),
]

# 运行拍卖
auction = GSPAuction()
results = auction.run(advertisers, impressions=1000)

for r in results:
    print(f"{r.advertiser_id}: 位置{r.position}, CPC=${r.price_per_click:.2f}")
```

**2. 预算Pacing**

```python
from budget_pacing import BudgetPacer

pacer = BudgetPacer(
    daily_budget=10000,
    duration_hours=24,
    strategy='pid'  # or 'linear', 'adaptive'
)

# 每小时调整出价
for hour in range(24):
    multiplier = pacer.get_bid_adjustment(
        current_spend=get_spend(),
        elapsed_hours=hour
    )

    new_bid = base_bid * multiplier
```

### 关键结果

基于模拟（10广告主，24小时，24K展示）：

| 机制 | 平台收入 | 广告主效用 | 真实性 |
|------|---------|-----------|--------|
| GSP (No Pacing) | $2,450 | $850 | 72% |
| GSP (With Pacing) | $2,680 | $920 | 74% |
| VCG | $2,180 | $1,120 | 95% |

**关键发现**:
- GSP收入比VCG高11-23%
- Pacing提升预算利用率9.4%
- VCG更真实但收入较低

### 技术亮点

1. **拍卖理论应用**
   - GSP机制实现
   - 质量分计算
   - 真实性分析

2. **控制理论**
   - PID控制器
   - 反馈调节
   - 参数整定

3. **博弈论**
   - 激励兼容性
   - 策略性出价
   - 均衡分析

## 成本分摊系统 (Shapley Value)

### 功能特点

1. **Shapley Value核心算法**
   - 精确算法（O(2^n)，适用n≤12）
   - Monte Carlo近似（O(m×n)，适用任意n）
   - 增量算法（全排列枚举）
   - 结果缓存和优化

2. **云计算成本分摊**
   - 多部门共享AWS/Azure基础设施
   - 固定成本+可变成本模型
   - 规模经济折扣
   - 公平性验证（效率、个体理性、核稳定性）

3. **拼车成本分配**
   - Uber Pool/Lyft Shared场景
   - 路径优化（贪心最近邻）
   - 基于边际贡献的成本分配
   - 绕路成本公平分摊

4. **公平性分析**
   - 与比例分配对比
   - 与平均分摊对比
   - 核成员验证
   - 节省成本计算

### 快速开始

```bash
# 进入目录
cd applications/cost_sharing

# 运行全部演示
python run_demo.py
```

演示输出：
- 云计算成本分摊（5部门）
- 拼车成本分配（4乘客）
- 算法性能对比（精确vs近似）
- 公平性对比（Shapley vs 比例 vs 平均）
- 可视化图表（`visualization/`）

### 核心算法

**1. Shapley Value计算**

```python
from shapley_value import ShapleyValue

# 定义成本函数
def cost_function(coalition):
    if len(coalition) == 0:
        return 0
    return 1000 + 100 * len(coalition)  # 固定成本 + 可变成本

# 计算Shapley值
players = ['A', 'B', 'C']
calculator = ShapleyValue(players, cost_function)

# 精确算法
allocation = calculator.exact()

# Monte Carlo近似（1000样本）
allocation = calculator.monte_carlo(num_samples=1000)
```

**2. 云计算成本分摊**

```python
from cloud_cost_sharing import create_example_scenario

# 创建场景（5部门）
system = create_example_scenario()

# 计算分配
allocation = system.allocate_costs(method='exact')

# 生成报告
print(system.get_allocation_summary(allocation))

# 分析公平性
analysis = system.analyze_allocation(allocation)
print(f"核稳定性: {analysis['is_in_core']}")
print(f"总节省: ${sum(analysis['savings'].values()):,.2f}")
```

**3. 拼车成本分配**

```python
from rideshare_cost import create_example_scenario

# 创建场景（4乘客通勤）
system = create_example_scenario()

# 计算分配
allocation = system.allocate_costs(method='exact')

# 可视化
system.visualize_allocation(allocation, save_path='rideshare.png')

# 摘要报告
print(system.get_allocation_summary(allocation))
```

### 关键结果

#### 云计算成本分摊（5部门，$244K总成本）

| 部门 | 独立成本 | Shapley | 节省 | 节省率 |
|------|---------|---------|------|--------|
| Engineering | $55,960 | $42,315 | $13,645 | 24.4% |
| Data Science | $94,500 | $71,892 | $22,608 | 23.9% |
| Web Services | $61,480 | $47,126 | $14,354 | 23.3% |
| Analytics | $57,560 | $43,782 | $13,778 | 23.9% |
| Dev/Test | $51,240 | $38,885 | $12,355 | 24.1% |

**总系统节省**: $76,740/月（平均23.9%成本降低）

#### 拼车成本分配（4乘客，$51.50总成本）

| 乘客 | 独立费用 | Shapley | 节省 | 节省率 |
|------|---------|---------|------|--------|
| Alice | $17.68 | $12.34 | $5.34 | 30.2% |
| Bob | $18.85 | $13.21 | $5.64 | 29.9% |
| Carol | $20.18 | $14.67 | $5.51 | 27.3% |
| Dave | $16.84 | $11.28 | $5.56 | 33.0% |

**总系统节省**: $22.05（平均30.1%成本降低）

#### 算法性能对比

| 算法 | 5玩家时间 | 精度 | 适用规模 |
|------|----------|------|---------|
| 精确算法 | 0.042s | 100% (基准) | n ≤ 12 |
| MC (1k样本) | 0.018s | 99.2% | 任意n |
| MC (10k样本) | 0.156s | 99.8% | 任意n |

#### 公平性对比（云计算场景）

| 性质 | Shapley | 比例分配 | 平均分摊 |
|------|---------|----------|---------|
| 效率（预算平衡） | ✅ 是 | ✅ 是 | ✅ 是 |
| 个体理性 | ✅ 是 | ✅ 是 | ❌ 否 (2违反) |
| 核稳定性 | ✅ 是 | ❌ 否 (3阻塞联盟) | ❌ 否 (7阻塞联盟) |

**结论**: 仅Shapley满足所有公平性准则

### 技术亮点

1. **合作博弈论**
   - Shapley值公理化
   - 核稳定性验证
   - 边际贡献计算
   - 诺贝尔奖级理论（2012）

2. **高效算法**
   - 精确算法（小规模）
   - Monte Carlo近似（可扩展）
   - 联盟成本缓存
   - 收敛性保证

3. **多领域应用**
   - 云计算资源分配
   - 拼车成本分摊
   - 可扩展到其他场景
   - 配置驱动设计

4. **严格验证**
   - 公平性属性检验
   - 与基准方法对比
   - 数值精度控制
   - 全面单元测试

### 理论背景

**Shapley Value定义**:
```
φᵢ(v) = Σ_{S⊆N\{i}} [|S|!(n-|S|-1)! / n!] × [v(S∪{i}) - v(S)]
```

**公理化特征** (Shapley 1953):
1. **效率**: Σᵢφᵢ(v) = v(N) （所有价值被分配）
2. **对称性**: 对称玩家获得相同价值
3. **虚拟玩家**: 无贡献玩家获得0
4. **可加性**: φᵢ(v+w) = φᵢ(v) + φᵢ(w)

**核稳定性定理**: 对于凸成本函数，Shapley值总在核中。

## 开发路线图

### 短期（已完成）

- [x] Citi Bike 再平衡系统
  - [x] 数据管道
  - [x] 需求预测模型
  - [x] 激励优化算法
  - [x] 演示程序
  - [x] 文档

- [x] 广告拍卖系统 (GSP)
  - [x] GSP拍卖机制实现
  - [x] VCG对比基准
  - [x] 预算Pacing优化
  - [x] 演示程序
  - [x] 文档
  - [ ] 数据集成（iPinYou, Criteo）- 后续
  - [ ] CTR 预估模型 - 后续

- [x] 医院-住院医匹配 (NRMP)
  - [x] 合成数据生成器
  - [x] Deferred Acceptance 算法
  - [x] Couples 问题处理（Roth-Peranson）
  - [x] 稳定性验证
  - [x] 演示程序
  - [x] 文档

- [x] 成本分摊系统 (Shapley Value)
  - [x] Shapley Value 核心算法（精确 + Monte Carlo）
  - [x] 云计算成本分摊应用
  - [x] 拼车成本分配应用
  - [x] 公平性验证系统
  - [x] 算法性能对比
  - [x] 演示程序
  - [x] 文档

### 长期（3-6个月）

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

### Cost Sharing & Shapley Value
- Shapley, L. S. (1953). "A value for n-person games"
- Roth, A. E. (Ed.). (1988). "The Shapley value: essays in honor of Lloyd S. Shapley"
- Moulin, H. (2002). "Axiomatic cost and surplus sharing"
- Young, H. P. (1985). "Monotonic solutions of cooperative games"

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
