import itertools
def combinations_generator(values):
    _keys, _values = zip(*values.items())
    combinations = [dict(zip(_keys, v)) for v in itertools.product(*_values)]
    return combinations