import nest
import random
import pdb

# ok qui quello che devo fare è differenziare i trial dx e sx. come lo faccio?
# prendo in input gli stimoli, la loro durata (che forse in realtà mi posso calcolare qui) e la durata della simulazione
# a quel punto genero un numero di booleani (random) pari al numero di stimoli che ci stanno in una simulazione
# uso questi booleani per definire se un trial è dx o sx
# ovvero: replico lo stimolo ma solo nei periodi in cui esiste
# ad esempio avrò A con tempi da 0 a 1000 e poi da 4000 a 5000, mentre B avrà tempi da 1000 a 4000 e poi da 5000 a 6000 e così via
def editSpikesForSimulation(spikes, durations, train_time, test_time, test_number):
    # import pdb
    # pdb.set_trace()
    number_of_train_stimuli = int(train_time/durations)
    number_of_test_stimuli = int(test_time/durations)
    train_trials = [True if x%2 else False for x in range(number_of_train_stimuli)]
    test_trials = [True if x%2 else False for x in range(number_of_test_stimuli)]
    random.seed(1234)
    random.shuffle(train_trials)
    random.shuffle(test_trials)
    print('TRAIN TRIALS', train_trials)
    print('TEST TRIALS', test_trials)
    #invece che usare un for lo faccio a mano per le due diverse popolazioni, mi sembra più facile da vedere e da capire
    #TODO: questo va decisamente reso automatico
    # spikes_A = spikes[0]
    # spikes_A_status = nest.GetStatus(spikes_A)
    # spikes_B = spikes[1]
    # spikes_B_status = nest.GetStatus(spikes_B)
    # for neuron_index, neuron in enumerate(spikes_A_status):
    #     new_spike_times = []
    #     spike_times = neuron['spike_times'].tolist()
    #     i=0

    #     for trial_index, trial in enumerate(train_trials):
    #         if trial:
    #             new_spike_times.extend(list(map(lambda x:(x+((trial_index+i)*durations)), spike_times)))
    #         i+=2

    #     for test_index in range(test_number):
    #         i=0
    #         for trial_index, trial in enumerate(test_trials):
    #             if trial:
    #                 new_spike_times.extend(list(map(lambda x:(x+(train_time*3)+(test_index*test_time*3)+((trial_index+i)*durations)), spike_times)))
    #             i+=2

    #     new_spike_times.sort()
    #     nest.SetStatus([spikes_A[neuron_index]], {'spike_times': new_spike_times})
    # spikes_A_status = nest.GetStatus(spikes_A)

    # for neuron_index, neuron in enumerate(spikes_B_status):
    #     new_spike_times = []
    #     spike_times = neuron['spike_times'].tolist()

    #     i=0
    #     for trial_index, trial in enumerate(train_trials):
    #         if not trial:
    #             new_spike_times.extend(list(map(lambda x:(x+((trial_index+i)*durations)), spike_times)))
    #         i+=2

    #     for test_index in range(test_number):
    #         i=0
    #         for trial_index, trial in enumerate(test_trials):
    #             if not trial:
    #                 new_spike_times.extend(list(map(lambda x:(x+(train_time*3)+(test_index*test_time*3)+((trial_index+i)*durations)), spike_times)))
    #             i+=2

    #     new_spike_times.sort()
    #     nest.SetStatus([spikes_B[neuron_index]], {'spike_times': new_spike_times})
    # spikes_B_status = nest.GetStatus(spikes_B)

    spike_types = [spikes[i] for i in range(len(spikes))]
    spike_types_status = [nest.GetStatus(spikes_type) for spikes_type in spike_types]

    for spikes_type_index, spikes_type in enumerate(spike_types):
        spikes_status = spike_types_status[spikes_type_index]

        for neuron_index, neuron in enumerate(spikes_status):
            new_spike_times = []
            spike_times = neuron['spike_times'].tolist()
            i = 0

            for trial_index, trial in enumerate(train_trials):
                if (trial and spikes_type_index == 0) or (not trial and spikes_type_index != 0):
                    new_spike_times.extend(list(map(lambda x:(x+((trial_index+i)*durations)), spike_times)))
                i += 2

            for test_index in range(test_number):
                i = 0
                for trial_index, trial in enumerate(test_trials):
                    if (trial and spikes_type_index == 0) or (not trial and spikes_type_index != 0):
                        new_spike_times.extend(list(map(lambda x:(x+(train_time*3)+(test_index*test_time*3)+((trial_index+i)*durations)), spike_times)))
                    i += 2

            new_spike_times.sort()
            nest.SetStatus([spikes_type[neuron_index]], {'spike_times': new_spike_times})

        spike_types_status[spikes_type_index] = nest.GetStatus(spikes_type)

    
    return train_trials+test_trials