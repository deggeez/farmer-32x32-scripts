def farm_sunflower_row():
	while True:
		if get_ground_type() != Grounds.Soil:
			till()

		if can_harvest():
			harvest()

		if get_entity_type() != Entities.Sunflower:
			plant(Entities.Sunflower)

		if get_water() < 0.5:
			use_item(Items.Water)

		# 向东走完一整行后从右边界环绕到左边界，不反向折返。
		move(East)
		