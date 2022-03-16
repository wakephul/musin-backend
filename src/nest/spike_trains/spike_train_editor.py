import nest
import random

# ok qui quello che devo fare è differenziare i trial dx e sx. come lo faccio?
# prendo in input gli stimoli, la loro durata (che forse in realtà mi posso calcolare qui) e la durata della simulazione
# a quel punto genero un numero di booleani (random) pari al numero di stimoli che ci stanno in una simulazione
# uso questi booleani per definire se un trial è dx o sx
# ovvero: replico lo stimolo ma solo nei periodi in cui esiste
# ad esempio avrò A con tempi da 0 a 1000 e poi da 4000 a 5000, mentre B avrà tempi da 1000 a 4000 e poi da 5000 a 6000 e così via
def spikes_for_simulation(spikes, durations, simulation_time):
    number_of_stimuli_in_simulation = int(simulation_time/durations)
    trials = [True if x%2 else False for x in range(number_of_stimuli_in_simulation)]
    random.shuffle(trials)
    print(trials)
    #invece che usare un for lo faccio a mano per le due diverse popolazioni, mi sembra più facile da vedere e da capire
    spikes_A = spikes[0]
    spikes_A_status = nest.GetStatus(spikes_A)
    spikes_B = spikes[1]
    spikes_B_status = nest.GetStatus(spikes_B)
    for neuron_index, neuron in enumerate(spikes_A_status):
        new_spike_times = []
        spike_times = neuron['spike_times'].tolist() # @toDiscuss: è normale che ciclandoli io abbia il primo tempo che è sempre successivo a quello del neurone precedente?
        # print(spike_times)
        for trial_index, trial in enumerate(trials):
            if trial:
                new_spike_times.extend(list(map(lambda x:(x+(trial_index*durations)), spike_times)))
        nest.SetStatus([spikes_A[neuron_index]], {'spike_times': new_spike_times})
    spikes_A_status = nest.GetStatus(spikes_A)
    # print(spikes_A_status[0])

    for neuron_index, neuron in enumerate(spikes_B_status):
        new_spike_times = []
        spike_times = neuron['spike_times'].tolist()
        for trial_index, trial in enumerate(trials):
            if not trial:
                new_spike_times.extend(list(map(lambda x:(x+(trial_index*durations)), spike_times)))
        nest.SetStatus([spikes_B[neuron_index]], {'spike_times': new_spike_times})
    spikes_B_status = nest.GetStatus(spikes_B)
    # print(spikes_B_status[0])