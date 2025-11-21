# 算法博弈论数学背景文档索引

本目录包含所有练习题的数学背景文档，帮助你深入理解算法博弈论的理论基础。

## 📚 文档结构

### 第一章：基础概念
- [策略式博弈 (Strategic Form Games)](01_intro/strategic_game.md)
- [占优策略与严格劣策略 (Dominant Strategies)](01_intro/dominant_strategy.md)

### 第二章：纳什均衡
- [纳什均衡 (Nash Equilibrium)](02_nash_equilibrium/nash_equilibrium.md)

### 第六章：效率与社会福利
- [无政府代价 (Price of Anarchy)](06_efficiency/price_of_anarchy.md)

## 📖 使用建议

### 学习流程

1. **先读文档，再做练习**
   - 阅读对应的数学背景文档
   - 理解核心概念和定理
   - 查看例子和应用

2. **文档内容**
   - 📐 **数学定义**：严格的形式化定义
   - 📊 **经典例子**：具体案例分析
   - 🔍 **性质与定理**：重要理论结果
   - 💡 **应用场景**：实际应用
   - 📚 **参考文献**：深入学习资源

3. **结合练习**
   - 每个文档末尾列出相关练习
   - 做练习时可以回顾文档
   - 利用文档中的提示和公式

### 推荐阅读顺序

#### 初学者路径（1-3周）

1. **基础概念** (Week 1)
   - 策略式博弈
   - 占优策略
   - 帕累托效率

2. **纳什均衡** (Week 2)
   - 纳什均衡基础
   - 纯策略与混合策略
   - IESDS

3. **混合策略** (Week 3)
   - 期望效用
   - 混合策略纳什均衡

#### 进阶路径（4-6周）

4. **拍卖理论** (Week 4)
   - 第二价格拍卖
   - 收入等价定理

5. **机制设计** (Week 5)
   - VCG 机制
   - 激励相容性

6. **效率分析** (Week 6)
   - 无政府代价
   - 社会福利最大化

#### 高级路径（7-9周）

7. **协同博弈** (Week 7)
   - 夏普利值
   - 公平分配

8. **匹配理论** (Week 8)
   - 稳定匹配
   - Gale-Shapley 算法

9. **势博弈** (Week 9)
   - 势函数
   - 收敛性分析

## 📐 数学符号约定

| 符号 | 含义 |
|------|------|
| $N$ | 玩家集合 |
| $S_i$ | 玩家 $i$ 的策略集 |
| $s_i$ | 玩家 $i$ 的策略 |
| $s$ | 策略组合 (strategy profile) |
| $s_{-i}$ | 除 $i$ 外其他玩家的策略 |
| $u_i(s)$ | 玩家 $i$ 在策略 $s$ 下的效用 |
| $BR_i(s_{-i})$ | 玩家 $i$ 对 $s_{-i}$ 的最佳响应 |
| $NE$ | 纳什均衡集合 |
| $SW(s)$ | 社会福利 (Social Welfare) |
| $\sigma_i$ | 玩家 $i$ 的混合策略 |
| $v(S)$ | 联盟 $S$ 的特征函数值 |
| $\phi_i$ | 玩家 $i$ 的夏普利值 |

## 🎓 学习资源

### 主要教材

1. **Tim Roughgarden - Twenty Lectures on Algorithmic Game Theory**
   - 本工具的主要参考来源
   - 涵盖算法博弈论核心主题
   - [PDF 链接](https://theory.stanford.edu/~tim/papers/agtalgs.pdf)

2. **Nisan, Roughgarden, Tardos, Vazirani - Algorithmic Game Theory**
   - 权威的算法博弈论教材
   - 各章节由领域专家撰写

3. **Osborne & Rubinstein - A Course in Game Theory**
   - 经典博弈论教材
   - 数学严谨，适合深入学习

### 在线课程

- [Stanford CS364A: Algorithmic Game Theory](http://timroughgarden.org/f13/f13.html)
- [Cornell CS6840: Algorithmic Game Theory](https://www.cs.cornell.edu/courses/cs6840/)

### 视频资源

- [Tim Roughgarden's YouTube Channel](https://www.youtube.com/channel/UCcH4Ga14Y4ELFKrEYM1vXCg)
- Coursera: Game Theory (Stanford, Yale)

## 💻 使用建议

### 如何阅读数学文档

1. **不要跳过定义**：每个定义都很重要
2. **手工验证例子**：自己计算一遍例子
3. **尝试证明定理**：至少理解证明思路
4. **联系实际应用**：思考现实世界的例子

### 遇到困难怎么办

1. **重读基础文档**：确保理解前置知识
2. **查看练习提示**：代码中的 HINT 注释
3. **参考教材**：查阅推荐的教材和论文
4. **画图理解**：用图表可视化概念
5. **讨论交流**：与他人讨论问题

## 📝 贡献文档

欢迎贡献新的数学背景文档！

**贡献指南**：
1. 使用 Markdown 格式
2. 包含数学定义、例子、性质、应用
3. 添加参考文献
4. 链接到相关练习
5. 使用 LaTeX 数学公式

## 📄 许可证

所有文档基于 MIT License 发布。
