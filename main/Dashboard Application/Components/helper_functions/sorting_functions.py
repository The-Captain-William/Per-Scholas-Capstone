def capture_min_max(input: list, interval: int, rounds:int, start_from_zero: bool = False):
    """
    Find the min and max given a list and an interval. 
    If start from zero is False, will start at interval and not zero
    """
    # O(N(Log(N)))
    if start_from_zero == True:
        start = interval
    mins = []
    maxs = []
    start = 0
    for index in range(start, (interval * rounds) + 1, interval):
        current_selection = input[start:index + 1]
        current_selection.sort()
        mins.append(current_selection[0])
        maxs.append(current_selection[-1])
        start = index
    return mins, maxs