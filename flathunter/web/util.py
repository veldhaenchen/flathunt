import re
import numbers

def sanitize_float(f):
    if isinstance(f, numbers.Number):
        return float(f)
    digits = re.match(r'\d+', f)
    if digits is None:
        return None
    return float(digits[0])
