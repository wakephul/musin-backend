import nest
from random import randint
from collections import defaultdict
from api.src.reset.reset import nest_reset

def generatePoissonSpikes(rate, start, number_of_neurons, trial_duration):
    print('generating poisson spikes')
    # TO DISCUSS: should we reset the nest kernel here?
    nest_reset(randint(0, 10000))
    spikes = nest.Create('poisson_generator',
                        params={'rate': rate,
                                'start': start,
                                'stop': trial_duration
                                }
                        )
    parrot_neurons = nest.Create('parrot_neuron', int(number_of_neurons))
    spike_detector = nest.Create('spike_detector')
    nest.Connect(spikes, parrot_neurons, 'all_to_all')
    nest.Connect(parrot_neurons, spike_detector, 'all_to_all')
    print('simulation started')
    nest.Simulate(trial_duration)
    print('spike detector status: ', nest.GetStatus(spike_detector))
    events = nest.GetStatus(spike_detector, keys="events")[0]
    print('events: ', events)

    ordered_events = defaultdict(list)
    for sender, time in zip(events['senders'], events['times']):
        print('sender-time: ', sender, time)
        (ordered_events[str(sender)]).append(time)

    return dict(ordered_events) # tempi ordinati sulla base dell'id del neurone che spara (chiave: id, valore: array di istanti temporali)

def generateSpikesFromTimes(times_dict):
    import numpy as np
    #neuron = nest.Create('iaf_cond_alpha')
    spikes = []
    for key, value in times_dict.items():
        spike_times = np.array(value)
        neuron_spikes = nest.Create('spike_generator',
                                    params={'spike_times': spike_times}
                                    )

        spikes.append(neuron_spikes[0])
    spikes = np.asarray(spikes)
    return tuple(spikes)