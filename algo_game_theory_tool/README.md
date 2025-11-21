# 算法博弈论学习工具 🎮📚

> 类似 Rustlings 的交互式算法博弈论学习工具
>
> 基于 **Tim Roughgarden 教授的《算法博弈论二十讲》**

[English](#english) | [中文](#chinese)

---

## 中文 <a name="chinese"></a>

### 简介

这是一个交互式的算法博弈论学习工具，灵感来自 Rustlings。通过完成一系列精心设计的练习题，你将逐步掌握算法博弈论的核心概念。

**主要特点：**
- 📖 基于 Tim Roughgarden 教授的经典课程
- ✅ 自动测试和即时反馈
- 🎯 从基础到高级的渐进式学习路径
- 💡 内置提示系统帮助理解
- 📊 进度跟踪，记录学习历程

### 学习内容

#### 第一章：基础概念
- `intro01_strategic_game` - 策略式博弈的基本表示
- `intro02_dominant_strategy` - 占优策略与严格劣策略
- `intro03_pareto_efficiency` - 帕累托效率与社会最优

#### 第二章：纳什均衡
- `nash01_pure_nash` - 纯策略纳什均衡的计算
- `nash02_iterative_elimination` - 重复剔除严格劣策略 (IESDS)

#### 第三章：混合策略
- `mixed01_expected_utility` - 混合策略与期望效用
- `mixed02_support_nash` - 混合策略纳什均衡的支撑集

#### 第四章：拍卖理论
- `auction01_second_price` - 第二价格拍卖（维克里拍卖）
- `auction02_revenue_equivalence` - 收入等价定理

#### 第五章：机制设计
- `mechanism01_vcg` - VCG 机制（Vickrey-Clarke-Groves）

#### 第六章：效率与社会福利
- `efficiency01_price_of_anarchy` - 无政府代价（Price of Anarchy）与稳定代价

#### 第七章：协同博弈
- `coop01_shapley_value` - 夏普利值（Shapley Value）与公平分配

#### 第八章：匹配理论
- `matching01_stable_matching` - 稳定匹配与 Gale-Shapley 算法

#### 第九章：势博弈
- `potential01_potential_function` - 势函数与最佳响应动态

### 安装

```bash
# 克隆仓库
git clone https://github.com/GeoffreyWang1117/Algorithm-Game-Theory.git
cd Algorithm-Game-Theory/algo_game_theory_tool

# 安装依赖
pip install -r requirements.txt
```

### 使用方法

#### 1. 列出所有练习

```bash
python algo_game_theory.py list
```

这会显示所有可用的练习题和你的完成进度。

#### 2. 运行特定练习

```bash
# 通过名称运行
python algo_game_theory.py run intro01_strategic_game

# 或通过序号运行
python algo_game_theory.py run 1
```

#### 3. 监视模式（推荐）

```bash
python algo_game_theory.py watch
```

监视模式会自动运行下一个未完成的练习，完成后再运行下一个，帮助你系统地学习。

#### 4. 获取提示

```bash
python algo_game_theory.py hint intro02_dominant_strategy
```

如果遇到困难，使用 hint 命令获取额外的提示。

#### 5. 重置进度

```bash
python algo_game_theory.py reset
```

重新开始学习之旅。

### 学习流程

1. **阅读练习说明**：每个练习文件开头都有详细的理论说明
2. **完成 TODO**：找到代码中的 `# TODO` 标记，实现对应功能
3. **运行测试**：使用 `python algo_game_theory.py run <练习名>` 测试你的代码
4. **查看提示**：如果卡住了，使用 `hint` 命令获取帮助
5. **理解反馈**：测试会给出详细的错误信息，帮助你定位问题
6. **继续前进**：完成后自动记录进度，继续下一个练习

### 示例

```bash
$ python algo_game_theory.py list

算法博弈论练习题列表

基于 Tim Roughgarden 教授的《算法博弈论二十讲》

第一章：基础概念
  ✓  1. intro01_strategic_game
  ○  2. intro02_dominant_strategy
  ○  3. intro03_pareto_efficiency

...

进度: 1/10 (10.0%)

$ python algo_game_theory.py run 2

运行练习: 01_intro/intro02_dominant_strategy

练习说明:
占优策略是博弈论中的核心概念...

测试 1: 囚徒困境 - 玩家1的占优策略
  ✓ 玩家1的占优策略: D
  ✓ 玩家2的占优策略: D

...

✓ 恭喜！练习完成！
```

### 学习建议

1. **按顺序学习**：练习题是精心排序的，建议按顺序完成
2. **理论与实践结合**：先阅读练习开头的理论说明，理解概念后再编码
3. **不要跳过练习**：每个练习都是后续内容的基础
4. **利用提示**：HINT 注释提供了实现思路，合理利用
5. **对比测试用例**：测试用例展示了预期行为，是很好的学习材料
6. **配合教材**：建议配合 Tim Roughgarden 的课程或教材学习

### 参考资料

- 📚 [Tim Roughgarden's Twenty Lectures on Algorithmic Game Theory](https://theory.stanford.edu/~tim/papers/agtalgs.pdf)
- 📖 Algorithmic Game Theory (Nisan, Roughgarden, Tardos, Vazirani)
- 🎓 [Stanford CS364A: Algorithmic Game Theory](http://timroughgarden.org/f13/f13.html)

### 贡献

欢迎贡献新的练习题或改进现有练习！请提交 Pull Request。

### 许可证

MIT License

---

## English <a name="english"></a>

### Introduction

An interactive learning tool for Algorithmic Game Theory, inspired by Rustlings. Master the core concepts of algorithmic game theory through a series of carefully designed exercises.

**Key Features:**
- 📖 Based on Professor Tim Roughgarden's classic lectures
- ✅ Automatic testing with instant feedback
- 🎯 Progressive learning path from basics to advanced topics
- 💡 Built-in hint system for better understanding
- 📊 Progress tracking for your learning journey

### Topics Covered

#### Chapter 1: Fundamentals
- `intro01_strategic_game` - Basic representation of strategic games
- `intro02_dominant_strategy` - Dominant strategies and strictly dominated strategies
- `intro03_pareto_efficiency` - Pareto efficiency and social optimality

#### Chapter 2: Nash Equilibrium
- `nash01_pure_nash` - Computing pure strategy Nash equilibria
- `nash02_iterative_elimination` - Iterated elimination of strictly dominated strategies

#### Chapter 3: Mixed Strategies
- `mixed01_expected_utility` - Mixed strategies and expected utility
- `mixed02_support_nash` - Support of mixed strategy Nash equilibria

#### Chapter 4: Auction Theory
- `auction01_second_price` - Second-price auctions (Vickrey auctions)
- `auction02_revenue_equivalence` - Revenue equivalence theorem

#### Chapter 5: Mechanism Design
- `mechanism01_vcg` - VCG Mechanism (Vickrey-Clarke-Groves)

#### Chapter 6: Efficiency and Social Welfare
- `efficiency01_price_of_anarchy` - Price of Anarchy and Price of Stability

#### Chapter 7: Cooperative Games
- `coop01_shapley_value` - Shapley Value and Fair Allocation

#### Chapter 8: Matching Theory
- `matching01_stable_matching` - Stable Matching and Gale-Shapley Algorithm

#### Chapter 9: Potential Games
- `potential01_potential_function` - Potential Functions and Best Response Dynamics

### Installation

```bash
# Clone the repository
git clone https://github.com/GeoffreyWang1117/Algorithm-Game-Theory.git
cd Algorithm-Game-Theory/algo_game_theory_tool

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### 1. List all exercises

```bash
python algo_game_theory.py list
```

#### 2. Run a specific exercise

```bash
# By name
python algo_game_theory.py run intro01_strategic_game

# Or by number
python algo_game_theory.py run 1
```

#### 3. Watch mode (recommended)

```bash
python algo_game_theory.py watch
```

Watch mode automatically runs the next incomplete exercise.

#### 4. Get hints

```bash
python algo_game_theory.py hint intro02_dominant_strategy
```

#### 5. Reset progress

```bash
python algo_game_theory.py reset
```

### Learning Flow

1. **Read the exercise description** at the top of each file
2. **Complete the TODOs** in the code
3. **Run tests** using `python algo_game_theory.py run <exercise>`
4. **Check hints** if you get stuck
5. **Understand feedback** from test results
6. **Move forward** to the next exercise

### References

- 📚 [Tim Roughgarden's Twenty Lectures on Algorithmic Game Theory](https://theory.stanford.edu/~tim/papers/agtalgs.pdf)
- 📖 Algorithmic Game Theory (Nisan, Roughgarden, Tardos, Vazirani)
- 🎓 [Stanford CS364A: Algorithmic Game Theory](http://timroughgarden.org/f13/f13.html)

### Contributing

Contributions of new exercises or improvements are welcome! Please submit a Pull Request.

### License

MIT License
