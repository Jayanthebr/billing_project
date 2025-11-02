# def compute_change(balance, denominations):
#     """
#     Compute how many notes/coins to return for a given balance amount
#     based on available denominations.
#     denominations: list of dicts like [{'value': 2000, 'count': 50}, ...]
#     Returns: list of dicts with denomination value and count used.
#     """
#     remaining = balance
#     result = []

#     for denom in sorted(denominations, key=lambda x: x['value'], reverse=True):
#         if remaining <= 0:
#             break
#         num_notes = min(remaining // denom['value'], denom['count'])
#         if num_notes > 0:
#             result.append({
#                 'value': denom['value'],
#                 'count': int(num_notes)
#             })
#             remaining -= denom['value'] * num_notes

#     if remaining > 0:
#         result.append({'value': 'Unavailable', 'count': float(remaining)})

#     return result
def compute_change(balance, denominations):
    """
    Compute how many notes/coins to return for a given balance amount
    based on available denominations.
    denominations: list of tuples like [(2000, 50), (500, 50), ...]
    Returns:
      used: list of dicts with denomination value and count used
      remaining: float, remaining amount if exact change not possible
      insufficient: bool, True if not enough denominations
    """

    remaining = balance
    used = []

    # Sort denominations from highest to lowest
    for value, count in sorted(denominations, key=lambda x: x[0], reverse=True):
        if remaining <= 0:
            break

        # Find max number of notes we can use
        num_notes = min(remaining // value, count)

        if num_notes > 0:
            used.append({'value': value, 'count': int(num_notes)})
            remaining -= value * num_notes

    # If still some balance left that can't be made with available denominations
    insufficient = remaining > 0

    return used, remaining, insufficient
