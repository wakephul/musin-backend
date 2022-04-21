import nest
nest.set_verbosity('M_ERROR') #lo metto qui per evitare tutte le print
import sys
from src.connection.connect import create_connection, close_connection
from src.queries import spikes_queries, support_queries
from src.file_handling import file_handling

from src.nest.plots.generate import generate_plots
from src.nest.plots.save import save_plots
        
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
                if 'spikes' in multiple_simulations_params:
                    spikes_params = multiple_simulations_params['spikes']
                    if 'rate' in spikes_params:
                        spikes_rate = spikes_params['rate']
                        for rate in range(spikes_rate['first_value'], spikes_rate['last_value']+spikes_rate['increment'], spikes_rate['increment']):

                            rate = float(rate)

                            start = spikes_params['first_spike_latency'] # latency of first spike in ms, represents the beginning of the simulation relative to trial start
                            number_of_neurons = spikes_params['number_of_neurons']
                            trial_duration = stop = spikes_params['trial_duration'] # trial duration in ms

                            spikes_A_times = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)
                            nest_reset(2021) # necessary to have the network start off with a "clean" nest setup
                            spikes_B_times = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)
                            nest_reset() # necessary to have the network start off with a "clean" nest setup
                            
                            spikes_A = spike_generator_from_times(spikes_A_times)
                            spikes_B = spike_generator_from_times(spikes_B_times)

                            new_simulation_id = new_row(file_path='multiple_trials/support.csv', data=[network_name])
                            current_output_folder = 'multiple_trials/'+str(new_simulation_id)+'/'

                            create_folder(current_output_folder)

                            spikes_A_file_name = file_handling.save_to_file(spikes_A_times, current_output_folder+'/spikes/spikes_A')
                            spikes_B_file_name = file_handling.save_to_file(spikes_B_times, current_output_folder+'/spikes/spikes_B')

                            new_row(file_path=current_output_folder+'support.csv', heading='id,spikes_A_file_name,spikes_B_file_name,spikes_rate,firing_rate_extern,rate_A,rate_B')

                            single_execution_information = [spikes_A_file_name, spikes_B_file_name, str(int(rate))]
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

        if not executions:
            from src.file_handling.support_file import new_row
            from src.file_handling.folder_handling import create_folder
            from src.file_handling.file_handling import write_to_file

            trial_notes = sys.argv[1] if len(sys.argv) > 1 else ''
            current_trial_id = new_row(trial_notes)
            current_output_folder = 'output/trials/'+str(current_trial_id)+'/'

            create_folder(current_output_folder)
            create_folder(current_output_folder+'merged_plots/')
            create_folder(current_output_folder+'values/')

            write_to_file(current_output_folder+"trial_notes.txt", trial_notes)

            network_params['current_output_folder'] = current_output_folder

            spikes_for_simulation([spikes_A, spikes_B], (float(network_params['t_stimulus_duration']) - float(network_params['t_stimulus_start'])), float(network_params['max_sim_time']), current_output_folder)

            network_params['execution'] = None
            network_module.run(network_params)

        else:
            spikes_A_status = nest.GetStatus(spikes_A)
            spikes_B_status = nest.GetStatus(spikes_B)
            for index, exec in enumerate(executions):
                network_params['current_output_folder'] = 'output/multiple_trials/'+str(index)+'/'
                spikes_for_simulation([spikes_A, spikes_B], (float(network_params['t_stimulus_duration']) - float(network_params['t_stimulus_start'])), float(network_params['max_sim_time']), network_params['current_output_folder'])
                if (sys.argv[1] == 'multiple_simulations'):
                    # TODO: gestire in automatico i diversi parametri
                    firing_rate_extern = multiple_simulations_params['network']['firing_rate_extern']
                    for fre in range(int(firing_rate_extern['first_value']*1000), int(firing_rate_extern['last_value']*1000+firing_rate_extern['increment']*1000), int(firing_rate_extern['increment']*1000)):
                        network_params['firing_rate_extern'] = fre/1000
                        exec.append(str(fre/1000))
                        network_params['execution'] = exec
                        
                        nest.ResetKernel()
                        from scripts.network_output_clean import network_output_clean
                        network_output_clean()

                        #recreate spikes
                        spikes_A = []
                        spikes_B = []
                        for i, el in enumerate(spikes_A_status):
                            spikes_A.append((nest.Create('spike_generator', params={'spike_times': el['spike_times'], 'start': el['start'], 'stop': el['stop']})[0]))
                        for i, el in enumerate(spikes_B_status):
                            spikes_B.append((nest.Create('spike_generator', params={'spike_times': el['spike_times'], 'start': el['start'], 'stop': el['stop']})[0]))

                        network_params['imported_stimulus_A'] = spikes_A
                        network_params['imported_stimulus_B'] = spikes_B

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

                        generate_plots(plots_to_create, simulation_results['current_output_folder'])

                        events_A = nest.GetStatus(simulation_results["spike_monitor_A"], "n_events")[0]
                        events_B = nest.GetStatus(simulation_results["spike_monitor_B"], "n_events")[0]

                        senders_spike_monitor_A = nest.GetStatus(simulation_results["spike_monitor_A"], 'events')[0]['senders']
                        times_spike_monitor_A = nest.GetStatus(simulation_results["spike_monitor_A"], 'events')[0]['times']

                        # * in questa implementazione quello che faccio è assegnare a ciascun id i propri tempi di sparo
                        # monitored_spikes_A = {}
                        # for index, sender in enumerate(senders_spike_monitor_A):
                        # 	if sender in monitored_spikes_A:
                        # 		monitored_spikes_A[sender].append(times_spike_monitor_A[index])
                        # 	else:
                        # 		monitored_spikes_A[sender] = [times_spike_monitor_A[index]]
                        # for id in monitored_spikes_A:
                        # 	monitored_spikes_A[id].sort()
                        # print('monitored_spikes_A', monitored_spikes_A)

                        # * penso che dovrebbe funzionare al contrario, ovvero dovrei assegnare l'elenco degli id a ciascun tempo
                        # * in questo modo potrei dividerli già sulla base dei bin (forse), oppure calcolare e poi proseguire con il calcolo
                        bin_size = 5 # value in ms
                        max_time = int(data['max_sim_time'])
                        bins = list(range(bin_size, max_time+1, bin_size))
                        monitored_times_A = {}
                        for index, time in enumerate(times_spike_monitor_A):
                            bin_index = np.digitize(time, bins, right=True)
                            if bin_index < len(bins):
                                bin_time = np.take(bins, bin_index)
                                if bin_time in monitored_times_A:
                                    monitored_times_A[bin_time].append(senders_spike_monitor_A[index])
                                else:
                                    monitored_times_A[bin_time] = [senders_spike_monitor_A[index]]
                        for id in monitored_times_A:
                            monitored_times_A[id].sort()
                        # print('monitored_times_A', monitored_times_A)
                        # * qui fondamentalmente ho un elenco di tutti gli spari che si vedono in ciascun bin
                        # * il problema è che ci sono un sacco di duplicati in ciascun bin, cioè mi pare che la frequenza sia un po' alta se ogni neurone spara 2 o 3 volte ogni 5ms
                        bin_rates = {}
                        for bin_time, spikes_list in monitored_times_A.items():
                            bin_rate = len(spikes_list) * 1000 / (bin_size * len(simulation_results["idx_monitored_neurons_A"]))
                            bin_rates[bin_time] = bin_rate
                            print(f'rate nel bin {bin_time}: {bin_rate} Hz')

                        print('bin_rates', bin_rates)

                        rate_A = events_A / data['max_sim_time'] * 1000.0 / len(simulation_results["idx_monitored_neurons_A"])
                        rate_B = events_B / data['max_sim_time'] * 1000.0 / len(simulation_results["idx_monitored_neurons_B"])

                        print("Population A rate   : %.2f Hz" % rate_A)
                        print("Population B rate   : %.2f Hz" % rate_B)

                        if data['execution']:
                            data['execution'].append(rate_A)
                            data['execution'].append(rate_B)
                            data['execution'].pop(0)
                            new_row('', 'output/multiple_trials/support.csv', data['execution'])
                        else:
                            append_to_file(output_folder+'trial_notes.txt', f"\n\nPopulation A rate: {rate_A:.2f} Hz\nPopulation B rate: {rate_B:.2f} Hz")