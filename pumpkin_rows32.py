from move import move_to
from pumpkin import check_pumpkin_tile


SIZE = 32


def ready_pumpkin_row():
	ready = []
	for column in range(SIZE):
		ready.append(False)
	remaining = SIZE

	while remaining > 0:
		column = get_pos_x()
		if not ready[column]:
			if check_pumpkin_tile(True, False, False) == True:
				ready[column] = True
				remaining -= 1
		if remaining > 0:
			move(East)
	return True


def wait_then_tend_row(row):
	move_to(0, row)
	# 本轮成熟南瓜被收走后，该格变空，再开始下一轮。
	while get_entity_type() == Entities.Pumpkin:
		do_a_flip()
	return ready_pumpkin_row()


def farm_32x32_pumpkin_forever():
	if get_world_size() != SIZE:
		quick_print("need 32x32 world")
		return

	clear()
	workers = []
	for row in range(SIZE - 1):
		worker = spawn_drone(ready_pumpkin_row)
		if worker == None:
			quick_print("need 32 drones")
			return
		workers.append(worker)
		move(North)

	harvested = 0
	while True:
		ready_pumpkin_row()
		move_to(0, SIZE - 1)

		next_workers = []
		for row in range(SIZE - 1):
			if not wait_for(workers[row]):
				quick_print("pumpkin row failed", row)
				return
			worker = spawn_drone(wait_then_tend_row, row)
			if worker == None:
				quick_print("could not replace pumpkin row", row)
				return
			next_workers.append(worker)

		# 31个子无人机都已确认各自行成熟，主无人机也确认了第31行。
		if not can_harvest() or not harvest():
			quick_print("32x32 pumpkin harvest failed")
			return
		harvested += 1
		quick_print("32x32 pumpkin harvested", harvested)
		workers = next_workers
		