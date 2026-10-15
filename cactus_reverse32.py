from move import move_to
from cactus import tend_current_cactus


SIZE = 32


def plant_and_sort_reverse_row():
	row = get_pos_y()

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

	# 数值从西到东递减。
	for pass_index in range(SIZE - 1):
		swapped = False
		for column in range(SIZE - 1 - pass_index):
			move_to(column, row)
			if measure() < measure(East):
				swap(East)
				swapped = True
		if not swapped:
			break

	return True


def sort_reverse_column():
	column = get_pos_x()

	# 数值从南到北递减；列排序不会破坏已排好的行顺序。
	for pass_index in range(SIZE - 1):
		swapped = False
		for row in range(SIZE - 1 - pass_index):
			move_to(column, row)
			if measure() < measure(North):
				swap(North)
				swapped = True
		if not swapped:
			break

	return True


def run_reverse_phase(task, direction):
	workers = []
	for index in range(SIZE - 1):
		worker = spawn_drone(task)
		if worker == None:
			return False
		workers.append(worker)
		move(direction)

	all_ready = task()
	for worker in workers:
		if not wait_for(worker):
			all_ready = False
	return all_ready


def grow_reverse_cactus_32x32():
	if get_world_size() != SIZE:
		return False

	clear()
	if not run_reverse_phase(plant_and_sort_reverse_row, North):
		return False

	move_to(0, 0)
	if not run_reverse_phase(sort_reverse_column, East):
		return False

	# 先完成整片逆序，再在左上角收获一次。
	move_to(0, SIZE - 1)
	if not can_harvest():
		return False
	return harvest()
	