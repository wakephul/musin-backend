import sys
from src.connection.connect import create_connection, close_connection
from src.queries import spikes_queries, support_queries
from src.file_handling import file_handling
        
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
                print(spikes_table_sql)
                create_table(connection, spikes_table_sql)
                print(config['app']['database'])
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

        executions = [] # it's a single execution, the information is already saved elsewhere
            
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

        # if spikes don't exist, generate spikes 
        # (--> nest: generate spikes + file: save them in json + connection: save filename in db)
        from src.nest.spike_trains.spike_train_generator import poisson_spikes_generator_parrot, spike_generator_from_times

        if (not (spikes_A and spikes_B)) or (len(sys.argv) > 1 and (sys.argv[1] == 'generate_spikes' or sys.argv[1] == 'multiple_simulations')):

            if (sys.argv[1] == 'multiple_simulations'):
                multiple_simulations_params = file_handling.read_json('data/config/multiple_simulations_config.json')
                print('multiple_simulations_params', multiple_simulations_params)
                if 'spikes' in multiple_simulations_params:
                    spikes_params = multiple_simulations_params['spikes']
                    if 'rate' in spikes_params:
                        spikes_rate = spikes_params['rate']
                        print('spikes_rate', spikes_rate)
                        for rate in range(spikes_rate['first_value'], spikes_rate['last_value']+spikes_rate['increment'], spikes_rate['increment']):

                            rate = float(rate)

                            start = spikes_params['first_spike_latency'] # latency of first spike in ms, represents the beginning of the simulation relative to trial start
                            number_of_neurons = spikes_params['number_of_neurons']
                            trial_duration = stop = spikes_params['trial_duration'] # trial duration in ms

                            spikes_A_times = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)
                            nest_reset(2021) # necessary to have the network start off with a "clean" nest setup
                            spikes_B_times = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)
                            nest_reset() # necessary to have the network start off with a "clean" nest setup

                            # questo deve essere letto da N spike generators (tanti quanti i parrot neurons), il cui output diventerà l'input della rete
                            # ciascuno spike generator avrà la sua lista di spike times 
                            # con un nest.setStatus possiamo far generare a ciascuno spike generator gli spikes con i tempi corretti
                            
                            spikes_A = spike_generator_from_times(spikes_A_times)
                            spikes_B = spike_generator_from_times(spikes_B_times)

                            import nest
                            spikes_A_status = nest.GetStatus(spikes_A)
                            spikes_B_status = nest.GetStatus(spikes_B)

                            # file: save spikes in json
                            spikes_A_file_name = file_handling.save_to_file(spikes_A_times, 'multiple_trials_spikes/spikes_A_'+str(int(rate))+'_')
                            spikes_B_file_name = file_handling.save_to_file(spikes_B_times, 'multiple_trials_spikes/spikes_B_'+str(int(rate))+'_')

                            from src.file_handling.folder_handling import create_folder
                            from src.file_handling.file_handling import write_to_file
                            from src.file_handling.support_file import get_last_id

                            current_output_folder = 'output/multiple_trials/'+str(get_last_id('output/multiple_trials/support.csv'))+'/'
                            print("output folder:", current_output_folder)

                            create_folder(current_output_folder)

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

                # questo deve essere letto da N spike generators (tanti quanti i parrot neurons), il cui output diventerà l'input della rete
                # ciascuno spike generator avrà la sua lista di spike times 
                # con un nest.setStatus possiamo far generare a ciascuno spike generator gli spikes con i tempi corretti
                
                spikes_A = spike_generator_from_times(spikes_A_times)
                spikes_B = spike_generator_from_times(spikes_B_times)

                import nest
                spikes_A_status = nest.GetStatus(spikes_A)
                spikes_B_status = nest.GetStatus(spikes_B)

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
            print('Spikes already exist:')
            # file: open spikes file
            spikes_A_times = file_handling.file_open(spikes_A)
            spikes_B_times = file_handling.file_open(spikes_B)
            spikes_A = spike_generator_from_times(spikes_A_times)
            spikes_B = spike_generator_from_times(spikes_B_times)

        
        # nest: here we need to connect spikes to input neurons

        from src.nest.networks import brian_nest
        from src.nest.spike_trains.spike_train_editor import spikes_for_simulation

        # file: read Brian params from json
        network_params = file_handling.read_json(config['networks']['brian_nest_params'])
        network_params['imported_stimulus_A'] = spikes_A
        network_params['imported_stimulus_B'] = spikes_B

        #creo una nuova riga nel file di supporto, in cui se esistono inserisco anche le note sul trial
        #questo mi serve per ottenere l'id del trial corrente ed usarlo per salvare gli output nella cartella corretta
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

            brian_nest.run(network_params)

        else:
            spikes_A_new = nest.GetStatus(spikes_A)
            spikes_B_new = nest.GetStatus(spikes_B)
            for exec in executions:
                network_params['current_output_folder'] = 'output/multiple_trials/'+exec[2]+'/'
                spikes_for_simulation([spikes_A, spikes_B], (float(network_params['t_stimulus_duration']) - float(network_params['t_stimulus_start'])), float(network_params['max_sim_time']), network_params['current_output_folder'])
                if (sys.argv[1] == 'multiple_simulations'):
                    # TODO: gestire in automatico i diversi parametri
                    firing_rate_extern = multiple_simulations_params['network']['firing_rate_extern']
                    for fre in range(int(firing_rate_extern['first_value']*1000), int(firing_rate_extern['last_value']*1000+firing_rate_extern['increment']*1000), int(firing_rate_extern['increment']*1000)):
                        network_params['firing_rate_extern'] = fre/1000
                        network_params['execution'] = exec.append(str(fre/1000))
                        
                        nest.ResetKernel()
                        from scripts.network_output_clean import network_output_clean
                        network_output_clean()

                        #recreate spikes
                        spikes_A = []
                        spikes_B = []
                        for i, el in enumerate(spikes_A_new):
                            spikes_A.append((nest.Create('spike_generator', params={'spike_times': el['spike_times'], 'start': el['start'], 'stop': el['stop']})[0]))
                        for i, el in enumerate(spikes_B_new):
                            spikes_B.append((nest.Create('spike_generator', params={'spike_times': el['spike_times'], 'start': el['start'], 'stop': el['stop']})[0]))

                        network_params['imported_stimulus_A'] = spikes_A
                        network_params['imported_stimulus_B'] = spikes_B
                        print('PARAMETRI:', network_params)
                        brian_nest.run(network_params)