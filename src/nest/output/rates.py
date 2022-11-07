import pdb
import nest
import numpy as np

def calculate_bins(senders, times, number_monitored_neurons, bin_size = 5, start_time = 5, end_time = 1000, split_into = 1):

    print("Calculating rates divided into bins")
    bins = list(range(int(start_time), int(end_time)+1, bin_size))

    monitored_times = {}

    for index, time in enumerate(times):
        bin_index = np.digitize(time, bins, right=True)
        if bin_index < len(bins):
            bin_time = np.take(bins, bin_index)
            if bin_time in monitored_times:
                monitored_times[bin_time].append(senders[index])
            else:
                monitored_times[bin_time] = [senders[index]]
    for id in monitored_times:
        monitored_times[id].sort()

    bin_rates = {}

    for bin_time in bins:
        if bin_time in monitored_times:
            bin_rate = len(monitored_times[bin_time]) * 1000 / (bin_size * number_monitored_neurons)
            bin_rates[bin_time] = bin_rate
        else:
            bin_rates[bin_time] = 0
        
    bin_rates_split = {i: [] for i in range(split_into)}

    step = int((end_time-start_time)/split_into)
    start = int(start_time)
    end = int(end_time)
    for index, value in enumerate(range(start, end, step)):
        bin_rates_split[index] = {k:v for k, v in bin_rates.items() if (k>=value and k<value+step)}

    return bin_rates_split

def calculate_average_rate(simulation_results = [], max_time = 1000, monitors = [], monitored_populations = []):

    if (not simulation_results): return None, None

    events = [nest.GetStatus(simulation_results[monitor], "n_events")[0] for monitor in monitors]

    rates = [events[i] / max_time * 1000.0 / len(simulation_results[monitored_populations[i]]) for i in range(len(monitors))]

    return rates

def calculate_response_times(values, threshold, trial_time, bin_size):
    elements_for_trial = trial_time/bin_size
    values_into_trials = divide_into_trials(values, elements_for_trial)
    response_times = []
    for values_index, trial_values in enumerate(values_into_trials):
        time_ids = [time_id for time_id, value in enumerate(trial_values) if value >= threshold]
        if len(time_ids):
            first_time_id = time_ids[0]
            actual_time = (values_index*trial_time)+(first_time_id*bin_size)
            response_times.append(actual_time)
        else:
            response_times.append(999999999)
    return response_times

def divide_into_trials(seq, size):
    return [seq[int(pos):(int(pos) + int(size))] for pos in range(0, len(seq), int(size))]