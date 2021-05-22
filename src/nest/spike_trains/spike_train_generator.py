# import numpy
# from neuronpy.graphics import spikeplot

# #stabilire quanti trial voglio fare (ad esempio 100), in maniera tale da creare tutti gli spike anche nella loro "versione shiftata di 1 secondo"
# # quindi se abbiamo uno spike a 250ms dovremo averlo anche a 1250ms
# # questo lo facciamo in fase di importazione del json nella rete.

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

def poisson_spikes_generator(rate, start, stop, number_of_neurons, trial_duration):
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
    ev = nest.GetStatus(spike_detector)[0]['events']
    return ev

# from functions.file_handling import file_handling
# file_handling.ndarray_to_json(spikes, 'spikes/spikes_')