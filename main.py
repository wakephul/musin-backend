import sys
from src.connection.connect import create_connection, close_connection

if __name__ == '__main__':

    # connection: connect to database to create table if needed
    # sys.argv[1] sets whether or not spikes table has to be created
    if len(sys.argv) > 1 and sys.argv[1] == 'true':
        from src.connection.create import create_table
        try:
            connection = create_connection('data/db/database.db')
            if connection:
                spikes_table_sql = " \
                                        CREATE TABLE IF NOT EXISTS spikes ( \
                                        spikeID integer PRIMARY KEY AUTOINCREMENT, \
                                        filename varchar(255) NOT NULL, \
                                        updated boolean NOT NULL, \
                                        creation timestamp DEFAULT CURRENT_TIMESTAMP \
                                        ); \
                                    "
                create_table(connection, spikes_table_sql)
                close_connection(connection)
                print("Spikes table created")
        except:
            print("Error while connecting to db or creating table")
        
    # connection: check if spikes exist (connection: get spikes)
    from src.connection.select import select_rows
    spikes = False
    try:
        connection = create_connection('data/db/database.db')
        if connection:
            select_spikes_sql = " \
                                SELECT * FROM spikes \
                                WHERE updated = 1 \
                                ORDER BY creation ASC \
                            "
            spikes = select_rows(connection, select_spikes_sql)
            close_connection(connection)
    except:
        print("Error while selecting spikes from db")

    # if spikes don't exist, generate spikes 
    # (--> nest: generate spikes + file: save them in json + connection: save filename in db)
    if not spikes:

        # nest: generate spikes
        from src.nest.spike_trains.spike_train_generator import poisson_spikes_generator
        rate = 40.0 # TODO: this is the frequency in Hz (40 spikes/s), right?
        start = 50.0 # latency of first spike in ms, represents the beginning of the simulation relative to trial start
        number_of_neurons = 100
        trial_duration = stop = 1000.0 # trial duration in ms
        spikes = poisson_spikes_generator(rate, start, stop, number_of_neurons, trial_duration)
        print("Spikes have been generated:")
        print(spikes)
        print(type(spikes['senders']))

        # file: save spikes in json
        from src.file_handling import file_handling
        spikes_file_name = file_handling.save_to_file(spikes, 'spikes/spikes_')

        # connection
        from src.nest.importer.spike_train_import import import_spike_train
        from src.connection.insert import insert_row
        try:
            connection = create_connection('data/db/database.db')
            if connection:
                save_spike_sql = " \
                                    INSERT INTO spikes(filename, updated) \
                                    VALUES(?,?) \
                                    ; \
                                "
                values_to_insert = (spikes_file_name, 1)
                insert_row(connection, save_spike_sql, values_to_insert)
                close_connection(connection)
                print("Spikes saved to db")
        except:
            print("Error while saving spikes to db")

    else:
        print('Spikes already exist:')
        print(spikes)
    # nest: connect spikes to input neurons

    # spike_trains = spike_train_import.import_json('data/spikes/spikes_1617654915.json')

    # print(spike_trains[0])
    # input_neurons = nest.Create('iaf_psc_exp', len(spike_trains))
    # print(input_neurons)