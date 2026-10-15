# 32×32 农田脚本合集

本合集提供干草、胡萝卜、木材、南瓜、仙人掌、向日葵、迷宫和恐龙的可调用入口，以及各入口用到的辅助函数。调用一个入口就会启动对应任务；不需要再手工编写 31 次 `spawn_drone()`。**一次只运行一种模式**，因为大部分入口会持续循环，而且不能与已经运行的无人机共用 32 个名额。

## 安装与调用

将本目录**顶层的所有 `.py` 文件**复制到游戏脚本目录，与游戏的 `main.py` 放在同一级。

之后在游戏的 `main.py` 中只保留一种调用，例如干草：

```python
from entrypoints import run_hay_32

run_hay_32()
```

要换模式，只需把导入和调用都换为下表的一项。不要在后面继续调用其他无限循环入口。

| 模式 | `main.py` 中的导入与调用 | 无人机 | 结果 |
| --- | --- | ---: | --- |
| 干草 | `from entrypoints import run_hay_32` → `run_hay_32()` | 32 | 每行一机，持续向东环绕收干草，使用伴生种植 |
| 胡萝卜 | `from entrypoints import run_carrot_32` → `run_carrot_32()` | 32 | 每行一机，伴生种植并给胡萝卜浇水 |
| 木材 | `from entrypoints import run_wood_32` → `run_wood_32()` | 32 | 每行一机，树木棋盘间隔种植、伴生种植并浇水 |
| 南瓜 | `from entrypoints import run_pumpkin_32` → `run_pumpkin_32()` | 32 | 32 行都确认成熟后，整片收获并循环重种 |
| 仙人掌 | `from entrypoints import run_cactus_32` → `run_cactus_32()` | 32 | 各行先排序，再各列排序，整片收获并循环 |
| 向日葵 | `from entrypoints import run_sunflower_32` → `run_sunflower_32()` | 32 | 每行一机，浇水，成熟就收；不按花瓣数排序 |
| 迷宫 | `from entrypoints import run_four_mazes_32` → `run_four_mazes_32()` | 32 | 四座 4×4 迷宫，每座 8 机驻守并循环复用 |
| 恐龙 | `from entrypoints import run_dinosaur_32_once` → `run_dinosaur_32_once()` | 1 | 跑一轮 32×32 恐龙路线，摘帽结算骨头 |

所有入口都要求世界大小为 32×32，并且开始时只有主无人机在运行。前七种模式要求已解锁 32 台无人机。若入口检查到条件不足，会打印原因并返回，不会先清空农田。逐行模式没有预检整片田地的种植库存；运行中的脚本仍可能因资源耗尽而停止或等待，入口检查不能替代持续供应资源。

## 参数、资源与清田行为

- `run_hay_32(clear_first=True)`：默认先 `clear()`，再启动 32 行。要求已解锁伴生种植。传 `False` 可保留现有田地，但如果地上还有迷宫墙或其他难以清除的实体，可能影响种植。
- `run_carrot_32(clear_first=True)`：默认清田。要求胡萝卜和伴生种植已解锁；需要有胡萝卜种植资源。胡萝卜格水分低于 0.5 时尝试使用 `Items.Water`。
- `run_wood_32(clear_first=True, wood_goal=None)`：默认清田。要求树木和伴生种植已解锁；需要树木种植资源，树木格水分低于 0.5 时尝试浇水。设置 `wood_goal` 后，各行会在木材达到该数值且回到行首时结束，例如 `run_wood_32(True, 10000000000)`。不设置则持续运行。这不是排行榜自动提交入口。
- `run_sunflower_32(clear_first=True)`：默认清田。要求已解锁向日葵、拥有种植资源；水分低于 0.5 时尝试浇水。此版只求逐行连续收获，不保证花瓣排序收益。
- `run_pumpkin_32()`：启动前要求已解锁南瓜，且至少有 `4096` 个胡萝卜供 1024 格首次种植；随后由原南瓜函数清田、分行养护和收获。它会尝试浇水，但水耗尽后仍会自然生长。后续循环还需要持续的胡萝卜供应。
- `run_cactus_32()`：启动前要求已解锁仙人掌，且至少有 `2048` 个南瓜供 1024 格首次种植；随后由原仙人掌函数清田、排序和收获。后续循环还需要持续的南瓜供应。
- `run_four_mazes_32()`：要求已解锁迷宫，启动时至少有四座迷宫各一次生成所需的 `Items.Weird_Substance`，然后清田。四座迷宫左下角分别在 `(4,4)`、`(20,4)`、`(4,20)`、`(20,20)`。`get_maze_substance_cost(4)` 会根据迷宫等级计算**每座**单次用量。后续复用也要奇异物质；不足时驻守无人机会等待补给，生成失败不会再打印“生成成功”。
- `run_dinosaur_32_once()`：要求已解锁恐龙，且只运行主无人机。内部用 `full_dinosaur_cost(32)` 检查整轮苹果成本；资源够时清田、戴帽、走路线、摘帽结算骨头，返回 `True`。资源不足返回 `False`，不清田。恐龙模式不需要 32 台无人机。
- `run_dinosaur_32_while_stocked()`：资源够就重复完整的恐龙轮次；不足时返回已完成轮数，**不会等待补货**。可以用它替换上表的一次性恐龙入口。
- `run_reverse_cactus_32_once()`：额外的一次性逆序仙人掌入口，使用 `cactus_reverse32.py`；同样要求 32 台无人机和至少 `2048` 个南瓜，会清田、逆序排列 32×32 后收获一次。日常循环请使用 `run_cactus_32()`。

上面的 `clear_first` 仅适用于四种逐行作物。默认清田是为了让每个模式能从未知的旧田地直接启动；若现有作物不想被清除，明确传 `False`。南瓜、仙人掌、迷宫和恐龙的清田属于其算法的一部分，不能用这个参数关闭。

## 文件与验证

`entrypoints.py` 负责参数检查和无人机分配。`hay_poly_rows32.py`、`carrot_poly_rows32.py`、`tree_poly_rows32.py`、`sunflower_rows32.py` 包含各行自己的辅助函数。`pumpkin_rows32.py`、`cactus_sorted32.py`、`cactus_reverse32.py`、`maze_four_persistent.py`、`dinosaur.py` 是其余模式的实现；`move.py`、`rectangle_and_route.py`、`growth_options.py`、`pumpkin.py`、`cactus.py`、`maze.py` 是这些实现的依赖。


