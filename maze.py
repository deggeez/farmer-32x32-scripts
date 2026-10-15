from move import move_to
from rectangle_and_route import rectangle_in_bounds


def can_afford_unlock_with_cactus_reserve(cost, cactus_reserve):
	for item in cost:
		reserve = 0

		if item == Items.Cactus:
			reserve = cactus_reserve

		if num_items(item) < cost[item] + reserve:
			return False

	return True


def upgrade_maze_to_highest(cactus_reserve):
	while True:
		cost = get_cost(Unlocks.Mazes)

		# 不同游戏版本在满级时可能返回None或空字典。
		if cost == None:
			return True

		if len(cost) == 0:
			return True

		if not can_afford_unlock_with_cactus_reserve(
			cost,
			cactus_reserve
		):
			return False

		if not unlock(Unlocks.Mazes):
			return False


def get_maze_substance_cost(n):
	level = num_unlocked(Unlocks.Mazes)
	multiplier = 1

	for unused in range(level - 1):
		multiplier *= 2

	return n * multiplier


def maze_seed_position(x, y, n):
	# 迷宫以灌木为中心生成。
	# 偶数边长使用右上侧的中心格。
	return [x + n // 2, y + n // 2]


def generate_maze(x, y, n):
	if not rectangle_in_bounds(x, y, n, n):
		quick_print("迷宫区域越界", x, y, n)
		return False

	if num_unlocked(Unlocks.Mazes) <= 0:
		quick_print("尚未解锁迷宫")
		return False

	seed = maze_seed_position(x, y, n)
	move_to(seed[0], seed[1])

	entity = get_entity_type()

	if entity == Entities.Hedge or entity == Entities.Treasure:
		return True

	# 草地上的Grass实体会自动存在，收割后仍然不会变成None。
	# 这种情况必须直接翻土，否则函数会在till()之前反复返回。
	if (
		get_ground_type() != Grounds.Soil
		and entity == Entities.Grass
	):
		till()
	else:
		# 其他实体先清除。harvest()也能清除尚未成熟的普通植物。
		if entity != None:
			harvest()

			if get_entity_type() != None:
				quick_print(
					"迷宫中心存在无法清除的实体",
					get_entity_type()
				)
				return False

		if get_ground_type() != Grounds.Soil:
			till()

	if get_ground_type() != Grounds.Soil:
		quick_print("迷宫中心翻土失败", seed)
		return False

	if get_entity_type() != None:
		quick_print(
			"翻土后迷宫中心仍有实体",
			get_entity_type()
		)
		return False

	if not plant(Entities.Bush):
		quick_print("迷宫中心种植灌木失败", seed)
		return False

	if get_entity_type() != Entities.Bush:
		quick_print(
			"种植后灌木被替换",
			get_entity_type()
		)
		return False

	cost = get_maze_substance_cost(n)

	if num_items(Items.Weird_Substance) < cost:
		quick_print(
			"生成迷宫所需诡异物质不足",
			num_items(Items.Weird_Substance),
			"/",
			cost
		)
		return False

	if not use_item(Items.Weird_Substance, cost):
		quick_print("对灌木使用诡异物质失败")
		return False

	success = (
		get_entity_type() == Entities.Hedge
		or get_entity_type() == Entities.Treasure
	)

	if not success:
		quick_print(
			"使用诡异物质后未生成迷宫",
			get_entity_type()
		)

	return success


def search_maze_tile(x, y, n, visited):
	if get_entity_type() == Entities.Treasure:
		return True

	current = [get_pos_x(), get_pos_y()]
	visited.append(current)

	directions = [North, East, South, West]
	opposites = [South, West, North, East]
	delta_x = [0, 1, 0, -1]
	delta_y = [1, 0, -1, 0]
	direction_order = []
	target = measure()

	# measure()可以直接得到宝藏坐标。
	# DFS优先探索朝向宝藏的两个方向，再尝试其余方向。
	if target != None:
		difference_x = target[0] - current[0]
		difference_y = target[1] - current[1]

		x_direction = None
		y_direction = None

		if difference_x > 0:
			x_direction = 1
		elif difference_x < 0:
			x_direction = 3

		if difference_y > 0:
			y_direction = 0
		elif difference_y < 0:
			y_direction = 2

		if abs(difference_x) >= abs(difference_y):
			if x_direction != None:
				direction_order.append(x_direction)
			if y_direction != None:
				direction_order.append(y_direction)
		else:
			if y_direction != None:
				direction_order.append(y_direction)
			if x_direction != None:
				direction_order.append(x_direction)

	for index in range(4):
		if index not in direction_order:
			direction_order.append(index)

	for index in direction_order:
		next_x = current[0] + delta_x[index]
		next_y = current[1] + delta_y[index]

		inside = (
			next_x >= x
			and next_x < x + n
			and next_y >= y
			and next_y < y + n
		)

		if inside and [next_x, next_y] not in visited:
			if can_move(directions[index]):
				move(directions[index])

				if search_maze_tile(x, y, n, visited):
					return True

				move(opposites[index])

	return False


def solve_maze_dfs(x, y, n):
	visited = []
	return search_maze_tile(x, y, n, visited)


def maze_directions():
	return [North, East, South, West]


def maze_opposites():
	return [South, West, North, East]


def maze_delta_x():
	return [0, 1, 0, -1]


def maze_delta_y():
	return [1, 0, -1, 0]


def maze_tile_inside(x, y, n, tile_x, tile_y):
	return (
		tile_x >= x
		and tile_x < x + n
		and tile_y >= y
		and tile_y < y + n
	)


def maze_ordered_direction_indices():
	current_x = get_pos_x()
	current_y = get_pos_y()
	target = measure()
	order = []

	# 优先尝试朝向宝藏的方向。即使该方向有墙，后面仍会检查
	# can_move()并继续尝试其他方向。
	if target != None:
		difference_x = target[0] - current_x
		difference_y = target[1] - current_y
		x_direction = None
		y_direction = None

		if difference_x > 0:
			x_direction = 1
		elif difference_x < 0:
			x_direction = 3

		if difference_y > 0:
			y_direction = 0
		elif difference_y < 0:
			y_direction = 2

		if abs(difference_x) >= abs(difference_y):
			if x_direction != None:
				order.append(x_direction)
			if y_direction != None:
				order.append(y_direction)
		else:
			if y_direction != None:
				order.append(y_direction)
			if x_direction != None:
				order.append(x_direction)

	for index in range(4):
		if index not in order:
			order.append(index)

	return order


def maze_available_directions(x, y, n, visited):
	directions = maze_directions()
	delta_x = maze_delta_x()
	delta_y = maze_delta_y()
	available = []
	current_x = get_pos_x()
	current_y = get_pos_y()

	for index in maze_ordered_direction_indices():
		next_x = current_x + delta_x[index]
		next_y = current_y + delta_y[index]

		if (
			maze_tile_inside(x, y, n, next_x, next_y)
			and [next_x, next_y] not in visited
			and can_move(directions[index])
		):
			available.append(index)

	return available


def search_maze_path(x, y, n, visited):
	# 返回从当前格到宝藏的方向列表。
	# 找到宝藏时不回退，因此执行本函数的无人机会停在宝藏上。
	if get_entity_type() == Entities.Treasure:
		return []

	current = [get_pos_x(), get_pos_y()]

	if current not in visited:
		visited.append(current)

	directions = maze_directions()
	opposites = maze_opposites()
	delta_x = maze_delta_x()
	delta_y = maze_delta_y()

	for index in maze_ordered_direction_indices():
		next_x = current[0] + delta_x[index]
		next_y = current[1] + delta_y[index]

		if (
			maze_tile_inside(x, y, n, next_x, next_y)
			and [next_x, next_y] not in visited
			and can_move(directions[index])
		):
			move(directions[index])
			path = search_maze_path(x, y, n, visited)

			if path != None:
				path.insert(0, directions[index])
				return path

			move(opposites[index])

	return None


def search_selected_maze_branches(
	x,
	y,
	n,
	visited,
	branch_indices
):
	# 本函数由主无人机和辅助无人机同时执行。
	# 两边只领取各自的第一层分支，之后在分支内部独立DFS。
	if get_entity_type() == Entities.Treasure:
		return []

	directions = maze_directions()
	opposites = maze_opposites()
	delta_x = maze_delta_x()
	delta_y = maze_delta_y()
	current_x = get_pos_x()
	current_y = get_pos_y()

	for index in branch_indices:
		next_x = current_x + delta_x[index]
		next_y = current_y + delta_y[index]

		if (
			maze_tile_inside(x, y, n, next_x, next_y)
			and [next_x, next_y] not in visited
			and can_move(directions[index])
		):
			move(directions[index])
			path = search_maze_path(x, y, n, visited)

			if path != None:
				path.insert(0, directions[index])
				return path

			move(opposites[index])

	return None


def follow_maze_path(path):
	for direction in path:
		if not move(direction):
			return False

	return get_entity_type() == Entities.Treasure


def solve_maze_dfs_two_drones(x, y, n):
	# 主无人机先走过没有分支的公共通道。这样辅助无人机是在
	# 第一个真正的岔路口生成，而不是浪费在同一条单通道上。
	visited = []
	directions = maze_directions()

	while True:
		if get_entity_type() == Entities.Treasure:
			return True

		current = [get_pos_x(), get_pos_y()]

		if current not in visited:
			visited.append(current)

		available = maze_available_directions(x, y, n, visited)

		if len(available) == 0:
			return False

		if len(available) >= 2:
			break

		if not move(directions[available[0]]):
			return False

	# 交替分配岔路口的分支，确保辅助无人机不会再生成其他无人机。
	main_branches = []
	helper_branches = []

	for index in range(len(available)):
		if index % 2 == 0:
			main_branches.append(available[index])
		else:
			helper_branches.append(available[index])

	helper = spawn_drone(
		search_selected_maze_branches,
		x,
		y,
		n,
		visited,
		helper_branches
	)

	# 如果没有空闲无人机，则由当前无人机搜索全部分支。
	if helper == None:
		return search_selected_maze_branches(
			x,
			y,
			n,
			visited,
			available
		) != None

	main_path = search_selected_maze_branches(
		x,
		y,
		n,
		visited,
		main_branches
	)
	helper_path = wait_for(helper)

	# 主无人机自己找到宝藏时，它已经停在宝藏上。
	if main_path != None:
		return get_entity_type() == Entities.Treasure

	# 辅助无人机结束后会消失。主无人机仍在岔路口，沿辅助无人机
	# 返回的路线重新走到宝藏，保证后续复用和收获由主无人机执行。
	if helper_path != None:
		return follow_maze_path(helper_path)

	return False


def reverse_direction_order(order):
	reversed_order = []

	for index in range(len(order) - 1, -1, -1):
		reversed_order.append(order[index])

	return reversed_order


def search_maze_for_collection(
	x,
	y,
	n,
	visited,
	reverse_order,
	target,
	reuse,
	cost,
	other_drone
):
	# 子无人机结束、宝藏位置变化或迷宫被收掉，均表示本轮
	# 搜索应停止。每轮只处理启动时测量到的那一个宝藏。
	if other_drone != None and has_finished(other_drone):
		return False

	entity = get_entity_type()

	if entity != Entities.Hedge and entity != Entities.Treasure:
		return False

	if measure() != target:
		return False

	if entity == Entities.Treasure:
		if get_pos_x() != target[0] or get_pos_y() != target[1]:
			return False

		if reuse:
			return use_item(Items.Weird_Substance, cost)

		return harvest()

	current = [get_pos_x(), get_pos_y()]

	if current not in visited:
		visited.append(current)

	directions = maze_directions()
	opposites = maze_opposites()
	delta_x = maze_delta_x()
	delta_y = maze_delta_y()
	order = maze_ordered_direction_indices()

	if reverse_order:
		order = reverse_direction_order(order)

	for index in order:
		if other_drone != None and has_finished(other_drone):
			return False

		if measure() != target:
			return False

		next_x = current[0] + delta_x[index]
		next_y = current[1] + delta_y[index]

		if (
			maze_tile_inside(x, y, n, next_x, next_y)
			and [next_x, next_y] not in visited
			and can_move(directions[index])
		):
			if not move(directions[index]):
				continue

			if search_maze_for_collection(
				x,
			y,
			n,
				visited,
				reverse_order,
				target,
				reuse,
				cost,
				other_drone
			):
				return True

			# 对方处理了宝藏时立即结束，避免在已变化的迷宫里
			# 继续沿旧DFS路径搜索。
			if measure() != target:
				return False

			if not move(opposites[index]):
				return False

	return False


def maze_collection_worker(
	x,
	y,
	n,
	target,
	reuse,
	cost,
	reverse_order,
	other_drone
):
	visited = []
	return search_maze_for_collection(
		x,
		y,
		n,
		visited,
		reverse_order,
		target,
		reuse,
		cost,
		other_drone
	)


def collect_one_maze_treasure(x, y, n, reuse, cost):
	target = measure()

	if target == None:
		quick_print("迷宫宝藏测量失败")
		return False

	helper = spawn_drone(
		maze_collection_worker,
		x,
		y,
		n,
		target,
		reuse,
		cost,
		True,
		None
	)

	main_success = maze_collection_worker(
		x,
		y,
		n,
		target,
		reuse,
		cost,
		False,
		helper
	)

	if helper == None:
		return main_success

	helper_success = wait_for(helper)
	return main_success or helper_success


def collect_and_reuse_maze_two_drones(
	x,
	y,
	n,
	reuse_count,
	weird_reserve
):
	cost = get_maze_substance_cost(n)
	reused = 0

	while reused < reuse_count:
		if num_items(Items.Weird_Substance) < cost + weird_reserve:
			break

		if not collect_one_maze_treasure(x, y, n, True, cost):
			quick_print("迷宫宝藏复用失败", reused, "/", reuse_count)
			return False

		reused += 1

	# 最后一个宝藏只收获一次，清除迷宫后再退出本批。
	if not collect_one_maze_treasure(x, y, n, False, cost):
		quick_print("迷宫最终宝藏收获失败")
		return False

	return True


def collect_and_reuse_maze(
	x,
	y,
	n,
	reuse_count,
	weird_reserve
):
	return collect_and_reuse_maze_two_drones(
		x,
		y,
		n,
		reuse_count,
		weird_reserve
	)


def grow_and_solve_maze(
	x,
	y,
	n,
	reuse_count,
	weird_reserve
):
	if not generate_maze(x, y, n):
		return False

	return collect_and_reuse_maze(
		x,
		y,
		n,
		reuse_count,
		weird_reserve
	)
	
	