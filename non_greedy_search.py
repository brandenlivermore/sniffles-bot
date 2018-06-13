def non_greedy_search(item, query):
	query = query.replace(' ', '').lower()
	item = item.lower()
	query_len = len(query)
	item_len = len(item)
	
	item_index = 0
	query_index = 0
	
	
	if query_len > item_len or query_len == 0:
		return 0
		
	score = 0
	
	correct_in_a_row = 0
	matched_first_char = False 
	prev_was_space = False
	while query_index < query_len and item_index < item_len:
		query_char = query[query_index]
		item_char = item[item_index]
	
		if item_char == ' ':
			prev_was_space = True
			item_index += 1
			continue
		
		if query_char == item_char:
			query_index += 1
			score += 5
			score += correct_in_a_row * 4
			correct_in_a_row += 1
			if item_index == 0:
				matched_first_char = True
				score += 5
			elif prev_was_space:
				if matched_first_char:
					score += 5
				score += 5
		else:
			correct_in_a_row = 0
		
		prev_was_space = False
		
		item_index += 1
	
	if query_index < query_len:
		return 0
	else:
		return score
