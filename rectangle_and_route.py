from move import axis_distance


rectangle_registry = []


def route_distance(x1, y1, x2, y2):
	size = get_world_size()
	return (
		axis_distance(x1, x2, size)
		+ axis_distance(y1, y2, size)
	)


def reset_rectangle_registry():
	global rectangle_registry
	rectangle_registry = []


def rectangle_in_bounds(x, y, n, m):
	size = get_world_size()

	return (
		x >= 0
		and y >= 0
		and n > 0
		and m > 0
		and x + n <= size
		and y + m <= size
	)


def rectangles_overlap(x1, y1, n1, m1, x2, y2, n2, m2):
	return not (
		x1 + n1 <= x2
		or x2 + n2 <= x1
		or y1 + m1 <= y2
		or y2 + m2 <= y1
	)


def reserve_rectangle(x, y, n, m):
	if not rectangle_in_bounds(x, y, n, m):
		return False

	for rectangle in rectangle_registry:
		if rectangles_overlap(
			x,
			y,
			n,
			m,
			rectangle[0],
			rectangle[1],
			rectangle[2],
			rectangle[3]
		):
			return False

	rectangle_registry.append([x, y, n, m])
	return True


def rectangle_positions(x, y, n, m):
	positions = []
	current_x = get_pos_x()
	current_y = get_pos_y()

	start_left = (
		route_distance(current_x, current_y, x, y)
		<= route_distance(current_x, current_y, x + n - 1, y)
	)

	start_bottom = (
		route_distance(current_x, current_y, x, y)
		<= route_distance(current_x, current_y, x, y + m - 1)
	)

	for row_index in range(m):
		if start_bottom:
			row_y = y + row_index
		else:
			row_y = y + m - 1 - row_index

		left_to_right = start_left

		if row_index % 2 == 1:
			left_to_right = not left_to_right

		for column_index in range(n):
			if left_to_right:
				column_x = x + column_index
			else:
				column_x = x + n - 1 - column_index

			positions.append([column_x, row_y])

	return positions
	