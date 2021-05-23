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

def poisson_spikes_generator_connected(rate, start, stop, number_of_neurons, trial_duration):
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
    events = nest.GetStatus(spike_detector)[0]['events']
    return events

def poisson_spikes_generator(rate, start, stop):
    spikes = nest.Create('poisson_generator',
                        params={'rate': rate,
                                'start' : start,
                                'stop' : stop
                                }
                        )
    return spikes


# from functions.file_handling import file_handling
# file_handling.ndarray_to_json(spikes, 'spikes/spikes_')