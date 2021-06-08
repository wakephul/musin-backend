# import numpy
# from neuronpy.graphics import spikeplot

# spikes = []
# num_neurons = 100
# num_spikes_per_neuron = 21
# frequency = 40

# for i in range(neurons):
#     isi = numpy.random.poisson(frequency, num_spikes_per_neuron)
#     spikes.append(numpy.cumsum(isi))

# sp = spikeplot.SpikePlot()
# sp.plot_spikes(spikes)

import nest
from collections import defaultdict

def poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration):
    spikes = nest.Create('poisson_generator',
                        params={'rate': rate,
                                'start' : start,
                                'stop' : stop
                                }
                        )
    parrot_neurons = nest.Create('parrot_neuron', number_of_neurons)
    spike_detector = nest.Create('spike_detector')
    nest.Connect(spikes, parrot_neurons, 'all_to_all')
    nest.Connect(parrot_neurons, spike_detector, 'all_to_all')
    nest.Simulate(trial_duration)
    events = nest.GetStatus(spike_detector ,keys="events")[0]
    # ritornare i tempi ordinati sulla base dell'id del neurone che spara (chiave: id, valore: array di istanti temporali)

    ordered_events = defaultdict(list)
    for sender, time in zip(events['senders'], events['times']):
        (ordered_events[str(sender)]).append(time)

    return dict(ordered_events)

def poisson_spikes_generator_brian(size):
    spikes = nest.Create('poisson_generator', size)
    return spikes

#rate = 40.0
#start = 50.0 # latency of first spike in ms, represents the beginning of the simulation relative to trial start
#number_of_neurons = 100
#trial_duration = stop = 1000.0 # trial duration in ms
#poisson_spikes_generator_connected(rate, start, stop, number_of_neurons, trial_duration)