# 无政府代价 (Price of Anarchy)

## 动机

纳什均衡是自私玩家的稳定状态，但不一定是社会最优的。

**核心问题**：自私行为导致的效率损失有多大？

## 数学定义

### 社会福利 (Social Welfare)

给定策略组合 $s = (s_1, \ldots, s_n)$，**社会福利** 定义为所有玩家效用之和：

$$SW(s) = \sum_{i=1}^{n} u_i(s)$$

### 社会最优 (Social Optimum)

**社会最优** 是使社会福利最大化的策略组合：

$$OPT = \max_{s \in S} SW(s)$$

### 无政府代价 (Price of Anarchy)

**定义（Koutsoupias & Papadimitriou, 1999）**：

$$\text{PoA} = \frac{OPT}{\min_{s \in NE} SW(s)}$$

其中 $NE$ 是所有纳什均衡的集合。

**解释**：
- PoA 衡量最坏纳什均衡相对于社会最优的效率损失
- $\text{PoA} \geq 1$（定义保证）
- PoA = 1：所有纳什均衡都是社会最优（无损失）
- PoA 越大，效率损失越严重

### 稳定代价 (Price of Stability)

$$\text{PoS} = \frac{OPT}{\max_{s \in NE} SW(s)}$$

**解释**：
- PoS 衡量最好纳什均衡的效率
- $1 \leq \text{PoS} \leq \text{PoA}$
- PoS = 1：存在社会最优的纳什均衡
- PoS 衡量通过协调能达到的最好效率

## 经典例子

### 1. 囚徒困境

|       | C     | D     |
|-------|-------|-------|
| **C** | -1,-1 | -3,0  |
| **D** | 0,-3  | -2,-2 |

**计算**：
- $SW(C, C) = -2$（最优）
- $SW(D, D) = -4$（纳什均衡）
- $\text{PoA} = \frac{|-2|}{|-4|} = \frac{4}{2} = 2$

**结论**：纳什均衡的效率只有最优的 50%

### 2. 协调博弈

|       | A     | B     |
|-------|-------|-------|
| **A** | 10,10 | 0,0   |
| **B** | 0,0   | 5,5   |

**计算**：
- $SW(A, A) = 20$（最优且是纳什均衡）
- $SW(B, B) = 10$（次优纳什均衡）
- $\text{PoA} = \frac{20}{10} = 2$
- $\text{PoS} = \frac{20}{20} = 1$

**结论**：
- PoS = 1：存在最优均衡
- PoA = 2：但玩家可能协调失败

### 3. Pigou 网络

经典的网络拥塞例子：

```
      x → [cost: x]
s ─────────────────→ t
      ↓ [cost: 1]
```

- 1单位流量从 s 到 t
- 上路：成本 = 流量 x
- 下路：成本 = 1（常数）

**自私路由（纳什均衡）**：
- 所有流量走下路
- 总成本 = 1

**社会最优**：
- 流量分配使总成本最小
- 这里还是全走下路
- 总成本 = 1

**结论**：$\text{PoA} = 1$（这个例子中）

**更一般的 Pigou 网络**：

```
      x² → [cost: x²]
s ─────────────────→ t
      ↓ [cost: 1]
```

**自私路由**：
- 全走下路，成本 = 1

**社会最优**：
- 分析显示最优分配的成本 < 1

**结论**：$\text{PoA} = \frac{4}{3}$（可以证明）

## Braess 悖论

**现象**：在网络中增加边可能增加所有人的成本！

**例子**：

原网络：
```
    ─→ [x] ─→
s ──           ── t
    ─→ [x] ─→
```

加边后：
```
    ─→ [x] ─→
s ──   ↓     ── t
    ─→ [x] ─→
    (加一条0成本的边)
```

**结果**：纳什均衡的总成本增加了！

**原因**：
- 自私路由选择新的捷径
- 但导致拥塞，反而更差
- 这说明纳什均衡可能不是帕累托有效

## PoA 的界

### 一般结果

