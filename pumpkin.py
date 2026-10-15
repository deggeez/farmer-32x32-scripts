from move import move_to
from rectangle_and_route import rectangle_in_bounds
from rectangle_and_route import rectangle_positions
from growth_options import apply_growth_options


def check_pumpkin_tile(
	use_water,
	use_fertilizer,
	cure_infected
):
	entity = get_entity_type()

	if entity == Entities.Pumpkin:
		if can_harvest():
			return True

		apply_growth_options(
			use_water,
			use_fertilizer,
			cure_infected
		)
		return False

	# 草地上的Grass会自动存在，必须直接翻土，不能等待它变成None。
	if (
		get_ground_type() != Grounds.Soil
		and entity == Entities.Grass
	):
		till()
	else:
		# 枯死南瓜和其他实体都直接清除。harvest()也能移除
		# 尚未成熟的普通植物。
		if entity != None:
			harvest()

			if get_entity_type() != None:
				return None

		if get_ground_type() != Grounds.Soil:
			till()

	if get_ground_type() != Grounds.Soil:
		return None

	if get_entity_type() != None:
		return None

	if num_items(Items.Carrot) < 4:
		return None

	if not plant(Entities.Pumpkin):
		return None

	apply_growth_options(
		use_water,
		use_fertilizer,
		cure_infected
	)

	# 新种下的南瓜还没有成熟，需要下轮继续检查。
	return False


def tend_pumpkin_positions(
	positions,
	use_water,
	use_fertilizer,
	cure_infected
):
	pending = positions
	reverse_route = False

	while len(pending) > 0:
		remaining = []

		if reverse_route:
			indices = range(len(pending) - 1, -1, -1)
		else:
			indices = range(len(pending))

		for index in indices:
			position = pending[index]
			move_to(position[0], position[1])

			result = check_pumpkin_tile(
				use_water,
				use_fertilizer,
				cure_infected
			)

			# None表示资源不足、清理失败、翻土失败或种植失败。
			if result == None:
				return False

			if not result:
				# 反向访问时恢复pending的原始顺序，保证下一轮
				# 真正从当前终点反向移动。
				if reverse_route:
					remaining.insert(0, position)
				else:
					remaining.append(position)

		pending = remaining
		reverse_route = not reverse_route

	return True


def split_pumpkin_positions(x, y, n, m):
	positions = rectangle_positions(x, y, n, m)
	left_positions = []
	right_positions = []
	split_x = x + n // 2

	for position in positions:
		if position[0] < split_x:
			left_positions.append(position)
		else:
			right_positions.append(position)

	return [left_positions, right_positions]


def harvest_largest_pumpkin(x, y):
	move_to(x, y)

	if not can_harvest():
		return False

	harvest()
	return True


def grow_largest_pumpkin(
	x,
	y,
	n,
	m,
	use_water,
	use_fertilizer,
	cure_infected
):
	if not rectangle_in_bounds(x, y, n, m):
		return False

	positions = rectangle_positions(x, y, n, m)

	if not tend_pumpkin_positions(
		positions,
		use_water,
		use_fertilizer,
		cure_infected
	):
		return False

	return harvest_largest_pumpkin(x, y)


def grow_largest_pumpkin_two_drones(
	x,
	y,
	n,
	m,
	use_water,
	use_fertilizer,
	cure_infected
):
	if not rectangle_in_bounds(x, y, n, m):
		return False

	if n < 2:
		return False

	position_groups = split_pumpkin_positions(x, y, n, m)
	left_positions = position_groups[0]
	right_positions = position_groups[1]

	# 辅助无人机维护右侧4×8，当前无人机维护左侧4×8。
	helper = spawn_drone(
		tend_pumpkin_positions,
		right_positions,
		use_water,
		use_fertilizer,
		cure_infected
	)

	left_ready = tend_pumpkin_positions(
		left_positions,
		use_water,
		use_fertilizer,
		cure_infected
	)

	if helper == None:
		right_ready = tend_pumpkin_positions(
			right_positions,
			use_water,
			use_fertilizer,
			cure_infected
		)
	else:
		right_ready = wait_for(helper)

	if not left_ready or not right_ready:
		return False

	# 两个4×8都全部成熟后，才由当前主无人机唯一收获整个8×8。
	return harvest_largest_pumpkin(x, y)
	