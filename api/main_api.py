import pdb

import nest
nest.set_verbosity('M_ERROR') #lo metto qui per evitare tutte le print
import sys
from src.connection.connect import create_connection, close_connection
from src.queries import spikes_queries, support_queries
from src.file_handling import file_handling

from src.nest.plots.generate import generate_plots, moving_average_plot
from src.nest.output.rates import calculate_average_rate, calculate_bins, calculate_response_times
from src.file_handling.support_file import new_row

from src.utils.dictionaries import merge_sort_dicts_of_lists
from src.utils.combinations import combinations_generator
from scripts.network_output_clean import network_output_clean

from src.nest.reset.reset import nest_reset
from importlib import import_module
from src.nest.spike_trains.edit import edit_spikes_for_simulation
from src.nest.spike_trains.generate import poisson_spikes_generator_parrot, spike_generator_from_times
from src.file_handling.folder_handling import create_folder

from src.nest.output.device_manager import multimeters_merge, spike_detectors_merge

from src.nest.plots.generate import moving_average_plot_no_save
from src.nest.output.rates import calculate_response_times
import json

def run(params):
    # CONFIGURATION FILE
    config = params['config'] if ('config' in params) else {}
    plots_config = params['plots_config'] if ('plots_config' in params) else {}
    network_config = params['networks_params'] if ('networks_params' in params) else {}
    execution_types = params['execution_types'] if ('execution_types' in params) else {}
    
    executions = config['executions'] if ('executions' in config) else {}

    print(params)
    print(config)
    print(executions)

    # config = file_handling.read_json('data/config/config.json')
    # plots_config = file_handling.read_json('data/config/plots_config.json')
    # network_config = file_handling.read_json('data/config/network_config.json')
    # execution_types = file_handling.read_json('data/config/execution_types.json')

    for execution in executions:
        merge_stimuli = True if ((not 'merge_stimuli' in execution) or ('merge_stimuli' in execution and execution['merge_stimuli'])) else False
        primary_networks_for_csv = '/'.join([n + '_DUPL' for n in execution['primary_networks']]) if not merge_stimuli else '/'.join(execution['primary_networks'])
        new_simulation_id = new_row(file_path='output/executions/executions.csv', data=[execution['name'], '/'.join(execution['types']), primary_networks_for_csv, '/'.join(execution['secondary_networks'])])
        current_simulations_folder = 'output/executions/'+str(new_simulation_id)+'/'
        create_folder(current_simulations_folder)
        
        execution_stimuli = {}

        for execution_type in execution['types']:
            execution_params = execution_types[execution_type]
            execution_stimuli[execution_type] = []
            if 'use_existent_spikes' in execution_params and not execution_params['use_existent_spikes']:
                spikes_params = execution_params['spikes']
                spikes_values = {}
                for spikes_params_key, spikes_params_info in spikes_params.items():
                    if 'single_value' in spikes_params_info and not spikes_params_info['single_value']:
                        # print('spikes_params_info', spikes_params_info)
                        spikes_values[spikes_params_key] = []
                        for value in range(int(spikes_params_info['first_value']*1000), int(spikes_params_info['last_value']*1000+spikes_params_info['increment']*1000), int(spikes_params_info['increment']*1000)):
                            spikes_values[spikes_params_key].append(float(value/1000))
                    else:
                        spikes_values[spikes_params_key] = [spikes_params_info['value']]
                
            # else: qui andrà effettivamente il codice per usare un file di spikes già esistente (passato in input)
                # spikes_A_times = file_handling.file_open(spikes_A)
                # spikes_B_times = file_handling.file_open(spikes_B)
                # spikes_A = spike_generator_from_times(spikes_A_times)
                # spikes_B = spike_generator_from_times(spikes_B_times)

            spikes_combinations = combinations_generator(spikes_values)
            # pdb.set_trace()

            for combination in spikes_combinations:
                # print('combination: ', combination)
                rate = combination['rate']
                start = combination['first_spike_latency']
                number_of_neurons = combination['number_of_neurons']
                trial_duration = stop = combination['trial_duration']
                # print(rate, start, stop, number_of_neurons, trial_duration)
                spikes_A_times = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)
                nest_reset(3232) # altrimenti l'rng genera tempi uguali
                spikes_B_times = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)
                nest_reset(1214)
                execution_stimuli[execution_type].append({'info': 'rate='+str(rate)+'&start='+str(start)+'&number_of_neurons='+str(number_of_neurons)+'&trial_duration='+str(trial_duration), 'A': spikes_A_times, 'B': spikes_B_times})

        # print('stimuli:', execution_stimuli)
        duplicate_primary_network = False
        input_stimuli_A = {'cortex_1': {'info': [], 'stimuli': []}, 'cortex_2': {'info': [], 'stimuli': []}}
        input_stimuli_B = {'cortex_1': {'info': [], 'stimuli': []}, 'cortex_2': {'info': [], 'stimuli': []}}

        if(len(execution['types']) > 1):
            for ex_type_1 in execution_stimuli[execution['types'][0]]:
                for ex_type_2 in execution_stimuli[execution['types'][1]]:
                    if merge_stimuli:
                        spikes_A_times_merged = merge_sort_dicts_of_lists(ex_type_1['A'], ex_type_2['A'])
                        input_stimuli_A['cortex_1']['info'].append(execution['types'][0]+'_'+ex_type_1['info']+'+'+execution['types'][1]+'_'+ex_type_2['info'])
                        input_stimuli_A['cortex_1']['stimuli'].append(spikes_A_times_merged)
                        
                        spikes_B_times_merged = merge_sort_dicts_of_lists(ex_type_1['B'], ex_type_2['B'])
                        input_stimuli_B['cortex_1']['info'].append(execution['types'][0]+'_'+ex_type_1['info']+'+'+execution['types'][1]+'_'+ex_type_2['info'])
                        input_stimuli_B['cortex_1']['stimuli'].append(spikes_B_times_merged)
                    else:
                        print('Multiple stimuli, won\'t be merged: another cortex will be added')
                        input_stimuli_A['cortex_1']['info'].append(execution['types'][0]+'_'+ex_type_1['info'])
                        input_stimuli_A['cortex_1']['stimuli'].append(ex_type_1['A'])
                        input_stimuli_A['cortex_2']['info'].append(execution['types'][1]+'_'+ex_type_2['info'])
                        input_stimuli_A['cortex_2']['stimuli'].append(ex_type_2['A'])

                        input_stimuli_B['cortex_1']['info'].append(execution['types'][1]+'_'+ex_type_2['info'])
                        input_stimuli_B['cortex_1']['stimuli'].append(ex_type_1['B'])
                        input_stimuli_B['cortex_2']['info'].append(execution['types'][1]+'_'+ex_type_2['info'])
                        input_stimuli_B['cortex_2']['stimuli'].append(ex_type_2['B'])
                        duplicate_primary_network = True
        else:
            for x in execution_stimuli[execution['types'][0]]:
                input_stimuli_A['cortex_1']['info'].append(x['info'])
                input_stimuli_A['cortex_1']['stimuli'].append(x['A'])
                input_stimuli_B['cortex_1']['info'].append(x['info'])
                input_stimuli_B['cortex_1']['stimuli'].append(x['B'])
        
        # pdb.set_trace()
        new_row(file_path=current_simulations_folder+'simulations.csv', heading=['id','spikes_info','firing_rate_extern','rate_A','rate_B'])
        current_simulation_folder = current_simulations_folder+'simulations/'
        create_folder(current_simulation_folder)
        current_simulation_id = 1 # parto da 1 così è allineato con l'ID nel CSV
        nest_reset()


        if len(execution['primary_networks']):
            for network in execution['primary_networks']:
                # print('network:', network)
                network_module = import_module('src.nest.networks.'+network)
                network_params = file_handling.read_json('data/config/networks/primary/'+network+'.json')
                network_config_params = network_config[network] if (network in network_config) else None
                # pdb.set_trace()
                if network_config_params:
                    # TODO: gestire in automatico i diversi parametri
                    firing_rate_extern = network_config_params['firing_rate_extern']
                    for fre in range(int(firing_rate_extern['first_value']*1000), int(firing_rate_extern['last_value']*1000+firing_rate_extern['increment']*1000), int(firing_rate_extern['increment']*1000)):
                        network_params['firing_rate_extern'] = float(fre/1000)
                        if ((len(execution['types']) > 1) and merge_stimuli) or len(execution['types']) == 1: # in questo caso usiamo una sola corteccia
                            for stim, stim_info in zip(list(zip(input_stimuli_A['cortex_1']['stimuli'], input_stimuli_B['cortex_1']['stimuli'])), input_stimuli_A['cortex_1']['info']):

                                nest_reset(1111)
                                network_output_clean()

                                output_folder = current_simulation_folder+str(current_simulation_id)+'/'
                                create_folder(output_folder)
                                create_folder(output_folder+'spikes')
                                current_simulation_id += 1

                                spikes_A = spike_generator_from_times(stim[0])
                                spikes_B = spike_generator_from_times(stim[1])

                                spikes_A_file_name = file_handling.save_to_file(stim[0], output_folder+'spikes/spikes_A')
                                spikes_B_file_name = file_handling.save_to_file(stim[1], output_folder+'spikes/spikes_B')
                                
                                file_handling.append_to_file(output_folder+'simulation_notes.txt', '\nExecution name:'+execution['name'])
                                file_handling.append_to_file(output_folder+'simulation_notes.txt', '\nExecution types:'+'/'.join(execution['types'])+'\n')

                                trials_side_to_string = edit_spikes_for_simulation([spikes_A, spikes_B], (float(network_params['t_stimulus_duration']) - float(network_params['t_stimulus_start'])), float(network_params['sim_time']))
                                file_handling.append_to_file(output_folder+'simulation_notes.txt', trials_side_to_string)

                                # current_simulation = [spikes_A_file_name, spikes_B_file_name]+[str(exec[0])]
                                current_simulation = [stim_info]

                                current_simulation.append(str(fre/1000))

                                network_params['imported_stimulus_A'] = spikes_A
                                network_params['imported_stimulus_B'] = spikes_B
                                
                                simulation_results = network_module.run(network_params)
                                # print("RESULTS", simulation_results)

                                # ! TODO: eguagliare i vari assi dei grafici per poterli comparare
                                
                                plots_to_create = plots_config[network]

                                max_time = int(network_params['sim_time'])

                                generate_plots(plots_to_create, output_folder, simulation_results, max_time)
                                
                                senders_spike_monitor_A = nest.GetStatus(simulation_results["spike_monitor_A"], 'events')[0]['senders']
                                times_spike_monitor_A = nest.GetStatus(simulation_results["spike_monitor_A"], 'events')[0]['times']
                                senders_spike_monitor_B = nest.GetStatus(simulation_results["spike_monitor_B"], 'events')[0]['senders']
                                times_spike_monitor_B = nest.GetStatus(simulation_results["spike_monitor_B"], 'events')[0]['times']
                                
                                bin_rates_A = calculate_bins(senders_spike_monitor_A, times_spike_monitor_A, len(simulation_results["idx_monitored_neurons_A"]), 5, max_time)
                                bin_rates_B = calculate_bins(senders_spike_monitor_B, times_spike_monitor_B, len(simulation_results["idx_monitored_neurons_B"]), 5, max_time)

                                file_handling.dict_to_json(bin_rates_A, output_folder+'bin_rates_A')
                                file_handling.dict_to_json(bin_rates_B, output_folder+'bin_rates_B')

                                rate_A, rate_B = calculate_average_rate(simulation_results, max_time)

                                file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nSpikes rate: {str(stim_info)} Hz")
                                file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nFiring rate extern: {str(float(fre/1000))} Hz")

                                file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nPopulation A rate: {rate_A} Hz")
                                file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nPopulation B rate: {rate_B} Hz")

                                current_simulation.append(rate_A)
                                current_simulation.append(rate_B)
                                new_row('', current_simulations_folder+'simulations.csv', current_simulation)
                            
                        else: # qui abbiamo doppia corteccia, devo duplicare l'esecuzione
                            pass
                
                else:
                    number_of_cortex = 1 if (((len(execution['types']) > 1) and merge_stimuli) or len(execution['types']) == 1) else 2
                    for cortex_id in range(1, (number_of_cortex+1)):
                        current_cortex_value = 'cortex_'+str(cortex_id)
                        print('CORTEX ID: ', current_cortex_value)
                        current_cortex_folder = current_simulation_folder+current_cortex_value+'/'
                        create_folder(current_cortex_folder)
                        for stim, stim_info in zip(list(zip(input_stimuli_A[current_cortex_value]['stimuli'], input_stimuli_B[current_cortex_value]['stimuli'])), input_stimuli_A[current_cortex_value]['info']):

                            nest_reset(12345)
                            network_output_clean()

                            output_folder = current_cortex_folder+str(current_simulation_id)+'/'
                            create_folder(output_folder)
                            create_folder(output_folder+'spikes')
                            current_simulation_id += 1

                            spikes_A = spike_generator_from_times(stim[0])
                            spikes_B = spike_generator_from_times(stim[1])

                            spikes_A_file_name = file_handling.save_to_file(stim[0], output_folder+'spikes/spikes_A')
                            spikes_B_file_name = file_handling.save_to_file(stim[1], output_folder+'spikes/spikes_B')
                            
                            file_handling.append_to_file(output_folder+'simulation_notes.txt', '\nExecution name:'+execution['name'])
                            file_handling.append_to_file(output_folder+'simulation_notes.txt', '\nExecution types:'+'/'.join(execution['types'])+'\n')

                            
                            trials_side_to_string = edit_spikes_for_simulation([spikes_A, spikes_B], (float(network_params['t_stimulus_duration']) - float(network_params['t_stimulus_start'])), float(network_params['sim_time']))
                            file_handling.append_to_file(output_folder+'simulation_notes.txt', trials_side_to_string)

                            # current_simulation = [spikes_A_file_name, spikes_B_file_name]+[str(exec[0])]
                            current_simulation = [stim_info]

                            current_simulation.append('NONE')

                            network_params['imported_stimulus_A'] = spikes_A
                            network_params['imported_stimulus_B'] = spikes_B
                            sim_time_old = network_params['sim_time']
                            network_params['sim_time'] = max_time = int(network_params['sim_time'])*3

                            simulation_results = network_module.run(network_params)
                            
                            plots_to_create = plots_config[network] if (network in plots_config) else None
                            if plots_to_create:
                                generate_plots(plots_to_create, output_folder, simulation_results, max_time)
                            # create_folder(output_folder+'/plots')
                            
                            senders_spike_monitor_A = nest.GetStatus(simulation_results["spike_monitor_A"], 'events')[0]['senders']
                            times_spike_monitor_A = nest.GetStatus(simulation_results["spike_monitor_A"], 'events')[0]['times']
                            senders_spike_monitor_B = nest.GetStatus(simulation_results["spike_monitor_B"], 'events')[0]['senders']
                            times_spike_monitor_B = nest.GetStatus(simulation_results["spike_monitor_B"], 'events')[0]['times']

                            bin_size = 5
                            
                            bin_rates_A_complete = calculate_bins(senders_spike_monitor_A, times_spike_monitor_A, len(simulation_results["idx_monitored_neurons_A"]), bin_size, max_time, 100)
                            bin_rates_B_complete = calculate_bins(senders_spike_monitor_B, times_spike_monitor_B, len(simulation_results["idx_monitored_neurons_B"]), bin_size, max_time, 100)

                            file_handling.dict_to_json(bin_rates_A_complete, output_folder+'bin_rates_A_complete')
                            file_handling.dict_to_json(bin_rates_B_complete, output_folder+'bin_rates_B_complete')

                            ma_rates_A = moving_average_plot(bin_rates_A_complete, output_folder+'plots/', 'ma_rates_A')
                            ma_rates_B = moving_average_plot(bin_rates_B_complete, output_folder+'plots/', 'ma_rates_B')

                            trial_time = float(network_params['t_stimulus_duration'])*3

                            # th = 15
                            # response_times = []
                            # response_times_A = calculate_response_times(ma_rates_A, th, trial_time, bin_size)
                            # file_handling.append_to_file(output_folder+'simulation_notes.txt', "\nResponse times A "+"th "+str(th)+": "+",".join(map(str, response_times_A)))
                            # for rt in response_times_A:
                            #     response_times.append(rt%1000)
                            
                            # response_times_B = calculate_response_times(ma_rates_B, th, trial_time, bin_size)
                            # file_handling.append_to_file(output_folder+'simulation_notes.txt', "\nResponse times B "+"th "+str(th)+": "+",".join(map(str, response_times_B)))
                            # for rt in response_times_B:
                            #     response_times.append(rt%1000)

                            # response_times_dict = {'response_times': response_times}
                            # file_handling.dict_to_json(response_times_dict, output_folder+'response_times')

                            # file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nTimes over threshold A: {','.join(map(str, times_over_threshold_A))}")
                            # file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nTimes over threshold B: {','.join(map(str, times_over_threshold_B))}")

                            # file_handling.dict_to_json(ma_rates_A, output_folder+'ma_rates_A')
                            # file_handling.dict_to_json(ma_rates_B, output_folder+'ma_rates_B')

                            # create_folder(output_folder+'multimeters')
                            # create_folder(output_folder+'spike_detectors')
                            # multimeters_merge(output_folder+'multimeters/')
                            # spike_detectors_merge(output_folder+'spike_detectors/')

                            # monitors = ['spike_monitor_A', 'spike_monitor_B']
                            # monitored_populations = ['idx_monitored_neurons_A', 'idx_monitored_neurons_B']
                            # rates = calculate_average_rate(simulation_results, max_time, monitors, monitored_populations)


                            file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nStimulus info: {str(stim_info)} Hz")
                            file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nFiring rate extern: not in this case")

                            # file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nRates: " + ', '.join(map(str, zip(monitors, rates))))

                            # current_simulation.append(rates[0])
                            # current_simulation.append(rates[1])
                            new_row('', current_simulations_folder+'simulations.csv', current_simulation)
                            network_params['sim_time'] = sim_time_old
        
        if (len(execution['types']) > 1) and len(execution['secondary_networks']):
            for network in execution['secondary_networks']:
                print('secondary network:', network)
                network_module = import_module('src.nest.networks.'+network)
                network_params = file_handling.read_json('data/config/networks/secondary/'+network+'.json')\
                
                current_network_folder = current_simulation_folder+'/'+network+'/'
                create_folder(current_network_folder)

                nest_reset(12345)
                network_output_clean()

                output_folder = current_network_folder+str(current_simulation_id)+'/'
                create_folder(output_folder)
                create_folder(output_folder+'spikes')
                current_simulation_id += 1

                spikes_type_1_A = spike_generator_from_times(input_stimuli_A['cortex_1']['stimuli'][0])
                spikes_type_2_A = spike_generator_from_times(input_stimuli_A['cortex_2']['stimuli'][0])
                spikes_type_1_B = spike_generator_from_times(input_stimuli_B['cortex_1']['stimuli'][0])
                spikes_type_2_B = spike_generator_from_times(input_stimuli_B['cortex_2']['stimuli'][0])

                current_simulation = [network]

                edit_spikes_for_simulation([spikes_type_1_A, spikes_type_1_B], (float(network_params['t_stimulus_duration']) - float(network_params['t_stimulus_start'])), float(network_params['sim_time']))
                edit_spikes_for_simulation([spikes_type_2_A, spikes_type_2_B], (float(network_params['t_stimulus_duration']) - float(network_params['t_stimulus_start'])), float(network_params['sim_time']))

                network_params['imported_stimulus_A'] = {'type_1': spikes_type_1_A, 'type_2': spikes_type_2_A}
                network_params['imported_stimulus_B'] = {'type_1': spikes_type_1_B, 'type_2': spikes_type_2_B}
                sim_time_old = network_params['sim_time']
                network_params['sim_time'] = max_time = int(network_params['sim_time'])*3

                simulation_results = network_module.run(network_params)
                
                plots_to_create = plots_config[network] if (network in plots_config) else None
                if plots_to_create:
                    generate_plots(plots_to_create, output_folder, simulation_results, max_time)
                
                senders_spike_monitor_GR = nest.GetStatus(simulation_results["spike_monitor_GR"], 'events')[0]['senders']
                times_spike_monitor_GR = nest.GetStatus(simulation_results["spike_monitor_GR"], 'events')[0]['times']
                senders_spike_monitor_PC = nest.GetStatus(simulation_results["spike_monitor_PC"], 'events')[0]['senders']
                times_spike_monitor_PC = nest.GetStatus(simulation_results["spike_monitor_PC"], 'events')[0]['times']
                senders_spike_monitor_IO = nest.GetStatus(simulation_results["spike_monitor_IO"], 'events')[0]['senders']
                times_spike_monitor_IO = nest.GetStatus(simulation_results["spike_monitor_IO"], 'events')[0]['times']
                senders_spike_monitor_DCN = nest.GetStatus(simulation_results["spike_monitor_DCN"], 'events')[0]['senders']
                times_spike_monitor_DCN = nest.GetStatus(simulation_results["spike_monitor_DCN"], 'events')[0]['times']

                bin_size = 5
                
                bin_rates_GR_complete = calculate_bins(senders_spike_monitor_GR, times_spike_monitor_GR, len(simulation_results["idx_monitored_neurons_GR"]), bin_size, max_time, 100)
                bin_rates_PC_complete = calculate_bins(senders_spike_monitor_PC, times_spike_monitor_PC, len(simulation_results["idx_monitored_neurons_PC"]), bin_size, max_time, 100)
                bin_rates_IO_complete = calculate_bins(senders_spike_monitor_PC, times_spike_monitor_IO, len(simulation_results["idx_monitored_neurons_IO"]), bin_size, max_time, 100)
                bin_rates_DCN_complete = calculate_bins(senders_spike_monitor_PC, times_spike_monitor_DCN, len(simulation_results["idx_monitored_neurons_DCN"]), bin_size, max_time, 100)

                file_handling.dict_to_json(bin_rates_GR_complete, output_folder+'bin_rates_GR_complete')
                file_handling.dict_to_json(bin_rates_PC_complete, output_folder+'bin_rates_PC_complete')
                file_handling.dict_to_json(bin_rates_IO_complete, output_folder+'bin_rates_IO_complete')
                file_handling.dict_to_json(bin_rates_DCN_complete, output_folder+'bin_rates_DCN_complete')

                ma_rates_GR = moving_average_plot(bin_rates_GR_complete, output_folder+'plots/', 'ma_rates_GR')
                ma_rates_PC = moving_average_plot(bin_rates_PC_complete, output_folder+'plots/', 'ma_rates_PC')
                ma_rates_IO = moving_average_plot(bin_rates_IO_complete, output_folder+'plots/', 'ma_rates_IO')
                ma_rates_DCN = moving_average_plot(bin_rates_DCN_complete, output_folder+'plots/', 'ma_rates_DCN')

                create_folder(output_folder+'multimeters')
                create_folder(output_folder+'spike_detectors')
                multimeters_merge(output_folder+'multimeters/')
                spike_detectors_merge(output_folder+'spike_detectors/')

                monitors = ['spike_monitor_GR', 'spike_monitor_PC', 'spike_monitor_IO', 'spike_monitor_DCN']
                monitored_populations = ['idx_monitored_neurons_GR', 'idx_monitored_neurons_PC', 'idx_monitored_neurons_IO', 'idx_monitored_neurons_DCN']
                rates = calculate_average_rate(simulation_results, max_time, monitors, monitored_populations)

                file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nRates: " + ', '.join(map(str, zip(monitors, rates))))

                new_row('', current_simulations_folder+'simulations.csv', current_simulation)
                network_params['sim_time'] = sim_time_old
    

def calculate_cdf():
    with open('output/executions/259/simulations/cerebellum_simple/1/bin_rates_DCN_complete.json', 'r') as j:
        bin_rates = json.loads(j.read())

    ma_rates = moving_average_plot_no_save(bin_rates)

    trial_time = 3000
    bin_size = 5

    # print('MA RATES: ', ma_rates)

    th = 0.1
    response_times = []
    resp = calculate_response_times(ma_rates, th, trial_time, bin_size)
    for rt in resp:
        response_times.append(rt%1000)

    print('RESPONSE TIMES: ', response_times)

    # CDF plot for spike times
    import numpy as np
    import matplotlib.pyplot as plt

    def cdf_calc(data):
        count, bins_count = np.histogram(data, bins=10)
        try:
            print(count, sum(count))
            pdf = count / sum(count)
        except:
            pdf = 0
        cdf = np.cumsum(pdf)
        return bins_count, cdf

    bins_count, cdf = cdf_calc(response_times)
    
    plt.xlim(0, 600)
    # plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    plt.plot(bins_count[1:], cdf, '--o', label="CDF cerebellum")
    plt.legend()
    plt.show()