**定理（Roughgarden, 2002）**：对于多项式延迟函数的网络：

$$\text{PoA} \leq \rho(d)$$

其中 $\rho(d)$ 只依赖于延迟函数的最高次数 $d$。

**具体界**：
- 线性延迟：$\text{PoA} \leq \frac{4}{3}$
- 二次延迟：$\text{PoA} \leq \frac{5}{2}$
- 一般 $d$ 次：$\text{PoA} = \Theta(\frac{d}{\ln d})$

### 拥塞博弈

**定理**：在拥塞博弈中：

$$\text{PoS} \leq H_n = 1 + \frac{1}{2} + \cdots + \frac{1}{n}$$

其中 $n$ 是玩家数量。

## PoA 的计算

### 困难性

**问题**：给定博弈，计算 PoA

**结果**：
- 找出所有纳什均衡可能很难（PPAD-complete）
- 但对于某些博弈类，可以分析性地给出 PoA 的界

### 方法论

**平滑分析** (Smoothness Framework)：

Roughgarden (2009) 提出的统一框架：

如果博弈满足 $(\lambda, \mu)$-平滑性：

$$\sum_{i} u_i(s_i^*, s_{-i}) \geq \lambda \cdot OPT - \mu \cdot SW(s)$$

对所有 $s$ 和社会最优 $s^*$，则：

$$\text{PoA} \leq \frac{\lambda}{1 - \mu}$$

**优点**：
- 统一了很多博弈类的 PoA 分析
- 证明技巧可复用
- 可以扩展到混合策略、相关均衡等

## 应用

### 1. 网络设计

**问题**：如何设计网络基础设施以减少自私路由的成本？

**Stackelberg 路由**：
- 中心化控制部分流量
- 引导自私流量走更好的路

**结果**：控制 $\alpha$ 比例的流量可以使 $\text{PoA} \leq f(\alpha)$

### 2. 拥塞定价

**思想**：对拥塞的资源收费，使自私行为与社会最优一致

**机制**：边际成本定价 (Marginal Cost Pricing)

**结果**：在某些网络中可以使 $\text{PoA} = 1$

### 3. 算法机制设计

**目标**：设计机制使：
- 真实报告是占优策略（激励相容）
- 纳什均衡近似社会最优（PoA 小）

## 变体与扩展

### 1. 强 PoA (Strong Price of Anarchy)

考虑强纳什均衡（coalition-proof）：

$$\text{Strong PoA} = \frac{OPT}{\min_{s \in SNE} SW(s)}$$

### 2. 贝叶斯 PoA

不完全信息博弈中的期望效率损失。

### 3. 动态 PoA

随时间变化的博弈中的效率损失。

## PoA vs PoS

| 指标 | 衡量内容 | 应用场景 |
|------|----------|----------|
| PoA  | 最坏情况效率损失 | 没有协调时的保证 |
| PoS  | 最好均衡的效率 | 可以协调选择均衡时 |

**实践意义**：
- PoA：下界保证（worst-case）
- PoS：协调目标（best-case among equilibria）

## 批评与局限

1. **均衡选择**：PoA 假设玩家会选择最坏的均衡（悲观）
2. **静态分析**：不考虑收敛过程
3. **完美理性**：假设玩家完全理性
4. **社会福利定义**：求和可能不是唯一合理的社会目标

## 参考文献

1. **Koutsoupias, E., & Papadimitriou, C. (1999).** "Worst-case equilibria." *STACS*, 404-413.
2. **Roughgarden, T., & Tardos, É. (2002).** "How bad is selfish routing?" *Journal of the ACM*, 49(2), 236-259.
3. **Roughgarden, T. (2009).** "Intrinsic robustness of the price of anarchy." *STOC*, 513-522.
4. **Roughgarden, T. (2016).** *Twenty Lectures on Algorithmic Game Theory*, Lectures 12-14.

## 相关练习

- `efficiency01_price_of_anarchy.py` - 计算 PoA 和 PoS
- `routing01_selfish_routing.py` - 网络路由中的 PoA（即将添加）
