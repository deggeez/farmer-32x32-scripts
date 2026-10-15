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


def keep_carrot():
	if get_entity_type() != Entities.Carrot:
		if get_entity_type() != None:
			harvest()
		if get_ground_type() != Grounds.Soil:
			till()
		plant(Entities.Carrot)
	if get_entity_type() == Entities.Carrot and get_water() < 0.5:
		use_item(Items.Water)


def farm_poly_carrot_row():
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
			keep_carrot()
			if get_entity_type() == Entities.Carrot:
				request_target = pending[column]
				if request_target != -1:
					if active[request_target] and can_harvest():
						harvest()
						references[request_target] -= 1
						if references[request_target] == 0:
							wanted[request_target] = None
							active[request_target] = False
						pending[column] = -1
						plant(Entities.Carrot)
						if not bonus_reported:
							quick_print("first companion carrot", row_y, column)
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
						plant(Entities.Carrot)

		# 行内始终只向东，行尾通过地图环绕回左侧。
		move(East)
		