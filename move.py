def axis_distance(start, target, size):
	forward = (target - start) % size
	backward = (start - target) % size

	if forward <= backward:
		return forward

	return backward


def move_to(target_x, target_y):
	size = get_world_size()
	target_x = target_x % size
	target_y = target_y % size

	current_x = get_pos_x()
	forward = (target_x - current_x) % size
	backward = (current_x - target_x) % size

	if forward <= backward:
		for unused in range(forward):
			move(East)
	else:
		for unused in range(backward):
			move(West)

	current_y = get_pos_y()
	forward = (target_y - current_y) % size
	backward = (current_y - target_y) % size

	if forward <= backward:
		for unused in range(forward):
			move(North)
	else:
		for unused in range(backward):
			move(South)

	return True
	