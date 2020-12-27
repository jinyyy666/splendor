def greater_than_or_equal_to(left, right):
    for k, v in right.items():
        if k not in left or v > left[k]:
            return False
    return True