"""
Functions for getting grid size for image_builder
"""

def get_factors(n: int) -> tuple:
	return [(i, n // i) for i in range(1, int(n**0.5)+1) if n % i == 0]

def reorder_pair(pair: tuple) -> tuple:
	return (max(pair), min(pair))

def factor_to_ratio(pair: tuple) -> float:
	return pair[0]/pair[1]

def valid_ratio_exists(ratios: list, max_ratio: float, min_ratio: float) -> bool:
	for ratio in ratios:
		if ratio >= min_ratio and ratio <= max_ratio:
			return True
	return False

def get_grid_size(n: int) -> tuple:
	MIN_RATIO = 1
	MAX_RATIO = 2.5

	while True:
		factors = list(map(reorder_pair, get_factors(n)))
		print(factors)
		factor_ratios = list(map(factor_to_ratio, factors))
		
		if not valid_ratio_exists(factor_ratios, MAX_RATIO, MIN_RATIO):
			n+=1
			continue
		dist_list = list(map(lambda x: abs(x - (MIN_RATIO + MAX_RATIO)/2), factor_ratios))
		return factors[dist_list.index(min(dist_list))]
