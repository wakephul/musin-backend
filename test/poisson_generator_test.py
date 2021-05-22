import nest
import matplotlib.pyplot as plt

frequency = 40.0 # Hz
rate = 40.0 # TODO: this is the frequency in Hz (40 spikes/s), right ?
start = 50.0 # latency of first spike in ms, represents the beginning of the simulation relative to trial start
stop = 1000.0 # trial duration in ms
number_of_neurons = 100
trial_duration = 1000.0 # ms

g = nest.Create('poisson_generator',
                params={'rate': rate,
                        'start' : start,
                        'stop' : stop
                        }
                )
p = nest.Create('parrot_neuron', number_of_neurons)
s = nest.Create('spike_detector')

nest.Connect(g, p, 'all_to_all')
nest.Connect(p, s, 'all_to_all')

nest.Simulate(trial_duration)
ev = nest.GetStatus(s)[0]['events']
plt.plot(ev['times'], ev['senders'] - min(ev['senders']), 'o')
plt.xlim([0, trial_duration])
plt.ylim([-1, number_of_neurons+1])
plt.xlabel('Spikes')
plt.ylabel('Neurons')
plt.title('Spike trains for each target')

# plt.show()
# print(p)
# print(s)
print(ev)