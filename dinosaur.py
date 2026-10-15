from move import move_to


# 以下是按snaky2.py移植的实现。它保留原算法的区域方向、
# 剪枝、递归进入和逐层退出规则，但统一通过reference_step移动，
# 方便之后加入我们的蛇身模拟和安全判定。
REFERENCE_X = 0
REFERENCE_Y = 1
REFERENCE_WIDTH = 2
REFERENCE_DIR = 3
REFERENCE_UP = 4
REFERENCE_MAIN = 5


def reference_reverse(direction):
	if direction == North:
		return South
	if direction == South:
		return North
	if direction == East:
		return West
	return East


def make_reference_area(x, y, width, direction, up, is_main):
	return [x, y, width, direction, up, is_main]


def reference_position_id(x, y, size):
	# 原实现使用1到size*size的编号，最左列是返回通道。
	if x == 0:
		return size - y
	if y % 2 == 0:
		return size + (size - 1) * y + x
	return size + (size - 1) * y + size - x


def reference_area_direction(area, x, y):
	x_n = area[REFERENCE_X]
	y_n = area[REFERENCE_Y]
	width = area[REFERENCE_WIDTH]
	direction = area[REFERENCE_DIR]
	up = area[REFERENCE_UP]

	if direction == East or direction == West:
		up_distance = abs(y - y_n)
		line_distance = abs(x - x_n)
	else:
		up_distance = abs(x - x_n)
		line_distance = abs(y - y_n)

	if up_distance % 2 == 0:
		if line_distance == 0 and up_distance != 0:
			return up
		return direction

	if line_distance == width - 1:
		return up
	return reference_reverse(direction)


def reference_area_contains(location, area, size, upper, can_equal):
	x = location[0]
	y = location[1]
	x_n = area[REFERENCE_X]
	y_n = area[REFERENCE_Y]
	width = area[REFERENCE_WIDTH]
	direction = area[REFERENCE_DIR]
	up = area[REFERENCE_UP]

	if width <= 0:
		return False

	if area[REFERENCE_MAIN]:
		if not upper:
			return x != 0
		current_id = reference_position_id(get_pos_x(), get_pos_y(), size)
		target_id = reference_position_id(x, y, size)
		return current_id > size and current_id <= target_id

	if upper:
		current_x = get_pos_x()
		current_y = get_pos_y()

		if not reference_area_contains([current_x, current_y], area, size, False, True):
			return False

		same_level = False

		if up == East:
			if current_x > x:
				return False
			if current_x == x:
				if not can_equal:
					return False
				same_level = True
		elif up == West:
			if current_x < x:
				return False
			if current_x == x:
				if not can_equal:
					return False
				same_level = True
		elif up == North:
			if current_y > y:
				return False
			if current_y == y:
				if not can_equal:
					return False
				same_level = True
		else:
			if current_y < y:
				return False
			if current_y == y:
				if not can_equal:
					return False
				same_level = True

		if same_level:
			next_direction = reference_area_direction(area, current_x, current_y)

			if current_x > x and next_direction != West:
				return False
			if current_x < x and next_direction != East:
				return False
			if current_y > y and next_direction != South:
				return False
			if current_y < y and next_direction != North:
				return False

	if direction == East:
		if x <= x_n - width or x > x_n:
			return False
	elif direction == West:
		if x < x_n or x >= x_n + width:
			return False
	elif direction == North:
		if y > y_n or y <= y_n - width:
			return False
	else:
		if y < y_n or y >= y_n + width:
			return False

	if up == North and y > y_n:
		return False
	if up == West and x < x_n:
		return False
	if up == South and y < y_n:
		return False
	if up == East and x > x_n:
		return False

	return True


def reference_step(direction):
	# 所有参考算法的实际移动都经过这一层；后续安全优化只需改这里。
	return move(direction)


def reference_move_in_area(area, size):
	x = get_pos_x()
	y = get_pos_y()

	if not reference_area_contains([x, y], area, size, False, True):
		# quick_move可能已经跨过区域边界；原版此时snaky_move返回None，
		# 调用者继续运行，因此这里也视作已经完成而不是失败。
		return True

	return reference_step(reference_area_direction(area, x, y))


