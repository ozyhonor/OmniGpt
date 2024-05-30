import re

def is_hex_color(color):
    pattern = re.compile(r'^[a-fA-F0-9]{8}$')
    if pattern.match(color) is not None:
        return True
    elif len(color) == 6:
        pattern = re.compile(r'^[a-fA-F0-9]{6}$')
        return pattern.match(color) is not None
    else:
        return False