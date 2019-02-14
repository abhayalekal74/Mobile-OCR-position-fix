import math

VERTICAL_THRES = 2 
HORIZ_THRES = 16

class Bound:
	def __init__(self, w, l, t, r, b):
		self.word = w
		self.left =  l
		self.top = t
		self.right = r
		self.bottom = b
		self.bound_merged = False

	def print(self):
		print (self.word, self.left, self.top, self.right, self.bottom, self.bound_merged)


class XPosMap:
	def __init__(self):
		self.max_x = 0
		self.pos_map = dict()
	
	def print(self):
		print ("\n\nmax_x", self.max_x)
		for k, v in self.pos_map.items():
			print (k) 
			[b.print() for b in v]


def update_x_pos_batches(x_pos_map, cur_merged_batch):
	if len(cur_merged_batch) > 0:
		max_right = math.ceil(cur_merged_batch[-1].right / 100.0)
		print ("max_right", cur_merged_batch[-1].right, max_right, x_pos_map.pos_map)

		for i in range(x_pos_map.max_x + 1, max_right + 1):
			x_pos_map.pos_map[i] = []

		if max_right > x_pos_map.max_x: 
			x_pos_map.max_x = max_right

		for batch in cur_merged_batch:
			left = math.ceil(batch.left / 100.0)
			right = math.ceil(batch.right / 100.0)
			print (batch.right)
			x_pos_map.pos_map[left].append(batch)
			x_pos_map.pos_map[right].append(batch)


def get_bounds_in_range(bound_of_next_batch, x_pos_map):
	bounds_in_range = list()
	for i in range(math.ceil(bound_of_next_batch.left / 100.0), math.ceil(bound_of_next_batch.right / 100.0) + 1):
		try:
			bounds_in_range += x_pos_map.pos_map[i]
		except KeyError: # In case the line above contains lesser words
			break
	return bounds_in_range