def reference_quick_move(target, area, size):
	target_x = target[0]
	target_y = target[1]
	x_n = area[REFERENCE_X]
	y_n = area[REFERENCE_Y]
	direction = area[REFERENCE_DIR]
	up = area[REFERENCE_UP]
	break_x = None
	break_y = None
	x = get_pos_x()
	y = get_pos_y()

	if not reference_area_contains([x, y], area, size, False, True):
		# 递归回卷时，内层调用可能已经把蛇头送出当前区域。
		# 原版把这种情况当作无需继续移动，而不是错误。
		return [None, True]

	if not reference_area_contains(target, area, size, True, True):
		result = reference_quick_move([x_n, y_n], area, size)

		if not result[1]:
			return result
		if not reference_move_in_area(area, size):
			return [None, False]
		# 目标不在当前局部路线的前方：已经回到区域端点并推进一格，
		# 本轮不吃苹果，但这不是移动失败，交还给外层继续判断。
		return [None, True]

	maximum_steps = size * size * 2

	for unused in range(maximum_steps):
		x = get_pos_x()
		y = get_pos_y()

		if x == target_x and y == target_y:
			if break_x == None:
				break_x = target_x
				break_y = target_y
			return [[break_x, break_y], True]

		if direction == East or direction == West:
			if x == target_x:
				break_x = x
				break_y = y

				for unused2 in range(abs(y - target_y)):
					if not reference_step(up):
						return [None, False]
				continue

			next_direction = reference_area_direction(area, x, y)

			if next_direction == East:
				if x > target_x:
					if not reference_step(up):
						return [None, False]
				else:
					for unused2 in range(target_x - x):
						if not reference_step(East):
							return [None, False]
			elif next_direction == West:
				if x < target_x:
					if not reference_step(up):
						return [None, False]
				else:
					for unused2 in range(x - target_x):
						if not reference_step(West):
							return [None, False]
			elif not reference_step(next_direction):
				return [None, False]
		else:
			if y == target_y:
				break_x = x
				break_y = y

				for unused2 in range(abs(x - target_x)):
					if not reference_step(up):
						return [None, False]
				continue

			next_direction = reference_area_direction(area, x, y)

			if next_direction == North:
				if y > target_y:
					if not reference_step(up):
						return [None, False]
				else:
					for unused2 in range(target_y - y):
						if not reference_step(North):
							return [None, False]
			elif next_direction == South:
				if y < target_y:
					if not reference_step(up):
						return [None, False]
				else:
					for unused2 in range(y - target_y):
						if not reference_step(South):
							return [None, False]
			elif not reference_step(next_direction):
				return [None, False]

	return [None, False]


def reference_quick_getout(area, size):
	x_n = area[REFERENCE_X]
	y_n = area[REFERENCE_Y]
	direction = area[REFERENCE_DIR]
	up = area[REFERENCE_UP]
	x = get_pos_x()
	y = get_pos_y()

	if not reference_area_contains([x, y], area, size, False, True):
		return True

	# 忠实保留原实现的不变量：递归结束时蛇头已经在出口轨道旁，
	# 因此沿up最多补一格，再沿dir到边缘并多走一格跨回父区域。
	if up == North or up == South:
		if y != y_n:
			if not reference_step(up):
				return False

		for unused in range(abs(x - x_n) + 1):
			if not reference_step(direction):
				return False
	else:
		if x != x_n:
			if not reference_step(up):
				return False

		for unused in range(abs(y - y_n) + 1):
			if not reference_step(direction):
				return False

	return True


def reference_eat_apple(target, area, count, size):
	x_n = area[REFERENCE_X]
	y_n = area[REFERENCE_Y]
	width = area[REFERENCE_WIDTH]
	direction = area[REFERENCE_DIR]
	up = area[REFERENCE_UP]
	target_x = target[0]
	target_y = target[1]
	x = get_pos_x()
	y = get_pos_y()

	if not reference_area_contains([x, y], area, size, False, True):
		return [target, count, True]

	if target_x == 0:
		result = reference_quick_move([x_n, y_n], area, size)

		if not result[1] or not reference_move_in_area(area, size):
			return [target, count, False]
		return [target, count, True]

	result = reference_quick_move(target, area, size)

	if not result[1]:
		return [target, count, False]
	if result[0] == None:
		return [target, count, True]

	count += 1
	x = get_pos_x()
	y = get_pos_y()
	break_x = result[0][0]
	break_y = result[0][1]
	inside_x = x
	inside_y = y
	outside_x = x
	outside_y = y

	if up == North or up == South:
		warning_distance = abs(y - y_n)
		new_width = abs(y - break_y)

		if direction == East:
			outside_x = x_n - width + 1
			inside_x = x_n
		else:
			outside_x = x_n + width - 1
			inside_x = x_n
	else:
		warning_distance = abs(x - x_n)
		new_width = abs(x - break_x)

		if direction == North:
			outside_y = y_n - width + 1
			inside_y = y_n
		else:
			outside_y = y_n + width - 1
			inside_y = y_n

	inside_area = make_reference_area(
		inside_x,
		inside_y,
		new_width - 1,
		up,
		direction,
		False
	)
	outside_area = make_reference_area(
		outside_x,
		outside_y,
		new_width - 1,
		up,
		reference_reverse(direction),
		False
	)

	if x != target_x or y != target_y:
		return [target, count, False]

	new_target = measure()

	if new_target == None:
		return [target, count, False]

	if reference_area_contains(new_target, area, size, True, True):
		recursive = reference_eat_apple(new_target, area, count, size)
		new_target = recursive[0]
		count = recursive[1]

		if not recursive[2]:
			return recursive
	elif warning_distance != 0 and reference_area_contains(new_target, inside_area, size, True, False):
		if not reference_step(direction):
			return [new_target, count, False]
		recursive = reference_eat_apple(new_target, inside_area, count, size)
		new_target = recursive[0]
		count = recursive[1]

		if not recursive[2]:
			return recursive
		recursive = reference_eat_apple(new_target, area, count, size)
		new_target = recursive[0]
		count = recursive[1]

		if not recursive[2]:
			return recursive
	elif warning_distance != 0 and reference_area_contains(new_target, outside_area, size, True, False):
		if not reference_step(reference_reverse(direction)):
			return [new_target, count, False]
		recursive = reference_eat_apple(new_target, outside_area, count, size)
		new_target = recursive[0]
		count = recursive[1]

		if not recursive[2]:
			return recursive
		recursive = reference_eat_apple(new_target, area, count, size)
		new_target = recursive[0]
		count = recursive[1]

		if not recursive[2]:
			return recursive

	if width < size - 1:
		if not reference_quick_getout(area, size):
			return [new_target, count, False]
	elif count <= y * 2 + 1:
		if not reference_quick_getout(area, size):
			return [new_target, count, False]
	else:
		result = reference_quick_move([x_n, y_n], area, size)

		if not result[1] or not reference_move_in_area(area, size):
			return [new_target, count, False]

	return [new_target, count, True]


