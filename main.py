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
        from src.nest.spike_trains.spike_train_generator import poisson_spikes_generator_parrot
        rate = 40.0
        start = 50.0 # latency of first spike in ms, represents the beginning of the simulation relative to trial start
        number_of_neurons = 100
        trial_duration = stop = 1000.0 # trial duration in ms

        spikes = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)

        # questo deve essere letto da N spike generators (tanti quanti i parrot neurons), il cui output diventerà l'input della rete
        # ciascuno spike generator avrà la sua lista di spike times 
        # con un nest.setStatus possiamo far generare a ciascuno spike generator gli spikes con i tempi corretti

        # spikes = poisson_spikes_generator(rate, start, stop)
        
        # N_group_A = int(brian_params['N_Excit'] * brian_params['f_Subpop_size']) # size of the excitatory subpopulation sensitive to stimulus A
        # spikes = poisson_spikes_generator_brian(N_group_A)
        # print("Spikes have been generated:")
        # print(spikes)

        # spikes = (1427, 1428, 1429, 1430, 1431, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447, 1448, 1449, 1450, 1451, 1452, 1453, 1454, 1455, 1456, 1457, 1458, 1459, 1460, 1461, 1462, 1463, 1464, 1465, 1466, 1467, 1468, 1469, 1470, 1471, 1472, 1473, 1474, 1475, 1476, 1477, 1478, 1479, 1480, 1481, 1482, 1483, 1484, 1485, 1486, 1487, 1488, 1489, 1490, 1491, 1492, 1493, 1494, 1495, 1496, 1497, 1498, 1499, 1500, 1501, 1502, 1503, 1504, 1505, 1506, 1507, 1508, 1509, 1510, 1511)

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

    brian_params['imported_stimulus_A'] = spike_trains
    print("params", brian_params)

    brian_nest.run(brian_params)

    # input_neurons = nest.Create('iaf_psc_exp', len(spike_trains))
    # print(input_neurons)