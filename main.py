import pdb

import nest
nest.set_verbosity('M_ERROR') #lo metto qui per evitare tutte le print
import sys
import shutil
import json
from src.connection.connect import create_connection, close_connection
from src.queries import spikes_queries, support_queries
from src.file_handling import file_handling

from src.nest.plots.generate import generate_plots, moving_average_plot
from src.nest.output.rates import calculate_average_rate, calculate_bins, calculate_response_times
from src.file_handling.support_file import new_row

from src.utils.dictionaries import merge_sort_dicts_of_lists
from src.utils.combinations import combinations_generator
import src.utils.cdf as cdf
from scripts.network_output_clean import network_output_clean

from src.nest.reset.reset import nest_reset
from importlib import import_module
from src.nest.spike_trains.edit import edit_spikes_for_simulation
from src.nest.spike_trains.generate import poisson_spikes_generator_parrot, spike_generator_from_times
from src.file_handling.folder_handling import create_folder
from src.file_handling.images.edit import merge_plots

from src.nest.output.device_manager import multimeters_merge, spike_detectors_merge


if __name__ == '__main__':
    # CONFIGURATION FILE
    config = file_handling.read_json('data/config/config.json')
    plots_config = file_handling.read_json('data/config/plots_config.json')
    plots_merge_config = file_handling.read_json('data/config/plots_merge_config.json')
    network_config = file_handling.read_json('data/config/network_config.json')
    execution_types = file_handling.read_json('data/config/execution_types.json')
    exit = False

    # connection: connect to database to create table if needed
    # if len(sys.argv) > 1 and sys.argv[1] == 'create_spikes_table':
    #     from src.connection.create import create_table
    #     try:
    #         connection = create_connection(config['app']['database'])
    #         if connection:
    #             spikes_table_sql = spikes_queries.create_spikes_table()
    #             create_table(connection, spikes_table_sql)
    #             close_connection(connection)
    #             print("Spikes table created")
    #             exit = True
    #     except:
    #         print("Error while connecting to db or creating table")

    # if len(sys.argv) > 1 and sys.argv[1] == 'create_support_table':
    #     try:
    #         connection = create_connection(config['app']['database'])
    #         if connection:
    #             support_table_sql = support_queries.create_support_table()
    #             create_table(connection, support_table_sql)
    #             close_connection(connection)
    #             print("Support table created")
    #             exit = True
    #     except:
    #         print("Error while connecting to db or creating table")

    if not exit:

        executions = config['executions']

        for execution_index, execution in enumerate(executions):
            #todo prendi info dal db e scrivi nuova esecuzione
            merge_stimuli = True if ((not 'merge_stimuli' in execution) or ('merge_stimuli' in execution and execution['merge_stimuli'])) else False
            networks_for_csv = '/'.join([n + '_DUPL' for n in execution['networks']]) if not merge_stimuli else '/'.join(execution['networks'])
            new_simulation_id = new_row(file_path='output/executions/executions.csv', data=[execution['name'], '/'.join(execution['types']), networks_for_csv, '/'.join(execution['networks'])])
            current_simulations_folder = 'output/executions/'+str(new_simulation_id)+'/'
            create_folder(current_simulations_folder)
            shutil.copytree('data/config', current_simulations_folder+'config')
            file_handling.write_to_file(current_simulations_folder+'config/execution_id', str(execution_index))
            
            execution_stimuli = {}

            for execution_type in execution['types']:
                execution_params = execution_types[execution_type]
                execution_stimuli[execution_type] = []
                spikes_combinations = []
                if not execution_params['use_existent_spikes']:
                    spikes_params = execution_params['spikes']
                    spikes_values = {}
                    for spikes_params_key, spikes_params_info in spikes_params.items():
                        if 'single_value' in spikes_params_info and not spikes_params_info['single_value']:
                            spikes_values[spikes_params_key] = []
                            for value in range(int(spikes_params_info['first_value']*1000), int(spikes_params_info['last_value']*1000+spikes_params_info['increment']*1000), int(spikes_params_info['increment']*1000)):
                                spikes_values[spikes_params_key].append(float(value/1000))
                        else:
                            spikes_values[spikes_params_key] = [spikes_params_info['value']]

                    spikes_combinations = combinations_generator(spikes_values)

                for combination in spikes_combinations:
                    rate = combination['rate']
                    start = combination['first_spike_latency']
                    number_of_neurons = combination['number_of_neurons']
                    trial_duration = stop = combination['trial_duration']
                    
                    if execution_index > 0:
                        nest_reset(execution['reset_values'][2])

                    spikes_A_times = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)
                    nest_reset(execution['reset_values'][0])
                    spikes_B_times = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)
                    nest_reset(execution['reset_values'][1])

                    execution_stimuli[execution_type].append({'info': 'rate='+str(rate)+'&start='+str(start)+'&number_of_neurons='+str(number_of_neurons)+'&trial_duration='+str(trial_duration), 'A': spikes_A_times, 'B': spikes_B_times})

            duplicate_primary_network = False
            input_stimuli_A = {'cortex_1': {'info': [], 'stimuli': []}, 'cortex_2': {'info': [], 'stimuli': []}}
            input_stimuli_B = {'cortex_1': {'info': [], 'stimuli': []}, 'cortex_2': {'info': [], 'stimuli': []}}

            if(len(execution['types']) > 1):
                #TODO! il numero di cortecce e dei tipi di esecuzione deve essere gestito in maniera DINAMICA
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

                            input_stimuli_B['cortex_1']['info'].append(execution['types'][0]+'_'+ex_type_1['info'])
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
            
            new_row(file_path=current_simulations_folder+'simulations.csv', heading=['id','spikes_info','firing_rate_extern','rate_A','rate_B'])
            current_simulation_folder = current_simulations_folder+'simulations/'
            create_folder(current_simulation_folder)
            current_simulation_id = 1 # parto da 1 così è allineato con l'ID nel CSV

            if len(execution['networks']):
                for network in execution['networks']:
                    print('network:', network)
                    network_module = import_module('src.nest.networks.'+network)
                    network_params = file_handling.read_json('data/config/networks/'+network+'.json')
                    
                    current_network_folder = current_simulation_folder+'/'+network+'/'
                    create_folder(current_network_folder)

                    if not merge_stimuli:
                        number_of_cortex = 2
                        for cortex_id in range(1, (number_of_cortex+1)):
                            nest_reset(execution['reset_values'][0])
                            network_output_clean()
                            current_cortex_value = 'cortex_'+str(cortex_id)
                            print('CORTEX ID: ', current_cortex_value)
                            current_cortex_folder = current_network_folder+current_cortex_value+'/'
                            create_folder(current_cortex_folder)
                            output_folder = current_cortex_folder+str(current_simulation_id)+'/'
                            create_folder(output_folder)
                            create_folder(output_folder+'spikes')
                            current_simulation_id += 1
                            
                            spikes_A = spike_generator_from_times(input_stimuli_A[current_cortex_value]['stimuli'][0])
                            spikes_B = spike_generator_from_times(input_stimuli_B[current_cortex_value]['stimuli'][0])

                            current_simulation = [network]

                            duration = int(network_params['t_stimulus_duration'])
                            train_time = int((network_params['train_time']))
                            test_time = int((network_params['test_time']))
                            test_types = network_params['test_types']
                            test_number = len(test_types)
                            trials_side = edit_spikes_for_simulation([spikes_A, spikes_B], duration, train_time/3, test_time/3, test_number)

                            network_params['imported_stimulus_A'] = spikes_A
                            network_params['imported_stimulus_B'] = spikes_B
                            train_time_old = network_params['train_time']
                            network_params['train_time'] = int(train_time)
                            network_params['test_time'] = int(test_time)
                            network_params['trials_side'] = trials_side
        
                            simulation_results = {}
                            try:
                                simulation_results = network_module.run(network_params)
                            except Exception as e:
                                print(e)
                                import traceback
                                print(traceback.format_exc())

                            # pdb.set_trace()
                            
                            plots_to_create = plots_config[network] if (network in plots_config) else None
                            if plots_to_create:
                                generate_plots(plots_to_create, output_folder, simulation_results, train_time=train_time, test_time=test_time, test_number=test_number, train=simulation_results["train"], test=simulation_results["test"], sides=trials_side)

                            plots_to_merge = plots_merge_config[network] if (network in plots_merge_config) else None
                            
                            #TODO! automatizzare questa cosa perché così è tutto hardcodato male
                            senders_spike_monitor_A = nest.GetStatus(simulation_results["spike_monitor_A"], 'events')[0]['senders']
                            times_spike_monitor_A = nest.GetStatus(simulation_results["spike_monitor_A"], 'events')[0]['times']
                            senders_spike_monitor_B = nest.GetStatus(simulation_results["spike_monitor_B"], 'events')[0]['senders']
                            times_spike_monitor_B = nest.GetStatus(simulation_results["spike_monitor_B"], 'events')[0]['times']

                            bin_size = 5
                            
                            bin_rates_A_complete = calculate_bins(senders_spike_monitor_A, times_spike_monitor_A, len(simulation_results["idx_monitored_neurons_A"]), bin_size, train_time, train_time+(test_time*test_number), test_number)
                            bin_rates_B_complete = calculate_bins(senders_spike_monitor_B, times_spike_monitor_B, len(simulation_results["idx_monitored_neurons_B"]), bin_size, train_time, train_time+(test_time*test_number), test_number)


                            for tt_index, tt in enumerate(test_types):
                                bin_rates_a_portion = bin_rates_A_complete[tt_index]
                                bin_rates_b_portion = bin_rates_B_complete[tt_index]
                                json_title_a = file_handling.dict_to_json(bin_rates_a_portion, output_folder+'bin_rates_A_test_'+str(tt_index))
                                json_title_b = file_handling.dict_to_json(bin_rates_b_portion, output_folder+'bin_rates_B_test_'+str(tt_index))

                            # create_folder(output_folder+'multimeters')
                            # create_folder(output_folder+'spike_detectors')
                            # multimeters_merge(output_folder+'multimeters/')
                            # spike_detectors_merge(output_folder+'spike_detectors/')

                            # monitors = ['spike_monitor_A', 'spike_monitor_B']
                            # monitored_populations = ['idx_monitored_neurons_A', 'idx_monitored_neurons_B']

                            # rates = calculate_average_rate(simulation_results=simulation_results, max_time=test_time*test_number, monitors=monitors, monitored_populations=monitored_populations)

                            # file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nRates: " + ', '.join(map(str, zip(monitors, rates))))

                            new_row('', current_simulations_folder+'simulations.csv', current_simulation)

            # if len(execution['secondary_networks']):
            #     for network in execution['secondary_networks']:
            #         print('secondary network:', network)
            #         network_module = import_module('src.nest.networks.'+network)
            #         network_params = file_handling.read_json('data/config/networks/secondary/'+network+'.json')
                    
            #         current_network_folder = current_simulation_folder+'/'+network+'/'
            #         create_folder(current_network_folder)

            #         nest_reset(execution['reset_values'][0])
            #         network_output_clean()

            #         output_folder = current_network_folder+str(current_simulation_id)+'/'
            #         create_folder(output_folder)
            #         create_folder(output_folder+'spikes')
            #         current_simulation_id += 1

            #         spikes_type_1_A = spike_generator_from_times(input_stimuli_A['cortex_1']['stimuli'][0])
            #         spikes_type_2_A = spike_generator_from_times(input_stimuli_A['cortex_2']['stimuli'][0])
            #         spikes_type_1_B = spike_generator_from_times(input_stimuli_B['cortex_1']['stimuli'][0])
            #         spikes_type_2_B = spike_generator_from_times(input_stimuli_B['cortex_2']['stimuli'][0])

            #         current_simulation = [network]

            #         duration = int(network_params['t_stimulus_duration'])
            #         train_time = int((network_params['train_time']))
            #         test_time = int((network_params['test_time']))
            #         test_types = network_params['test_types']
            #         test_number = len(test_types)
            #         trials_type_1 = edit_spikes_for_simulation([spikes_type_1_A, spikes_type_1_B], duration, train_time/3, test_time/3, test_number)
            #         trials_type_2 = edit_spikes_for_simulation([spikes_type_2_A, spikes_type_2_B], duration, train_time/3, test_time/3, test_number)

            #         network_params['imported_stimulus_A'] = {'type_1': spikes_type_1_A, 'type_2': spikes_type_2_A}
            #         network_params['imported_stimulus_B'] = {'type_1': spikes_type_1_B, 'type_2': spikes_type_2_B}
            #         train_time_old = network_params['train_time']
            #         network_params['train_time'] = int(train_time)
            #         network_params['test_time'] = int(test_time)
            #         network_params['trials_side'] = trials_type_1
 
            #         simulation_results = network_module.run(network_params)
                    
            #         # plots_to_create = plots_config[network] if (network in plots_config) else None
            #         # if plots_to_create:
            #         #     generate_plots(plots_to_create, output_folder, simulation_results, train_time=train_time, test_time=test_time, test_number=test_number, train=simulation_results["train"], test=simulation_results["test"], sides=trials_type_1)

            #         plots_to_merge = plots_merge_config[network] if (network in plots_merge_config) else None
                    
            #         senders_spike_monitor_DCN_a = nest.GetStatus(simulation_results["spike_monitor_DCN_a"], 'events')[0]['senders']
            #         times_spike_monitor_DCN_a = nest.GetStatus(simulation_results["spike_monitor_DCN_a"], 'events')[0]['times']
            #         senders_spike_monitor_DCN_b = nest.GetStatus(simulation_results["spike_monitor_DCN_b"], 'events')[0]['senders']
            #         times_spike_monitor_DCN_b = nest.GetStatus(simulation_results["spike_monitor_DCN_b"], 'events')[0]['times']

            #         bin_size = 5
                    
            #         times_spike_monitor_DCN_a = [t for t in times_spike_monitor_DCN_a if t > train_time]
            #         times_spike_monitor_DCN_b = [t for t in times_spike_monitor_DCN_b if t > train_time]
            #         bin_rates_DCN_complete_a = calculate_bins(senders_spike_monitor_DCN_a, times_spike_monitor_DCN_a, len(simulation_results["idx_monitored_neurons_DCN_a"])//2, bin_size, train_time, train_time+(test_time*test_number), test_number)
            #         bin_rates_DCN_complete_b = calculate_bins(senders_spike_monitor_DCN_b, times_spike_monitor_DCN_b, len(simulation_results["idx_monitored_neurons_DCN_a"])//2, bin_size, train_time, train_time+(test_time*test_number), test_number)

            #         cdf_plots = []
                    
            #         for tt_index, tt in enumerate(test_types):
            #             bin_rates_a_portion = bin_rates_DCN_complete_a[tt_index]
            #             bin_rates_b_portion = bin_rates_DCN_complete_b[tt_index]
            #             json_title_a = file_handling.dict_to_json(bin_rates_a_portion, output_folder+'bin_rates_DCN_a_test_'+str(tt_index))
            #             json_title_b = file_handling.dict_to_json(bin_rates_b_portion, output_folder+'bin_rates_DCN_b_test_'+str(tt_index))

            #             # moving_average_plot(bin_rates_a_portion, output_folder+'plots/', 'ma_rates_DCN_a_test_'+str(tt_index), (train_time+(test_time*tt_index), train_time+test_time+(test_time*tt_index)))

            #             # cdf.calculate([json_title_a, json_title_b], output_folder+'plots/', 'cdf_test_'+str(tt_index), 5, 'save')

            #             # ma_plots.append(['ma_rates_DCN_a', 'ma_rates', 'test'])
            #             # cdf_plots.append(['cdf', 'cdf', 'test'])
                    
            #         # merge_plots(output_folder, cdf_plots, 'cdf_plots', len(test_types))

            #         create_folder(output_folder+'multimeters')
            #         create_folder(output_folder+'spike_detectors')
            #         multimeters_merge(output_folder+'multimeters/')
            #         spike_detectors_merge(output_folder+'spike_detectors/')

            #         # monitors = ['spike_monitor_DCN_a', 'spike_monitor_DCN_b']
            #         # monitored_populations = ['idx_monitored_neurons_DCN_a', 'idx_monitored_neurons_DCN_b']

            #         # rates = calculate_average_rate(simulation_results=simulation_results, max_time=test_time*test_number, monitors=monitors, monitored_populations=monitored_populations)

            #         # file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nRates: " + ', '.join(map(str, zip(monitors, rates))))
            #         file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nExecution: " + json.dumps(execution))

            #         new_row('', current_simulations_folder+'simulations.csv', current_simulation)