from move import move_to
from cactus import tend_current_cactus


SIZE = 32


def sort_row_round_trip():
	row = get_pos_y()
	move_to(0, row)
	left = 0
	right = SIZE - 1

	while left < right:
		swapped = False
		for column in range(left, right):
			if measure() > measure(East):
				swap(East)
				swapped = True
			if column < right - 1:
				move(East)
		if not swapped:
			break
		right -= 1

		swapped = False
		for column in range(right, left, -1):
			if measure() < measure(West):
				swap(West)
				swapped = True
			if column > left + 1:
				move(West)
		if not swapped:
			break
		left += 1

	return True


def sort_column_round_trip():
	column = get_pos_x()
	move_to(column, 0)
	bottom = 0
	top = SIZE - 1

	while bottom < top:
		swapped = False
		for row in range(bottom, top):
			if measure() > measure(North):
				swap(North)
				swapped = True
			if row < top - 1:
				move(North)
		if not swapped:
			break
		top -= 1

		swapped = False
		for row in range(top, bottom, -1):
			if measure() < measure(South):
				swap(South)
				swapped = True
			if row > bottom + 1:
				move(South)
		if not swapped:
			break
		bottom += 1

	return True


def plant_and_sort_row():
	for column in range(SIZE):
		if not tend_current_cactus(False, False, False):
			return False
		move(East)

	while True:
		all_ready = True
		for column in range(SIZE):
			if not can_harvest():
				all_ready = False
			move(East)
		if all_ready:
			break

	return sort_row_round_trip()


def wait_then_sort_column(column, row_workers):
	move_to(column, 0)
	# 全部行结束后，才允许开始列排序。
	for worker in row_workers:
		while not has_finished(worker):
			do_a_flip()
	return sort_column_round_trip()


def wait_then_plant_row(row):
	move_to(0, row)
	# 上一轮整片仙人掌被收获后，开始下一轮行任务。
	while get_entity_type() == Entities.Cactus:
		do_a_flip()
	return plant_and_sort_row()


def farm_sorted_cactus_32x32():
	if get_world_size() != SIZE:
		quick_print("need 32x32 world")
		return

	clear()
	row_workers = []
	for row in range(SIZE - 1):
		worker = spawn_drone(plant_and_sort_row)
		if worker == None:
			quick_print("need 32 drones")
			return
		row_workers.append(worker)
		move(North)

	harvested = 0
	while True:
		if not plant_and_sort_row():
			quick_print("main cactus row failed")
			return
		move_to(0, 0)

		column_workers = []
		for column in range(SIZE - 1):
			if not wait_for(row_workers[column]):
				quick_print("cactus row failed", column)
				return
			worker = spawn_drone(wait_then_sort_column, column, row_workers)
			if worker == None:
				quick_print("could not replace cactus row", column)
				return
			column_workers.append(worker)

		move_to(SIZE - 1, 0)
		if not sort_column_round_trip():
			quick_print("main cactus column failed")
			return
		move_to(0, 0)

		next_row_workers = []
		for row in range(SIZE - 1):
			if not wait_for(column_workers[row]):
				quick_print("cactus column failed", row)
				return
			worker = spawn_drone(wait_then_plant_row, row)
			if worker == None:
				quick_print("could not replace cactus column", row)
				return
			next_row_workers.append(worker)

		if not can_harvest() or not harvest():
			quick_print("32x32 cactus harvest failed")
			return
		harvested += 1
		quick_print("32x32 cactus harvested", harvested)
		row_workers = next_row_workers
		move_to(0, SIZE - 1)
		