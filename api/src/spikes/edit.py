import nest
nest.set_verbosity('M_ERROR')

import random
import pdb

# ok qui quello che devo fare è differenziare i trial dx e sx. come lo faccio?
# prendo in input gli stimoli, la loro durata (che forse in realtà mi posso calcolare qui) e la durata della simulazione
# a quel punto genero un numero di booleani (random) pari al numero di stimoli che ci stanno in una simulazione
# uso questi booleani per definire se un trial è dx o sx
# ovvero: replico lo stimolo ma solo nei periodi in cui esiste
# ad esempio avrò A con tempi da 0 a 1000 e poi da 4000 a 5000, mentre B avrà tempi da 1000 a 4000 e poi da 5000 a 6000 e così via
def editSpikesForSimulation(
        spikes=[],
        duration=0,
        train_time=0,
        test_time=0,
        amount_of_test_types=0,
        amount_of_sides=0,
    ):
    print('EDITING SPIKES FOR SIMULATION')
    amount_of_train_trials = int(train_time/duration)
    amount_of_test_trials = int(test_time/duration)
    train_sides_sequence = [random.randint(0, amount_of_sides-1) for x in range(amount_of_train_trials)]
    test_sides_sequence = [random.randint(0, amount_of_sides-1) for x in range(amount_of_test_trials)]
    random.seed(1234)
    random.shuffle(train_sides_sequence)
    random.shuffle(test_sides_sequence)
    print('TRAIN SIDES SEQUENCE', train_sides_sequence)
    print('AMOUNT OF TEST TYPES', amount_of_test_types)
    print('TEST SIDES SEQUENCE', test_sides_sequence)
    sequence = train_sides_sequence+(amount_of_test_types*test_sides_sequence)
    print('SEQUENCE', sequence)

    # the structure is --> spikes: {input_code: [{network_code: [neurons]}]}

    for input_code in spikes:
        print('INPUT CODE', input_code)
        for network_code in spikes[input_code]:
            print('NETWORK CODE', network_code)
            for network_side in range(len(spikes[input_code][network_code])):
                print('NETWORK SIDE', network_side)
                sequence_mask = [1 if x == network_side else 0 for x in sequence]
                # print('SEQUENCE MASK', sequence_mask)
                for neuron in spikes[input_code][network_code][network_side]:
                    neuron_status = nest.GetStatus([neuron])
                    # print('NEURON STATUS', neuron_status)
                    new_spike_times = []
                    spike_times = neuron_status[0]['spike_times'].tolist()
                    new_spike_times = [spike_time+(trial_index*duration) for spike_time in spike_times for trial_index, trial in enumerate(sequence_mask) if trial == 1]
                    new_spike_times.sort()
                    # print('NEW SPIKE TIMES', new_spike_times)
                    nest.SetStatus([neuron], {'spike_times': new_spike_times})
                    neuron_status_final = nest.GetStatus([neuron])
                    # print('NEURON STATUS FINAL', neuron_status_final)

    return sequence