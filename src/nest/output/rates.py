import nest
import numpy as np

def calculate_bins(senders, times, number_monitored_neurons, bin_size = 5, max_time = 1000):
    # if (not senders or not times): return {}

    # * penso che dovrebbe funzionare al contrario, ovvero dovrei assegnare l'elenco degli id a ciascun tempo
    # * in questo modo potrei dividerli già sulla base dei bin (forse), oppure calcolare e poi proseguire con il calcolo
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
    
    # * qui fondamentalmente ho un elenco di tutti gli spari che si vedono in ciascun bin
    # * il problema è che ci sono un sacco di duplicati in ciascun bin, cioè mi pare che la frequenza sia un po' alta se ogni neurone spara 2 o 3 volte ogni 5ms

    bin_rates = {}
    for bin_time, spikes_list in monitored_times.items():
        bin_rate = len(spikes_list) * 1000 / (bin_size * number_monitored_neurons)
        bin_rates[bin_time] = bin_rate
        # print(f'rate nel bin {bin_time}: {bin_rate} Hz')

    print('bin_rates', bin_rates)

    return bin_rates

def calculate_average_rate(simulation_results = [], max_time = 1000):

    if (not simulation_results): return None, None

    events_A = nest.GetStatus(simulation_results["spike_monitor_A"], "n_events")[0]
    events_B = nest.GetStatus(simulation_results["spike_monitor_B"], "n_events")[0]

    rate_A = events_A / max_time * 1000.0 / len(simulation_results["idx_monitored_neurons_A"])
    rate_B = events_B / max_time * 1000.0 / len(simulation_results["idx_monitored_neurons_B"])

    return rate_A, rate_B