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

        if (not (spikes_A and spikes_B)) or (len(sys.argv) > 1 and sys.argv[1] == 'generate_spikes'):

            # nest: generate spikes
            # @todo! spostare in file appositi (prevedere di averne più di 1)
            rate = 40.0
            start = 50.0 # latency of first spike in ms, represents the beginning of the simulation relative to trial start
            number_of_neurons = 100
            trial_duration = stop = 1000.0 # trial duration in ms

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
            print(spikes_A)
            print(spikes_B)
            # file: open spikes file
            spikes_A_times = file_handling.file_open(spikes_A)
            spikes_B_times = file_handling.file_open(spikes_B)
            spikes_A = spike_generator_from_times(spikes_A_times)
            spikes_B = spike_generator_from_times(spikes_B_times)

        
        # nest: here we need to connect spikes to input neurons

        from src.nest.networks import brian_nest
        from src.nest.spike_trains.spike_train_editor import spikes_for_simulation
        #stabilire quanti trial voglio fare (ad esempio 100), in maniera tale da creare tutti gli spike anche nella loro "versione shiftata di 1 secondo"
        # quindi se abbiamo uno spike a 250ms dovremo averlo anche a 1250ms
        # questo lo facciamo in fase di importazione del json nella rete.

        # file: read Brian params from json
        brian_params = file_handling.read_json(config['networks']['brian_nest_params'])
        spikes_for_simulation([spikes_A, spikes_B], (float(brian_params['t_stimulus_duration']) - float(brian_params['t_stimulus_start'])), float(brian_params['max_sim_time']))

        brian_params['imported_stimulus_A'] = spikes_A
        brian_params['imported_stimulus_B'] = spikes_B
        brian_params['trial_notes'] = sys.argv[1] if len(sys.argv) > 1 else ''
        # print("params", brian_params)

        # brian_nest.run(brian_params)