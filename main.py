import sys
from src.connection.connect import create_connection, close_connection
from src.queries import spikes_queries
from src.file_handling import file_handling

if __name__ == '__main__':
    
    # CONFIGURATION FILE
    config = file_handling.read_json('data/config/config.json')

    # file: read Brian params from json
    brian_params = file_handling.read_json(config['networks']['brian_nest_params'])

    # connection: connect to database to create table if needed
    # sys.argv[1] sets whether or not spikes table has to be created
    if len(sys.argv) > 1 and sys.argv[1] == 'true':
        from src.connection.create import create_table
        try:
            connection = create_connection(config['app']['database'])
            if connection:
                spikes_table_sql = spikes_queries.create_spikes_table()
                create_table(connection, spikes_table_sql)
                close_connection(connection)
                print("Spikes table created")
        except:
            print("Error while connecting to db or creating table")
        
    # connection: check if spikes exist (connection: get spikes)
    from src.connection.select import select_rows
    spikes = False
    try:
        connection = create_connection(config['app']['database'])
        if connection:
            select_spikes_sql = spikes_queries.select_existing_spikes()
            spikes_rows = select_rows(connection, select_spikes_sql)
            spikes = spikes_rows[-1][1]
            close_connection(connection)
    except:
        print("Error while selecting spikes from db")

    # if spikes don't exist, generate spikes 
    # (--> nest: generate spikes + file: save them in json + connection: save filename in db)
    if not spikes or (len(sys.argv) > 2 and sys.argv[2] == 'true'):

        # nest: generate spikes
        from src.nest.spike_trains.spike_train_generator import poisson_spikes_generator_connected, poisson_spikes_generator
        rate = 40.0
        start = 50.0 # latency of first spike in ms, represents the beginning of the simulation relative to trial start
        number_of_neurons = 100
        trial_duration = stop = 1000.0 # trial duration in ms

        # TODO: temporarily commented because of compatibility with brian_nest
        # spikes = poisson_spikes_generator_connected(rate, start, stop, number_of_neurons, trial_duration)
        spikes = poisson_spikes_generator(rate, start, stop)
        print("Spikes have been generated:")
        print(spikes)

        # file: save spikes in json
        spikes_file_name = file_handling.save_to_file(spikes, 'spikes/spikes_')

        # connection
        from src.connection.insert import insert_row
        try:
            connection = create_connection(config['app']['database'])
            if connection:
                save_spike_sql = spikes_queries.insert_new_spikes()
                values_to_insert = (spikes_file_name, 1)
                insert_row(connection, save_spike_sql, values_to_insert)
                close_connection(connection)
                print("Spikes saved to db")
                spike_trains = spikes
        except:
            print("Error while saving spikes to db")

    else:
        print('Spikes already exist:')
        print(spikes)
        # file: open spikes file
        spike_trains = file_handling.file_open(spikes)
    # nest: connect spikes to input neurons


    print(spike_trains)

    from src.nest.networks import brian_nest
    # #stabilire quanti trial voglio fare (ad esempio 100), in maniera tale da creare tutti gli spike anche nella loro "versione shiftata di 1 secondo"
    # # quindi se abbiamo uno spike a 250ms dovremo averlo anche a 1250ms
    # # questo lo facciamo in fase di importazione del json nella rete.

    # brian_params['imported_stimulus_A'] = spike_trains
    import nest
    N_group_A = int(brian_params['N_Excit'] * brian_params['f_Subpop_size']) # size of the excitatory subpopulation sensitive to stimulus A
    brian_params['imported_stimulus_A'] = nest.Create('poisson_generator', N_group_A)
    print("params", brian_params)

    brian_nest.run(brian_params)

    # input_neurons = nest.Create('iaf_psc_exp', len(spike_trains))
    # print(input_neurons)