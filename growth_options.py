def water_current_tile(threshold):
	if get_water() >= threshold:
		return False

	if num_items(Items.Water) <= 0:
		return False

	return use_item(Items.Water)


def fertilize_current_tile():
	if get_entity_type() == None:
		return False

	if can_harvest():
		return False

	if num_items(Items.Fertilizer) <= 0:
		return False

	return use_item(Items.Fertilizer)


def cure_current_tile():
	if get_entity_type() == None:
		return False

	if num_items(Items.Weird_Substance) <= 0:
		return False

	return use_item(Items.Weird_Substance)


def apply_growth_options(
	use_water,
	use_fertilizer,
	cure_infected
):
	if use_water:
		water_current_tile(0.5)

	fertilized = False

	if use_fertilizer:
		fertilized = fertilize_current_tile()

	# 只有本次确实施过肥时才尝试治疗，避免把健康植物感染。
	# 治疗还会影响相邻植物，因此当前布局默认传入False。
	if cure_infected and fertilized:
		cure_current_tile()

	return True
	