def human_format(num, sign=False):
    prefix = ''

    if sign:
        if num > 0:
            prefix = '+'

    formatted = None
    if len(str(num)) <= 4:
        formatted = '{:,d}'.format(num)
    else:
        num = float('{:.4g}'.format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0

        formatted = '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

    return prefix + formatted


def runescape_number_to_int(number):
    if isinstance(number, int):
        return number

    multiplier = 1
    number = number.replace('+', '')
    number = number.replace(',', '')
    if '-' in number:
        multiplier = -1
        number = number.replace('-', '')

    if 'k' in number:
        return int(float(number.replace('k', '')) * 10 ** 3) * multiplier

    if 'm' in number:
        return int(float(number.replace('m', '')) * 10 ** 6) * multiplier

    if 'b' in number:
        return int(float(number.replace('b', '')) * 10 ** 9) * multiplier

    return int(number) * multiplier
