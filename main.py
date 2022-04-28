import nest
nest.set_verbosity('M_ERROR') #lo metto qui per evitare tutte le print
import sys
from src.connection.connect import create_connection, close_connection
from src.queries import spikes_queries, support_queries
from src.file_handling import file_handling

from src.nest.plots.generate import generate_plots
from src.nest.output.rates import calculate_average_rate, calculate_bins
from src.file_handling.support_file import new_row
        
if __name__ == '__main__':
    # CONFIGURATION FILE
    config = file_handling.read_json('data/config/config.json')
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

        nest_reset()

        executions = [] # if it's a single execution, the information is already saved elsewhere
            
        # connection: check if spikes exist (connection: get spikes)
        from src.connection.select import select_rows
        spikes_A = False
        spikes_B = False
        try:
            connection = create_connection(config['app']['database'])
            if connection:
                select_spikes_A_sql = spikes_queries.select_existing_spikes('A')
                spikes_A_rows = select_rows(connection, select_spikes_A_sql)
                spikes_A = spikes_A_rows[-1][1]
                select_spikes_B_sql = spikes_queries.select_existing_spikes('B')
                spikes_B_rows = select_rows(connection, select_spikes_B_sql)
                spikes_B = spikes_B_rows[-1][1]
                close_connection(connection)
        except:
            print("Error while selecting spikes from db")

        from importlib import import_module
        from src.nest.spike_trains.edit import spikes_for_simulation
        from src.nest.spike_trains.generate import poisson_spikes_generator_parrot, spike_generator_from_times
        from src.file_handling.folder_handling import create_folder
        from src.file_handling.file_handling import write_to_file

        network_name = config['network']['name']
        network_module = import_module('src.nest.networks.'+network_name)

        if (not (spikes_A and spikes_B)) or (len(sys.argv) > 1 and (sys.argv[1] == 'generate_spikes' or sys.argv[1] == 'multiple_simulations')):

            if (sys.argv[1] == 'multiple_simulations'):
                multiple_simulations_params = file_handling.read_json('data/config/multiple_simulations_config.json')

                new_simulation_id = new_row(file_path='multiple_trials/support.csv', data=[network_name])
                current_simulation_folder = 'multiple_trials/'+str(new_simulation_id)+'/'
                create_folder(current_simulation_folder)
                new_row(file_path=current_simulation_folder+'support.csv', heading=['id','spikes_A_file_name','spikes_B_file_name','spikes_rate','firing_rate_extern','rate_A','rate_B'])
                current_trials_folder = current_simulation_folder+'trials/'
                create_folder(current_trials_folder)
                current_trial_id = 1 # parto da 1 così è allineato con l'ID nel CSV

                if 'spikes' in multiple_simulations_params:
                    spikes_params = multiple_simulations_params['spikes']
                    if 'rate' in spikes_params:
                        spikes_rate = spikes_params['rate']
                        for r in range(int(spikes_rate['first_value']*1000), int(spikes_rate['last_value']*1000+spikes_rate['increment']*1000), int(spikes_rate['increment']*1000)):

                            print('RATE', r/1000)

                            rate = float(r/1000)

                            start = spikes_params['first_spike_latency'] # latency of first spike in ms, represents the beginning of the simulation relative to trial start
                            number_of_neurons = spikes_params['number_of_neurons']
                            trial_duration = stop = spikes_params['trial_duration'] # trial duration in ms

                            spikes_A_times = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)
                            nest_reset(2021) # necessary to have the network start off with a "clean" nest setup
                            spikes_B_times = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)
                            nest_reset() # necessary to have the network start off with a "clean" nest setup

                            single_execution_information = [spikes_A_times, spikes_B_times, rate]
                            executions.append(single_execution_information)
               
            else:
                spikes_params = file_handling.read_json(config['input']['spikes_params'])
                rate = spikes_params['rate']
                start = spikes_params['first_spike_latency'] # latency of first spike in ms, represents the beginning of the simulation relative to trial start
                number_of_neurons = spikes_params['number_of_neurons']
                trial_duration = stop = spikes_params['trial_duration'] # trial duration in ms

                spikes_A_times = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)
                nest_reset(2021) # necessary to have the network start off with a "clean" nest setup
                spikes_B_times = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)
                nest_reset() # necessary to have the network start off with a "clean" nest setup
                
                spikes_A = spike_generator_from_times(spikes_A_times)
                spikes_B = spike_generator_from_times(spikes_B_times)

                # file: save spikes in json
                spikes_A_file_name = file_handling.save_to_file(spikes_A_times, 'spikes/spikes_A_')
                spikes_B_file_name = file_handling.save_to_file(spikes_B_times, 'spikes/spikes_B_')

                # connection
                from src.connection.insert import insert_row
                try:
                    connection = create_connection(config['app']['database'])
                    if connection:
                        save_spikes_sql = spikes_queries.insert_new_spikes()
                        values_to_insert_A = (spikes_A_file_name, 1, 'A')
                        insert_row(connection, save_spikes_sql, values_to_insert_A)
                        values_to_insert_B = (spikes_B_file_name, 1, 'B')
                        insert_row(connection, save_spikes_sql, values_to_insert_B)
                        close_connection(connection)
                        print("Spikes saved to db")
                        spike_trains_A = spikes_A
                        spike_trains_B = spikes_B
                except:
                    print("Error while saving spikes to db")

        else:
            # file: open spikes file
            spikes_A_times = file_handling.file_open(spikes_A)
            spikes_B_times = file_handling.file_open(spikes_B)
            spikes_A = spike_generator_from_times(spikes_A_times)
            spikes_B = spike_generator_from_times(spikes_B_times)

        # file: read network params from json
        network_params = file_handling.read_json('data/network_params/'+config['network']['params']+'.json')
        network_params['imported_stimulus_A'] = spikes_A
        network_params['imported_stimulus_B'] = spikes_B

        if not executions: # ! questo caso potrei farlo semplicemente rientrare nell'altro, come caso base. Da considerare la possibilità
            from src.file_handling.support_file import new_row
            from src.file_handling.folder_handling import create_folder
            from src.file_handling.file_handling import write_to_file

            trial_notes = sys.argv[1] if len(sys.argv) > 1 else ''
            current_trial_id = new_row(trial_notes)
            output_folder = 'output/trials/'+str(current_trial_id)+'/'

            create_folder(output_folder)
            create_folder(output_folder+'merged_plots/')
            create_folder(output_folder+'values/')

            write_to_file(output_folder+"trial_notes.txt", trial_notes)

            spikes_for_simulation([spikes_A, spikes_B], (float(network_params['t_stimulus_duration']) - float(network_params['t_stimulus_start'])), float(network_params['max_sim_time']))

            simulation_results = network_module.run(network_params)

            plots_to_create = [
                ['spike_monitor_A', 'raster'],
                ['spike_monitor_B', 'raster'],
                ['spike_monitor_Z', 'raster'],
                ['spike_monitor_inhib', 'raster'],
                ['voltage_monitor_A', 'voltage'],
                ['voltage_monitor_B', 'voltage'],
                ['voltage_monitor_Z', 'voltage'],
                ['voltage_monitor_inhib', 'voltage']
            ]

            max_time = int(network_params['max_sim_time'])

            generate_plots(plots_to_create, output_folder, simulation_results, max_time)
            
            bin_rates = calculate_bins(simulation_results, max_time)
            print(bin_rates)
            file_handling.dict_to_json(bin_rates, output_folder+'bin_rates')
            rate_A, rate_B = calculate_average_rate(simulation_results, max_time)

            # print("Population A rate   : %.2f Hz" % rate_A)
            # print("Population B rate   : %.2f Hz" % rate_B)

            spikes_params = file_handling.read_json(config['input']['spikes_params'])

            file_handling.append_to_file(output_folder+'trial_notes.txt', f"\nSpikes rate: {str(spikes_params['rate'])} Hz")
            file_handling.append_to_file(output_folder+'trial_notes.txt', f"\nFiring rate extern: {str(network_params['firing_rate_extern'])} Hz")

            file_handling.append_to_file(output_folder+'trial_notes.txt', f"\nPopulation A rate: {rate_A} Hz")
            file_handling.append_to_file(output_folder+'trial_notes.txt', f"\nPopulation B rate: {rate_B} Hz")

        else:
            for exec in executions:
                spikes_A_times = exec.pop(0)
                spikes_B_times = exec.pop(0)

                # TODO: gestire in automatico i diversi parametri
                firing_rate_extern = multiple_simulations_params['network']['firing_rate_extern']
                for fre in range(int(firing_rate_extern['first_value']*1000), int(firing_rate_extern['last_value']*1000+firing_rate_extern['increment']*1000), int(firing_rate_extern['increment']*1000)):

                    # nest.ResetKernel()
                    nest_reset()
                    from scripts.network_output_clean import network_output_clean
                    network_output_clean()

                    output_folder = current_trials_folder+str(current_trial_id)+'/'
                    create_folder(output_folder)
                    create_folder(output_folder+'spikes')
                    current_trial_id += 1

                    spikes_A = spike_generator_from_times(spikes_A_times)
                    spikes_B = spike_generator_from_times(spikes_B_times)

                    spikes_A_file_name = file_handling.save_to_file(spikes_A_times, output_folder+'spikes/spikes_A')
                    spikes_B_file_name = file_handling.save_to_file(spikes_B_times, output_folder+'spikes/spikes_B')
                    
                    trials_to_string = spikes_for_simulation([spikes_A, spikes_B], (float(network_params['t_stimulus_duration']) - float(network_params['t_stimulus_start'])), float(network_params['max_sim_time']))
                    file_handling.append_to_file(output_folder+'trial_notes.txt', trials_to_string)

                    current_execution = [spikes_A_file_name, spikes_B_file_name]+[str(exec[0])]

                    network_params['firing_rate_extern'] = float(fre/1000)
                    current_execution.append(str(fre/1000))

                    network_params['imported_stimulus_A'] = spikes_A
                    network_params['imported_stimulus_B'] = spikes_B
                    
                    simulation_results = network_module.run(network_params)
                    print("RESULTS", simulation_results)

                    # ! TODO: eguagliare i vari assi dei grafici per poterli comparare
                    
                    plots_to_create = [
                        ['spike_monitor_A', 'raster'],
                        ['spike_monitor_B', 'raster'],
                        ['spike_monitor_Z', 'raster'],
                        ['spike_monitor_inhib', 'raster'],
                        ['voltage_monitor_A', 'voltage'],
                        ['voltage_monitor_B', 'voltage'],
                        ['voltage_monitor_Z', 'voltage'],
                        ['voltage_monitor_inhib', 'voltage']
                    ]

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

                    file_handling.append_to_file(output_folder+'trial_notes.txt', f"\nSpikes rate: {str(exec[0])} Hz")
                    file_handling.append_to_file(output_folder+'trial_notes.txt', f"\nFiring rate extern: {str(float(fre/1000))} Hz")

                    file_handling.append_to_file(output_folder+'trial_notes.txt', f"\nPopulation A rate: {rate_A} Hz")
                    file_handling.append_to_file(output_folder+'trial_notes.txt', f"\nPopulation B rate: {rate_B} Hz")

                    current_execution.append(rate_A)
                    current_execution.append(rate_B)
                    new_row('', current_simulation_folder+'support.csv', current_execution)