def merge_bounds(bounds):

	"""
	Grouping all bounds in a line into one batch
	"""

	rect_bottoms = list() # Contains rectangle bottom points
	for b in bounds:
		rect_bottoms.append(b.bottom)

	rect_bottoms = sorted(set(rect_bottoms)) # Sorting the rectangle bottoms in asc order

	bounds.sort(key=lambda x: x.top) # Sorting bounds on rectangle tops, to batch all tops less than a rect bottom

	rect_bot_counter, bounds_counter = 0, 0

	batched_bounds = list() # Contains bottom point and all the tops above it

	while rect_bot_counter < len(rect_bottoms) and bounds_counter < len(bounds):
		batches = list() # Batch of all tops less than a bottom
		while bounds_counter < len(bounds) and rect_bottoms[rect_bot_counter] >= bounds[bounds_counter].top:
			batches.append(bounds[bounds_counter])
			bounds_counter += 1
		if len(batches) > 0:
			batches.sort(key=lambda x: x.left)
			batched_bounds.append([rect_bottoms[rect_bot_counter], bounds[bounds_counter - 1].top, batches]) # Adding this to the list of batches of top
		rect_bot_counter += 1

	print ("\n\n", len(batched_bounds), "Batched bounds\n")
	for bound in batched_bounds:
		[b.print() for b in bound[2]]
		print ()

	# Merge fractions if present
	merged_batch_bounds = list()
	i = 0 
	while i < len(batched_bounds):
		cur_merged_batch = list()
		x_pos_map = XPosMap()
		cur_merged_batch += batched_bounds[i][2]
		update_x_pos_batches(x_pos_map, cur_merged_batch)
		j = i + 1
		while j < len(batched_bounds):
			next_batched_bounds = batched_bounds[j][2]

			first_bound_of_next_batch = next_batched_bounds[0]
			last_bound_of_next_batch = next_batched_bounds[-1]
			cur_batch_bounds_in_range_for_first_bound = get_bounds_in_range(first_bound_of_next_batch, x_pos_map)
			cur_batch_bounds_in_range_for_last_bound = get_bounds_in_range(last_bound_of_next_batch, x_pos_map) 

			print ("first_bound_of_next_batch")
			first_bound_of_next_batch.print()
			cur_batch_bounds_in_range_for_first_bound[0].print()

			print ("last_bound_of_next_batch")
			last_bound_of_next_batch.print()
			cur_batch_bounds_in_range_for_first_bound[-1].print()

			print (first_bound_of_next_batch.top - cur_batch_bounds_in_range_for_first_bound[0].bottom)

			if abs(first_bound_of_next_batch.top - cur_batch_bounds_in_range_for_first_bound[0].bottom) < VERTICAL_THRES and abs(last_bound_of_next_batch.top < cur_batch_bounds_in_range_for_last_bound[-1].bottom) < VERTICAL_THRES:
				cur_merged_batch += batched_bounds[j][2]
				update_x_pos_batches(x_pos_map, cur_merged_batch)
				j += 1
				i += 1
			else:
				break

		x_pos_map.print()
		if len(cur_merged_batch) > 0:
			merged_batch_bounds.append(cur_merged_batch)
		i += 1

	print ("\n\nMerged bounds\n")
	for bound in merged_batch_bounds:
		[b.print() for b in bound]
		print ()

	"""
	Ordering words within a line
	"""
	x_ordered_batches = list() # All groups of words within a line arranged in order of x
	for batched_bound in merged_batch_bounds:
		# batched_bound contains all words in a line
		batched_bound.sort(key=lambda x: x.left) # Sorting with word's starting position
		if len(batched_bound) == 1: # If there's only one word in the line, no need to anything else
			x_ordered_batches.append(batched_bound)
		else: # If there is more than 1 word
			# Merge words on the basis of y
			for i in range(len(batched_bound)):
				cur_batch = list()
				if not batched_bound[i].bound_merged:
					cur_batch.append(batched_bound[i])
					# Checking if there are words with top and bottom similar to i'th word and also check if they are consecutive
					for j in range(i + 1, len(batched_bound)):
						if not batched_bound[j].bound_merged and abs(cur_batch[-1].top - batched_bound[j].top) < VERTICAL_THRES and abs(cur_batch[-1].bottom - batched_bound[j].bottom) < VERTICAL_THRES and abs(cur_batch[-1].right - batched_bound[j].left) < HORIZ_THRES:
							batched_bound[j].bound_merged = True # Mark the word as visited
							cur_batch.append(batched_bound[j]) # Add it to current batch of words with similar top and bottom
				if len(cur_batch) > 0:
					x_ordered_batches.append(cur_batch) # Add the current batch to x_ordered_batches

	# Arrange overlapping groups of words in order of y (for fractions, to maintain order)
	# Numerator and denominator should already be grouped as one batch each
	# So just checking the consecutive batches should suffice because not more than two batches can overlap on x axis (numerator and denominator)
	x_y_ordered_batches = list()
	i = 0
	while i < len(x_ordered_batches) - 1:
		cur_batch_x_min = x_ordered_batches[i][0].left
		cur_batch_x_max = x_ordered_batches[i][-1].right
		next_batch_x_min = x_ordered_batches[i + 1][0].left
		next_batch_x_max = x_ordered_batches[i + 1][-1].right
		# Check if they overlap on X axis
		if (((next_batch_x_min - cur_batch_x_min) + (next_batch_x_max - cur_batch_x_max)) <= ((cur_batch_x_max - cur_batch_x_min) + (next_batch_x_max - next_batch_x_min))):
			# Lines do overlap, order these two batches on the basis of smallest top
			smallest_top_for_cur_batch = min([b.top for b in x_ordered_batches[i]])
			smallest_top_for_next_batch = min([b.top for b in x_ordered_batches[i + 1]])
			if smallest_top_for_next_batch < smallest_top_for_cur_batch: # These two batches need to be reversed
				x_y_ordered_batches.append(x_ordered_batches[i + 1])
				x_y_ordered_batches.append(x_ordered_batches[i])
			else: # Batches need not be reversed
				x_y_ordered_batches.append(x_ordered_batches[i])
				x_y_ordered_batches.append(x_ordered_batches[i + 1])
			i += 2 # Because, both numerator and denominator batches have been processed
		else: 
			x_y_ordered_batches.append(x_ordered_batches[i])
			i += 1 # No overlap, move on to the next word
		
		if (i == len(x_ordered_batches) - 1): # If only last batch is remaining
			x_y_ordered_batches.append(x_ordered_batches[i])

	final_output = []
	for batch in x_y_ordered_batches:
		for b in batch:
			final_output.append(b.word)

	print ("\nFinal Output\n")
	print (" ".join(final_output))
			
if __name__=='__main__':
	import sys
	import re
	csv_format_regex = re.compile(r'(.*?)(([,]\d+){4})')
	f = open(sys.argv[1], 'r')
	bounds = list()
	for l in f.readlines():
		matches = csv_format_regex.match(l)
		rect_bounds = [int(i) for i in matches.group(2)[1:].split(',')]
		bounds.append(Bound(matches.group(1), rect_bounds[0], rect_bounds[1], rect_bounds[2], rect_bounds[3]))
	merge_bounds(bounds)

