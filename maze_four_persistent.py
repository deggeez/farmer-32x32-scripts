from move import move_to
from maze import get_maze_substance_cost
from maze import generate_maze


SIZE = 4


def reverse_direction(direction):
	if direction == North:
		return South
	if direction == South:
		return North
	if direction == East:
		return West
	return East


def adjacent_direction(home_x, home_y, target_x, target_y):
	if target_x == home_x and target_y == home_y + 1:
		return North
	if target_x == home_x and target_y == home_y - 1:
		return South
	if target_y == home_y and target_x == home_x + 1:
		return East
	if target_y == home_y and target_x == home_x - 1:
		return West
	return None


def recycle_or_harvest(x, y, cost):
	# 相邻无人机可能同时到达。竞争失败不能立即当作复用已达上限。
	for attempt in range(3):
		if use_item(Items.Weird_Substance, cost):
			return
		for unused in range(205):
			pass
		if get_entity_type() != Entities.Treasure:
			return
	if harvest():
		quick_print("maze harvested", x, y, "time", get_time(), "gold", num_items(Items.Gold))


def watch_checker_tile(x, y, cost):
	home_x = get_pos_x()
	home_y = get_pos_y()
	while True:
		entity = get_entity_type()
		if entity == Entities.Treasure:
			recycle_or_harvest(x, y, cost)
			continue
		if entity != Entities.Hedge:
			continue
		target = measure()
		if target == None:
			continue
		direction = adjacent_direction(home_x, home_y, target[0], target[1])
		if direction == None:
			continue
		if not can_move(direction):
			continue
		if move(direction):
			if get_entity_type() == Entities.Treasure:
				recycle_or_harvest(x, y, cost)
			move(reverse_direction(direction))


def run_four_maze(x, y):
	cost = get_maze_substance_cost(SIZE)
	seed_x = x + 2
	seed_y = y + 2
	# 先在空地放好另外七台，之后不再回收或重新生成无人机。
	move_to(seed_x, seed_y)
	for row in range(SIZE):
		for column in range(SIZE):
			if (column + row) % 2 == 0:
				tile_x = x + column
				tile_y = y + row
				if tile_x != seed_x or tile_y != seed_y:
					move_to(tile_x, tile_y)
					spawn_drone(watch_checker_tile, x, y, cost)
	move_to(seed_x, seed_y)
	quick_print("maze workers ready", x, y, num_drones())
	while True:
		entity = get_entity_type()
		if entity != Entities.Hedge and entity != Entities.Treasure:
			# 收获后让出格子的无人机先走回驻守位，再生成新墙。
			for unused in range(650):
				pass
			if num_items(Items.Weird_Substance) < cost:
				do_a_flip()
				continue
			if generate_maze(x, y, SIZE):
				quick_print("maze generated", x, y, "time", get_time(), "gold", num_items(Items.Gold))
			continue
		if entity == Entities.Treasure:
			recycle_or_harvest(x, y, cost)
			continue
		target = measure()
		if target == None:
			continue
		direction = adjacent_direction(seed_x, seed_y, target[0], target[1])
		if direction == None:
			continue
		if not can_move(direction):
			continue
		if move(direction):
			if get_entity_type() == Entities.Treasure:
				recycle_or_harvest(x, y, cost)
			move(reverse_direction(direction))
			
