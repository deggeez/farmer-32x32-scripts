ROW_LENGTH = 32


def empty_row(value):
	result = []
	for column in range(ROW_LENGTH):
		result.append(value)
	return result


def keep_companion(crop):
	if get_entity_type() != crop:
		if get_entity_type() != None:
			harvest()
		if get_ground_type() != Grounds.Soil:
			till()
		plant(crop)
	return get_entity_type() == crop


def restore_grassland():
	if get_entity_type() != None:
		harvest()
	if get_ground_type() != Grounds.Grassland:
		till()


def farm_poly_hay_row():
	row_y = get_pos_y()
	wanted = empty_row(None)
	active = empty_row(False)
	references = empty_row(0)
	pending = empty_row(-1)
	bonus_reported = False

	while True:
		column = get_pos_x()
		if wanted[column] != None:
			active[column] = keep_companion(wanted[column])
		else:
			if get_ground_type() != Grounds.Grassland or get_entity_type() != Entities.Grass:
				restore_grassland()
			else:
				request_target = pending[column]
				if request_target != -1:
					if active[request_target] and can_harvest():
						harvest()
						references[request_target] -= 1
						if references[request_target] == 0:
							wanted[request_target] = None
							active[request_target] = False
						pending[column] = -1
						if not bonus_reported:
							quick_print("first companion hay", row_y, column)
							bonus_reported = True
				else:
					companion = get_companion()
					accepted = False
					if companion != None:
						crop = companion[0]
						target_x = companion[1][0]
						target_y = companion[1][1]
						if target_y == row_y and pending[target_x] == -1:
							if wanted[target_x] == None or wanted[target_x] == crop:
								wanted[target_x] = crop
								references[target_x] += 1
								pending[column] = target_x
								accepted = True
					if not accepted and can_harvest():
						harvest()

		# 每台无人机始终只往东，行尾通过地图环绕回到行首。
		move(East)
		