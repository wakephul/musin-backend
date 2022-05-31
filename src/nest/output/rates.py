import pdb
import nest
import numpy as np

def calculate_bins(senders, times, number_monitored_neurons, bin_size = 5, max_time = 1000, threshold_rate = 100):

    print("Calculating rates divided into bins")
    bins = list(range(bin_size, max_time+1, bin_size))
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

    bin_rates_complete = {}
    for bin_time in bins:
        if bin_time in monitored_times:
            bin_rate = len(monitored_times[bin_time]) * 1000 / (bin_size * number_monitored_neurons)
            bin_rates_complete[bin_time] = bin_rate
        else:
            bin_rates_complete[bin_time] = 0

        # print(f'rate nel bin {bin_time}: {bin_rate} Hz')

    # print('bin_rates', bin_rates)

    return bin_rates_complete

def calculate_average_rate(simulation_results = [], max_time = 1000):

    if (not simulation_results): return None, None

    events_A = nest.GetStatus(simulation_results["spike_monitor_A"], "n_events")[0]
    events_B = nest.GetStatus(simulation_results["spike_monitor_B"], "n_events")[0]

    rate_A = events_A / max_time * 1000.0 / len(simulation_results["idx_monitored_neurons_A"])
    rate_B = events_B / max_time * 1000.0 / len(simulation_results["idx_monitored_neurons_B"])

    return rate_A, rate_B

def calculate_response_times(values, threshold, trial_time, bin_size):
    elements_for_trial = trial_time/bin_size
    values_into_trials = divide_into_trials(values, elements_for_trial)
    response_times = []
    print(values_into_trials)
    for values_index, trial_values in enumerate(values_into_trials):
        time_ids = [time_id for time_id, value in enumerate(trial_values) if value >= threshold]
        if len(time_ids):
            first_time_id = time_ids[0]
            print(first_time_id)
            actual_time = (values_index*trial_time)+(first_time_id*bin_size)
            response_times.append(actual_time)
    return response_times

def divide_into_trials(seq, size):
    return [seq[int(pos):(int(pos) + int(size))] for pos in range(0, len(seq), int(size))]