def run_hamiltonian_pruning_dinosaur(size):
	area = make_reference_area(1, size - 1, size - 1, West, North, True)
	area_size = size * size
	# 保留原版排行榜实现：蛇长达到一半后回到完整主环。
	turn_point = area_size // 2
	directions = {}

	# 与原实现相同：主回路只打一次方向表。
	for x in range(size):
		for y in range(size):
			position_id = reference_position_id(x, y, size)

			if position_id < size:
				directions[position_id] = South
			elif position_id == size:
				directions[position_id] = East
			else:
				directions[position_id % area_size] = reference_area_direction(area, x, y)

	count = 1
	target = measure()

	if target == None:
		return count

	target_id = reference_position_id(target[0], target[1], size)

	while True:
		x = get_pos_x()
		y = get_pos_y()
		position_id = reference_position_id(x, y, size)

		if position_id == target_id:
			count += 1
			target = measure()

			if target == None:
				return count
			target_id = reference_position_id(target[0], target[1], size)

		if count >= turn_point:
			# 后半程按原实现回到完整主环，直到游戏判定不能继续移动。
			while True:
				position_id = position_id % area_size

				if not reference_step(directions[position_id]):
					return count
				position_id += 1

		compacted_limit = count - size + count // size

		if position_id < compacted_limit:
			if position_id < target_id and target_id <= compacted_limit:
				distance = target_id - position_id
			else:
				distance = compacted_limit - position_id

			for unused in range(distance):
				if not reference_step(directions[position_id]):
					return count
				position_id += 1
			continue

		if x == 0:
			if not reference_step(directions[position_id]):
				return count
			continue

		result = reference_eat_apple(target, area, count, size)
		target = result[0]
		count = result[1]

		if not result[2]:
			quick_print(
				"递归路线停止",
				"蛇长=",
				count,
				"位置=",
				get_pos_x(),
				get_pos_y(),
				"苹果=",
				target[0],
				target[1]
			)
			return count
		target_id = reference_position_id(target[0], target[1], size)


def get_apple_cost():
	cost = get_cost(Entities.Apple)

	if cost == None:
		return {}

	return cost


def full_dinosaur_cost(size):
	apple_cost = get_apple_cost()
	required = {}
	apples = size * size

	# 尾巴最大为size*size-1。游戏可能在吃掉最后一颗苹果时
	# 立刻购买下一颗，因此按size*size颗苹果预留资源。
	for item in apple_cost:
		required[item] = apple_cost[item] * apples

	return required


def can_afford_full_dinosaur(size):
	required = full_dinosaur_cost(size)

	for item in required:
		if num_items(item) < required[item]:
			return False

	return True


def print_missing_dinosaur_resources(size):
	required = full_dinosaur_cost(size)

	for item in required:
		if num_items(item) < required[item]:
			quick_print("恐龙等待资源", item, num_items(item), "/", required[item])


def grow_full_dinosaur(size):
	if get_world_size() != size:
		quick_print("恐龙区域大小错误", get_world_size(), "/", size)
		return False

	if size < 2 or size % 2 != 0:
		quick_print("恐龙哈密顿循环要求偶数边长", size)
		return False

	if not can_afford_full_dinosaur(size):
		print_missing_dinosaur_resources(size)
		return False

	start_bones = num_items(Items.Bone)

	# clear()会清空农场并把无人机送回(0,0)。
	clear()
	move_to(0, 0)
	change_hat(Hats.Dinosaur_Hat)

	tail_length = run_hamiltonian_pruning_dinosaur(size)

	# 摘下恐龙帽会把尾巴结算为骨头。
	change_hat(Hats.Straw_Hat)

	gained = num_items(Items.Bone) - start_bones
	quick_print("恐龙收获骨头", gained, "尾巴长度=", tail_length)
	return True


def farm_dinosaur_forever(size):
	completed = 0

	while can_afford_full_dinosaur(size):
		if not grow_full_dinosaur(size):
			return completed

		completed += 1

	print_missing_dinosaur_resources(size)
	return completed

	