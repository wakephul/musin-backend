import ast, re
from typing import Any, List

_num_re = re.compile(r"^\s*-?\d+(?:\.\d+)?\s*$")

def coerce_numbers(obj):
    if isinstance(obj, str) and re.fullmatch(r"\s*\d+\s*", obj):
        return int(obj.strip())
    if isinstance(obj, (int, float)):
        return int(obj)
    if isinstance(obj, (list, tuple)):
        return [coerce_numbers(el) for el in obj]
    return obj
        
def safe_int(value, *, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _to_float(x):
    """Convert numeric strings to float, leave others untouched."""
    if isinstance(x, str) and _num_re.match(x):
        return float(x)
    return x

def normalize_param_value(val):
    """
    • '[1,2]'  →  [1.0, 2.0]
    • '1.5'    →  1.5
    • 'foo'    →  'foo'
    • lists/tuples are processed element-wise
    """
    if isinstance(val, str):
        s = val.strip()
        if s.startswith('[') and s.endswith(']'):
            try:
                parsed = ast.literal_eval(s)
                return [_to_float(v) for v in parsed]
            except Exception:
                pass
        return _to_float(s)

    if isinstance(val, (list, tuple)):
        return [_to_float(v) for v in val]

    return 

def parse_test_types(raw_test_types):
    if isinstance(raw_test_types, (list, tuple)):
        test_types = list(raw_test_types)

    elif isinstance(raw_test_types, str):
        s = raw_test_types.strip()
        if s.startswith('['):
            test_types = ast.literal_eval(s)
        elif ',' in s:
            test_types = [seg for seg in s.split(',') if seg.strip()]
        else:
            test_types = [s]
    else:
        test_types = [raw_test_types]

    test_types = coerce_numbers(test_types)
    
    return test_types