# 快速开始指南 | Quick Start Guide

## 中文

### 5分钟上手

1. **安装依赖**
   ```bash
   cd algo_game_theory_tool
   pip install -r requirements.txt
   ```

2. **查看所有练习**
   ```bash
   python algo_game_theory.py list
   ```

3. **完成第一个练习**

   打开 `exercises/01_intro/intro01_strategic_game.py`，找到 `TODO` 标记：

   ```python
   def __init__(self, player1_strategies, player2_strategies, payoff_matrix):
       # TODO: 实现初始化逻辑
       pass
   ```

   实现代码：

   ```python
   def __init__(self, player1_strategies, player2_strategies, payoff_matrix):
       self.player1_strategies = player1_strategies
       self.player2_strategies = player2_strategies
       self.payoff_matrix = payoff_matrix
   ```

4. **运行测试**
   ```bash
   python algo_game_theory.py run intro01_strategic_game
   ```

5. **继续学习**

   完成一个练习后，继续下一个：
   ```bash
   python algo_game_theory.py watch
   ```

### 完整示例：实现第一个练习

**文件**: `exercises/01_intro/intro01_strategic_game.py`

```python
class StrategicGame:
    def __init__(self, player1_strategies, player2_strategies, payoff_matrix):
        self.player1_strategies = player1_strategies
        self.player2_strategies = player2_strategies
        self.payoff_matrix = payoff_matrix

    def get_payoff(self, strategy1, strategy2):
        return self.payoff_matrix[(strategy1, strategy2)]

    def get_player1_strategies(self):
        return self.player1_strategies

    def get_player2_strategies(self):
        return self.player2_strategies
```

保存后运行：
```bash
python algo_game_theory.py run 1
```

输出：
```
✓ 恭喜！练习完成！
```

### 学习路径建议

#### 初学者（第1-3周）
1. 完成基础概念练习（第一章）
2. 理解纳什均衡（第二章）
3. 学习混合策略（第三章）

#### 进阶（第4-6周）
4. 深入拍卖理论（第四章）
5. 掌握机制设计（第五章）

---

## English

### 5-Minute Quickstart

1. **Install dependencies**
   ```bash
   cd algo_game_theory_tool
   pip install -r requirements.txt
   ```

2. **List all exercises**
   ```bash
   python algo_game_theory.py list
   ```

3. **Complete the first exercise**

   Open `exercises/01_intro/intro01_strategic_game.py` and find the `TODO`:

   ```python
   def __init__(self, player1_strategies, player2_strategies, payoff_matrix):
       # TODO: Implement initialization logic
       pass
   ```

   Implement:

   ```python
   def __init__(self, player1_strategies, player2_strategies, payoff_matrix):
       self.player1_strategies = player1_strategies
       self.player2_strategies = player2_strategies
       self.payoff_matrix = payoff_matrix
   ```

4. **Run tests**
   ```bash
   python algo_game_theory.py run intro01_strategic_game
   ```

5. **Continue learning**
   ```bash
   python algo_game_theory.py watch
   ```

### Learning Path

#### Beginners (Weeks 1-3)
1. Complete fundamental concepts (Chapter 1)
2. Understand Nash equilibrium (Chapter 2)
3. Learn mixed strategies (Chapter 3)

#### Advanced (Weeks 4-6)
4. Study auction theory (Chapter 4)
5. Master mechanism design (Chapter 5)
