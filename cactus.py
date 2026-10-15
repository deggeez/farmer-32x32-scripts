from move import move_to
from rectangle_and_route import rectangle_in_bounds
from rectangle_and_route import rectangle_positions
from growth_options import apply_growth_options


def tend_current_cactus(
	use_water,
	use_fertilizer,
	cure_infected
):
	entity = get_entity_type()

	if entity == Entities.Cactus:
		apply_growth_options(
			use_water,
			use_fertilizer,
			cure_infected
		)
		return True

	# 草地上的Grass会自动存在，必须直接翻土，不能等待它变成None。
	if (
		get_ground_type() != Grounds.Soil
		and entity == Entities.Grass
	):
		till()
	else:
		if entity != None:
			harvest()

			if get_entity_type() != None:
				return False

		if get_ground_type() != Grounds.Soil:
			till()

	if get_ground_type() != Grounds.Soil:
		return False

	if get_entity_type() != None:
		return False

	if num_items(Items.Pumpkin) < 2:
		return False

	if not plant(Entities.Cactus):
		return False

	apply_growth_options(
		use_water,
		use_fertilizer,
		cure_infected
	)

	return True


def plant_cactus_positions(
	positions,
	use_water,
	use_fertilizer,
	cure_infected
):
	while True:
		all_ready = True

		for position in positions:
			move_to(position[0], position[1])

			if not tend_current_cactus(
				use_water,
				use_fertilizer,
				cure_infected
			):
				return False

			if not can_harvest():
				all_ready = False

		if all_ready:
			return True


def split_cactus_positions(x, y, n, m):
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


def plant_cactus_rectangle_two_drones(
	x,
	y,
	n,
	m,
	use_water,
	use_fertilizer,
	cure_infected
):
	position_groups = split_cactus_positions(x, y, n, m)
	left_positions = position_groups[0]
	right_positions = position_groups[1]

	helper = spawn_drone(
		plant_cactus_positions,
		right_positions,
		use_water,
		use_fertilizer,
		cure_infected
	)

	left_success = plant_cactus_positions(
		left_positions,
		use_water,
		use_fertilizer,
		cure_infected
	)

	if helper == None:
		right_success = plant_cactus_positions(
			right_positions,
			use_water,
			use_fertilizer,
			cure_infected
		)
	else:
		right_success = wait_for(helper)

	return left_success and right_success


def plant_cactus_rectangle(
	x,
	y,
	n,
	m,
	use_water,
	use_fertilizer,
	cure_infected
):
	positions = rectangle_positions(x, y, n, m)

	while True:
		all_ready = True

		for position in positions:
			move_to(position[0], position[1])

			if not tend_current_cactus(
				use_water,
				use_fertilizer,
				cure_infected
			):
				return False

			if not can_harvest():
				all_ready = False

		if all_ready:
			return True


def sort_cactus_rows(x, y, n, m):
	return sort_cactus_row_range(x, y, n, 0, m)


def sort_cactus_row_range(x, y, n, start_row, row_count):
	swaps = 0

	for row_offset in range(row_count):
		row = start_row + row_offset

		for pass_index in range(n - 1):
			pass_swapped = False

			# 每完成一轮，最右侧会多一个已经就位的最大值，
			# 后续不需要再次比较这些位置。
			for column in range(n - 1 - pass_index):
				move_to(x + column, y + row)

				if measure() > measure(East):
					swap(East)
					swaps += 1
					pass_swapped = True

			# 本轮没有交换，说明这一行已经有序。
			if not pass_swapped:
				break

	return swaps


def sort_cactus_columns(x, y, n, m):
	return sort_cactus_column_range(x, y, m, 0, n)


def sort_cactus_column_range(x, y, m, start_column, column_count):
	swaps = 0

	for column_offset in range(column_count):
		column = start_column + column_offset

		for pass_index in range(m - 1):
			pass_swapped = False

			# 每完成一轮，最上方会多一个已经就位的最大值。
			for row in range(m - 1 - pass_index):
				move_to(x + column, y + row)

				if measure() > measure(North):
					swap(North)
					swaps += 1
					pass_swapped = True

			# 本轮没有交换，说明这一列已经有序。
			if not pass_swapped:
				break

	return swaps


def cactus_rectangle_sorted(x, y, n, m):
	for row in range(m):
		for column in range(n - 1):
			move_to(x + column, y + row)

			if measure() > measure(East):
				return False

	for column in range(n):
		for row in range(m - 1):
			move_to(x + column, y + row)

			if measure() > measure(North):
				return False

	return True


def sort_cactus_rectangle_two_drones(x, y, n, m):
	first_round = True

	while True:
		# 第一阶段：两台无人机各自负责一半行。
		lower_row_count = m // 2
		upper_row_count = m - lower_row_count
		row_helper = spawn_drone(
			sort_cactus_row_range,
			x,
			y,
			n,
			lower_row_count,
			upper_row_count
		)

		lower_row_swaps = sort_cactus_row_range(
			x,
			y,
			n,
			0,
			lower_row_count
		)

		if row_helper == None:
			upper_row_swaps = sort_cactus_row_range(
				x,
				y,
				n,
				lower_row_count,
				upper_row_count
			)
		else:
			upper_row_swaps = wait_for(row_helper)

		row_swaps = lower_row_swaps + upper_row_swaps

		# 上一轮列阶段结束时，所有列都已经有序。如果本轮行阶段
		# 没有发生交换，则行列同时有序，可以直接结束。
		if not first_round and row_swaps == 0:
			return True

		# 第二阶段：确认全部行任务结束后，两台无人机各自负责一半列。
		left_column_count = n // 2
		right_column_count = n - left_column_count
		column_helper = spawn_drone(
			sort_cactus_column_range,
			x,
			y,
			m,
			left_column_count,
			right_column_count
		)

		left_column_swaps = sort_cactus_column_range(
			x,
			y,
			m,
			0,
			left_column_count
		)

		if column_helper == None:
			right_column_swaps = sort_cactus_column_range(
				x,
				y,
				m,
				left_column_count,
				right_column_count
			)
		else:
			right_column_swaps = wait_for(column_helper)

		column_swaps = left_column_swaps + right_column_swaps

		# 行阶段结束时所有行已经有序。如果列阶段没有交换，
		# 列排序没有破坏行顺序，因此整块田已经完成。
		if column_swaps == 0:
			return True

		first_round = False


def grow_sorted_cactus(
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

	if not plant_cactus_rectangle(
		x,
		y,
		n,
		m,
		use_water,
		use_fertilizer,
		cure_infected
	):
		return False

	first_round = True

	while True:
		row_swaps = sort_cactus_rows(x, y, n, m)

		if not first_round and row_swaps == 0:
			break

		column_swaps = sort_cactus_columns(x, y, n, m)

		if column_swaps == 0:
			break

		first_round = False

	move_to(x, y)

	if can_harvest():
		harvest()
		return True

	return False


def grow_sorted_cactus_two_drones(
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

	if not plant_cactus_rectangle_two_drones(
		x,
		y,
		n,
		m,
		use_water,
		use_fertilizer,
		cure_infected
	):
		return False

	if not sort_cactus_rectangle_two_drones(x, y, n, m):
		return False

	# 只有当前主无人机负责最终收获，辅助无人机在wait_for()后
	# 已经结束，避免两台无人机重复收获同一片仙人掌。
	move_to(x, y)

	if can_harvest():
		harvest()
		return True

	return False
	
	