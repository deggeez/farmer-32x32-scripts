# 32x32 农田的统一调用入口；选择其中一个函数放进 main.py 调用。

from move import move_to
from hay_poly_rows32 import farm_poly_hay_row
from carrot_poly_rows32 import farm_poly_carrot_row
from tree_poly_rows32 import farm_poly_tree_row
from sunflower_rows32 import farm_sunflower_row
from pumpkin_rows32 import farm_32x32_pumpkin_forever
from cactus_sorted32 import farm_sorted_cactus_32x32
from cactus_reverse32 import grow_reverse_cactus_32x32
from maze_four_persistent import run_four_maze
from maze import get_maze_substance_cost
from dinosaur import grow_full_dinosaur
from dinosaur import farm_dinosaur_forever


def ready_for_32_drones():
	if get_world_size() != 32 or max_drones() < 32:
		quick_print("需要 32x32 农田和 32 台无人机")
		return False
	if num_drones() != 1:
		quick_print("请先停止其他无人机")
		return False
	return True


def start_32_rows(row_task, clear_first):
	if not ready_for_32_drones():
		return False
	if clear_first:
		clear()

	move_to(0, 0)
	for row in range(31):
		if spawn_drone(row_task) == None:
			quick_print("生成行无人机失败", row)
			return False
		move(North)
	row_task()


def run_hay_32(clear_first=True):
	if num_unlocked(Unlocks.Polyculture) == 0:
		quick_print("干草混种需要解锁伴生种植")
		return False
	return start_32_rows(farm_poly_hay_row, clear_first)


def run_carrot_32(clear_first=True):
	if num_unlocked(Unlocks.Carrots) == 0 or num_unlocked(Unlocks.Polyculture) == 0:
		quick_print("胡萝卜混种需要解锁胡萝卜和伴生种植")
		return False
	return start_32_rows(farm_poly_carrot_row, clear_first)


def run_sunflower_32(clear_first=True):
	if num_unlocked(Unlocks.Sunflowers) == 0:
		quick_print("尚未解锁向日葵")
		return False
	return start_32_rows(farm_sunflower_row, clear_first)


def run_wood_32(clear_first=True, wood_goal=None):
	if num_unlocked(Unlocks.Trees) == 0 or num_unlocked(Unlocks.Polyculture) == 0:
		quick_print("木材混种需要解锁树木和伴生种植")
		return False
	if not ready_for_32_drones():
		return False
	if clear_first:
		clear()

	move_to(0, 0)
	for row in range(31):
		if spawn_drone(farm_poly_tree_row, wood_goal) == None:
			quick_print("生成木材无人机失败", row)
			return False
		move(North)
	farm_poly_tree_row(wood_goal)


def run_pumpkin_32():
	if not ready_for_32_drones():
		return False
	if num_unlocked(Unlocks.Pumpkins) == 0:
		quick_print("尚未解锁南瓜")
		return False
	if num_items(Items.Carrot) < 32 * 32 * 4:
		quick_print("南瓜启动至少需要 4096 个胡萝卜")
		return False
	return farm_32x32_pumpkin_forever()


def run_cactus_32():
	if not ready_for_32_drones():
		return False
	if num_unlocked(Unlocks.Cactus) == 0:
		quick_print("尚未解锁仙人掌")
		return False
	if num_items(Items.Pumpkin) < 32 * 32 * 2:
		quick_print("仙人掌启动至少需要 2048 个南瓜")
		return False
	return farm_sorted_cactus_32x32()


def run_reverse_cactus_32_once():
	if not ready_for_32_drones():
		return False
	if num_unlocked(Unlocks.Cactus) == 0:
		quick_print("尚未解锁仙人掌")
		return False
	if num_items(Items.Pumpkin) < 32 * 32 * 2:
		quick_print("逆序仙人掌至少需要 2048 个南瓜")
		return False
	return grow_reverse_cactus_32x32()


def run_four_mazes_32():
	if not ready_for_32_drones():
		return False
	if num_unlocked(Unlocks.Mazes) == 0:
		quick_print("尚未解锁迷宫")
		return False
	cost = get_maze_substance_cost(4) * 4
	if num_items(Items.Weird_Substance) < cost:
		quick_print("四座迷宫启动至少需要诡异物质", cost)
		return False

	clear()
	if spawn_drone(run_four_maze, 4, 4) == None:
		return False
	if spawn_drone(run_four_maze, 20, 4) == None:
		return False
	if spawn_drone(run_four_maze, 4, 20) == None:
		return False
	run_four_maze(20, 20)


def run_dinosaur_32_once():
	if get_world_size() != 32 or num_drones() != 1:
		quick_print("恐龙需要 32x32 农田和仅主无人机")
		return False
	if num_unlocked(Unlocks.Dinosaurs) == 0:
		quick_print("尚未解锁恐龙")
		return False
	return grow_full_dinosaur(32)


def run_dinosaur_32_while_stocked():
	if get_world_size() != 32 or num_drones() != 1:
		quick_print("恐龙需要 32x32 农田和仅主无人机")
		return 0
	if num_unlocked(Unlocks.Dinosaurs) == 0:
		quick_print("尚未解锁恐龙")
		return 0
	return farm_dinosaur_forever(32)
