'''
from src.nest.spike_trains.spike_train_generator import poisson_spikes_generator_parrot, spike_generator_from_times
rate = 40.0
start = 50.0 # latency of first spike in ms, represents the beginning of the simulation relative to trial start
number_of_neurons = 100
trial_duration = stop = 1000.0 # trial duration in ms

spike_times = poisson_spikes_generator_parrot(rate, start, stop, number_of_neurons, trial_duration)

spikes = spike_generator_from_times(spike_times)

print(spikes)
'''
import nest
import numpy as np

n = nest.Create('iaf_cond_alpha',  params = {'tau_syn_ex': 1.0, 'V_reset': -70.0})

m = nest.Create('multimeter', params = {'withtime': True, 'interval': 0.1, 'record_from': ['V_m', 'g_ex', 'g_in']})

# Create spike generators and connect
gex = nest.Create('spike_generator', params = {'spike_times': np.array([10.0, 20.0, 50.0])})
gin = nest.Create('spike_generator',  params = {'spike_times': np.array([15.0, 25.0, 55.0])})

con1 = nest.Connect(gex, n) # excitatory
con2 = nest.Connect(gin, n) # inhibitory
con3 = nest.Connect(m, n)

print(nest.GetStatus(gex))
print(gin)
print(con1)
print(con2)
print(con3)

nest.Simulate(100)

# obtain and display data
events = nest.GetStatus(m)[0]['events']

#print(events)