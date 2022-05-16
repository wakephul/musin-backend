import itertools
def combinations_generator(spikes_values):
    keys, values = zip(*spikes_values.items())
    combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    return combinations