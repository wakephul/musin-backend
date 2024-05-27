def manage_results(simulation_results):
    if not simulation_results:
        return False
    
    #if they are paired, then they will be put on the same side at each trial. If they are not paired, they will be put on random sides          
    #         # plots_to_create = plots_config[network] if (network in plots_config) else None
    #         # if plots_to_create:
    #         #     generate_plots(plots_to_create, output_folder, simulation_results, train_time=train_time, test_time=test_time, test_number=test_number, train=simulation_results["train"], test=simulation_results["test"], sides=trials_side)

    #         # plots_to_merge = plots_merge_config[network] if (network in plots_merge_config) else None
            
    #         #TO DISCUSS: questo è tutto hardcodato, probabilmente avrebbe senso avere un file "extra" per ciascuna rete, in cui si definisce il preprocessing e il postprocessing
    #         # senders_spike_monitor_A = nest.GetStatus(simulation_results["spike_monitor_A"], 'events')[0]['senders']
    #         # times_spike_monitor_A = nest.GetStatus(simulation_results["spike_monitor_A"], 'events')[0]['times']
    #         # senders_spike_monitor_B = nest.GetStatus(simulation_results["spike_monitor_B"], 'events')[0]['senders']
    #         # times_spike_monitor_B = nest.GetStatus(simulation_results["spike_monitor_B"], 'events')[0]['times']

    #         # bin_size = 5
            
    #         # bin_rates_A_complete = calculate_bins(senders_spike_monitor_A, times_spike_monitor_A, len(simulation_results["idx_monitored_neurons_A"]), bin_size, train_time, train_time+(test_time*test_number), test_number)
    #         # bin_rates_B_complete = calculate_bins(senders_spike_monitor_B, times_spike_monitor_B, len(simulation_results["idx_monitored_neurons_B"]), bin_size, train_time, train_time+(test_time*test_number), test_number)


    #         # for tt_index, tt in enumerate(test_types):
    #         #     bin_rates_a_portion = bin_rates_A_complete[tt_index]
    #         #     bin_rates_b_portion = bin_rates_B_complete[tt_index]
    #         #     json_title_a = file_handling.dict_to_json(bin_rates_a_portion, output_folder+'bin_rates_A_test_'+str(tt_index))
    #         #     json_title_b = file_handling.dict_to_json(bin_rates_b_portion, output_folder+'bin_rates_B_test_'+str(tt_index))
    
    return simulation_results