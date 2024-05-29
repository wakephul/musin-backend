import nest
nest.set_verbosity('M_ERROR')

import os
from api.src.nest.output.rates import calculate_bins
from api.src.managers import file_handling
from api.src.nest.plots.generate import moving_average_plot
from api.utils import cdf
from api.src.managers.images.edit import merge_plots

def postprocessing(results, test_types, train_time, test_time, test_number, output_folder):
    senders_spike_monitor_DCN_a = nest.GetStatus(results["spike_monitor_DCN_a"], 'events')[0]['senders']
    times_spike_monitor_DCN_a = nest.GetStatus(results["spike_monitor_DCN_a"], 'events')[0]['times']
    senders_spike_monitor_DCN_b = nest.GetStatus(results["spike_monitor_DCN_b"], 'events')[0]['senders']
    times_spike_monitor_DCN_b = nest.GetStatus(results["spike_monitor_DCN_b"], 'events')[0]['times']

    bin_size = 5
    
    times_spike_monitor_DCN_a = [t for t in times_spike_monitor_DCN_a if t > train_time]
    times_spike_monitor_DCN_b = [t for t in times_spike_monitor_DCN_b if t > train_time]
    bin_rates_DCN_complete_a = calculate_bins(senders_spike_monitor_DCN_a, times_spike_monitor_DCN_a, len(results["idx_monitored_neurons_DCN_a"])//2, bin_size, train_time, train_time+(test_time*test_number), test_number)
    bin_rates_DCN_complete_b = calculate_bins(senders_spike_monitor_DCN_b, times_spike_monitor_DCN_b, len(results["idx_monitored_neurons_DCN_a"])//2, bin_size, train_time, train_time+(test_time*test_number), test_number)

    cdf_plots = []
    
    for tt_index, tt in enumerate(test_types):
        bin_rates_a_portion = bin_rates_DCN_complete_a[tt_index]
        bin_rates_b_portion = bin_rates_DCN_complete_b[tt_index]
        os.makedirs(output_folder+'files', exist_ok=True)
        json_title_a = file_handling.dict_to_json(bin_rates_a_portion, output_folder+'files/bin_rates_DCN_a_test_'+str(tt_index))
        json_title_b = file_handling.dict_to_json(bin_rates_b_portion, output_folder+'files/bin_rates_DCN_b_test_'+str(tt_index))

        moving_average_plot(bin_rates_a_portion, output_folder, 'ma_rates_DCN_a_test_'+str(tt_index), (train_time+(test_time*tt_index), train_time+test_time+(test_time*tt_index)))

        cdf.calculate([json_title_a, json_title_b], output_folder, 'cdf_test_'+str(tt_index), 5, 'save')

        # ma_plots.append(['ma_rates_DCN_a', 'ma_rates', 'test'])
        cdf_plots.append(['cdf', 'cdf', 'test'])
    
    merge_plots(output_folder, cdf_plots, 'cdf_plots', len(test_types))

    # create_folder(output_folder+'multimeters')
    # create_folder(output_folder+'spike_detectors')
    # multimeters_merge(output_folder+'multimeters/')
    # spike_detectors_merge(output_folder+'spike_detectors/')

    # # monitors = ['spike_monitor_DCN_a', 'spike_monitor_DCN_b']
    # # monitored_populations = ['idx_monitored_neurons_DCN_a', 'idx_monitored_neurons_DCN_b']

    # # rates = calculate_average_rate(simulation_results=simulation_results, max_time=test_time*test_number, monitors=monitors, monitored_populations=monitored_populations)

    # # file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nRates: " + ', '.join(map(str, zip(monitors, rates))))
    # file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nExecution: " + json.dumps(execution))
    