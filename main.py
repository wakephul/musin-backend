import nest
nest.set_verbosity('M_ERROR') #lo metto qui per evitare tutte le print
import sys
from src.connection.connect import create_connection, close_connection
from src.queries import spikes_queries, support_queries
from src.file_handling import file_handling

from src.nest.plots.generate import generate_plots
from src.nest.output.rates import calculate_average_rate, calculate_bins
from src.file_handling.support_file import new_row

from src.utils.dictionaries import merge_sort_dicts_of_lists
        
if __name__ == '__main__':
    # CONFIGURATION FILE
    config = file_handling.read_json('data/config/config.json')
    plots_config = file_handling.read_json('data/config/plots_config.json')
    network_config = file_handling.read_json('data/config/network_config.json')
    exit = False

    # connection: connect to database to create table if needed
    if len(sys.argv) > 1 and sys.argv[1] == 'create_spikes_table':
        from src.connection.create import create_table
        try:
            connection = create_connection(config['app']['database'])
            if connection:
                spikes_table_sql = spikes_queries.create_spikes_table()
                create_table(connection, spikes_table_sql)
                close_connection(connection)
                print("Spikes table created")
                exit = True
        except:
            print("Error while connecting to db or creating table")

    if len(sys.argv) > 1 and sys.argv[1] == 'create_support_table':
        try:
            connection = create_connection(config['app']['database'])
            if connection:
                support_table_sql = support_queries.create_support_table()
                create_table(connection, support_table_sql)
                close_connection(connection)
                print("Support table created")
                exit = True
        except:
            print("Error while connecting to db or creating table")

    if not exit:
        from src.nest.reset.reset import nest_reset
        from importlib import import_module
        from src.nest.spike_trains.edit import spikes_for_simulation
        from src.nest.spike_trains.generate import poisson_spikes_generator_parrot, spike_generator_from_times
        from src.file_handling.folder_handling import create_folder

        # executions_information = []
        executions = config['executions']
        execution_types = config['execution_types']

        for execution in executions:
            new_simulation_id = new_row(file_path='output/executions/executions.csv', data=[execution['name'], '/'.join(execution['types']), '/'.join(execution['primary_networks']), '/'.join(execution['secondary_networks'])])
            current_simulations_folder = 'output/executions/'+str(new_simulation_id)+'/'
            create_folder(current_simulations_folder)
            # ! TODO: qui l'heading non dovrebbe essere esattamente così, nel senso che i file name li potrei togliere
            # ! e bisognerebbe salvare solo i parametri che effettivamente variano durante la simulazione
            new_row(file_path=current_simulations_folder+'simulations.csv', heading=['id','spikes_A_file_name','spikes_B_file_name','spikes_rate','firing_rate_extern','rate_A','rate_B'])
            current_simulation_folder = current_simulations_folder+'simulations/'
            create_folder(current_simulation_folder)
            current_simulation_id = 1 # parto da 1 così è allineato con l'ID nel CSV
            nest_reset()
            
            execution_stimuli = []
            for execution_index, execution_type in enumerate(execution['types']):
                execution_params = execution_types[execution_type]
                execution_stimuli.append([])
                if 'use_existent_spikes' in execution_params and not execution_params['use_existent_spikes']:
                    spikes_params = execution_params['spikes']
                    spikes_values = {}
                    has_multiple_values = []
                    for spike_params_key, spikes_params_info in spikes_params.items():
                        if 'single_value' in spikes_params_info and not spikes_params_info['single_value']:
                            print('spikes_params_info', spikes_params_info)
                            spikes_values[spike_params_key] = []
                            has_multiple_values.append(spike_params_key)
                            for value in range(int(spikes_params_info['first_value']*1000), int(spikes_params_info['last_value']*1000+spikes_params_info['increment']*1000), int(spikes_params_info['increment']*1000)):

                                spikes_values[spike_params_key].append(float(value/1000))
                        else:
                            spikes_values[spike_params_key] = spikes_params_info['value']
                    
                # else: qui andrà effettivamente il codice per usare un file di spikes già esistente (passato in input)
                    # spikes_A_times = file_handling.file_open(spikes_A)
                    # spikes_B_times = file_handling.file_open(spikes_B)
                    # spikes_A = spike_generator_from_times(spikes_A_times)
                    # spikes_B = spike_generator_from_times(spikes_B_times)

                start = spikes_values['first_spike_latency'] # latency of first spike in ms, represents the beginning of the simulation relative to trial start
                number_of_neurons = spikes_values['number_of_neurons']
                trial_duration = stop = spikes_values['trial_duration'] # trial duration in ms
                if not isinstance(spikes_values['rate'], list):
                    spikes_values['rate'] = [spikes_values['rate']]
                for r in spikes_values['rate']:
                    rate = r
                    spikes_A_times = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)
                    nest_reset()
                    spikes_B_times = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)
                    nest_reset()

                    execution_stimuli[execution_index].append([spikes_A_times, spikes_B_times])

            print('stimuli:', len(execution_stimuli))
            duplicate_primary_network = False
            input_stimuli = []
            for execution_index in range(len(execution['types'])):
                stimuli_to_edit = execution_stimuli[execution_index]
                # TODO: credo che qui sotto manchi la gestione degli stimoli generati con rate diversi.
                # ! dovrei aver fatto, da testare!
                for stimuli_to_merge in stimuli_to_edit:
                    if(len(execution['types']) > 1): #se visual o auditory allora faccio un solo ciclo, altrimenti li faccio entrambi e mergio (se merge_types è a true)
                        # TODO: gestire anche qui i casi in cui ho più di due popolazioni / più di due stimoli alla volta (?)
                        if ('merge_stimuli' in execution and execution['merge_stimuli']):
                            print('Stimuli are being merged:', stimuli_to_merge[0][0], stimuli_to_merge[1][0])
                            spikes_A_times_merged = merge_sort_dicts_of_lists(stimuli_to_merge[0][0], stimuli_to_merge[1][0])
                            spikes_B_times_merged = merge_sort_dicts_of_lists(stimuli_to_merge[0][1], stimuli_to_merge[1][1])
                            input_stimuli = [[spikes_A_times_merged, spikes_B_times_merged]]
                        else:
                            print('Multiple stimuli, won\'t be merged: another cortex will be added')
                            input_stimuli = stimuli_to_merge
                            duplicate_primary_network = True
                            
                    else:
                        print('There is only one execution to perform')
            
                for primary_network in execution['primary_networks']:
                    primary_networks = [primary_network for x in range(len(execution['types']))] if duplicate_primary_network else [primary_network]
                    print('reti primarie:', primary_networks)
                    for stimulus, network in zip(input_stimuli, primary_networks):
                        network_module = import_module('src.nest.networks.'+network)
                        network_params = file_handling.read_json('data/config/networks/'+network+'.json')
                        network_config_params = network_config[network]

                        # TODO: gestire in automatico i diversi parametri
                        firing_rate_extern = network_config['firing_rate_extern']
                        for fre in range(int(firing_rate_extern['first_value']*1000), int(firing_rate_extern['last_value']*1000+firing_rate_extern['increment']*1000), int(firing_rate_extern['increment']*1000)):
                            network_params['firing_rate_extern'] = float(fre/1000)

                            nest_reset()
                            from scripts.network_output_clean import network_output_clean
                            network_output_clean()

                            output_folder = current_simulation_folder+str(current_simulation_id)+'/'
                            create_folder(output_folder)
                            create_folder(output_folder+'spikes')
                            current_simulation_id += 1

                            spikes_A = spike_generator_from_times(spikes_A_times)
                            spikes_B = spike_generator_from_times(spikes_B_times)

                            spikes_A_file_name = file_handling.save_to_file(spikes_A_times, output_folder+'spikes/spikes_A')
                            spikes_B_file_name = file_handling.save_to_file(spikes_B_times, output_folder+'spikes/spikes_B')
                            
                            file_handling.append_to_file(output_folder+'simulation_notes.txt', '\nExecution name:'+execution['name'])
                            file_handling.append_to_file(output_folder+'simulation_notes.txt', '\nExecution types:'+'/'.join(execution['types']))

                            trials_side_to_string = spikes_for_simulation([spikes_A, spikes_B], (float(network_params['t_stimulus_duration']) - float(network_params['t_stimulus_start'])), float(network_params['max_sim_time']))
                            file_handling.append_to_file(output_folder+'simulation_notes.txt', trials_side_to_string)

                            current_simulation = [spikes_A_file_name, spikes_B_file_name]+[str(exec[0])]

                            current_simulation.append(str(fre/1000))

                            network_params['imported_stimulus_A'] = spikes_A
                            network_params['imported_stimulus_B'] = spikes_B
                            
                            simulation_results = network_module.run(network_params)
                            print("RESULTS", simulation_results)

                            # ! TODO: eguagliare i vari assi dei grafici per poterli comparare
                            
                            plots_to_create = plots_config[network]

                            max_time = int(network_params['max_sim_time'])

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

                            file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nSpikes rate: {str(exec[0])} Hz")
                            file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nFiring rate extern: {str(float(fre/1000))} Hz")

                            file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nPopulation A rate: {rate_A} Hz")
                            file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nPopulation B rate: {rate_B} Hz")

                            current_simulation.append(rate_A)
                            current_simulation.append(rate_B)
                            new_row('', current_simulations_folder+'simulations.csv', current_simulation)