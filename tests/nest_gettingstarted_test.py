import nest
import nest.voltage_trace
nest.ResetKernel()

neuron = nest.Create('iaf_psc_exp')
spikegenerator = nest.Create('spike_generator')
voltmeter = nest.Create('voltmeter')
nest.SetStatus(spikegenerator, {'spike_times': [10.0, 50.0]})
nest.Connect(spikegenerator, neuron, syn_spec={'weight': 1e3})
nest.Connect(voltmeter, neuron)
nest.Simulate(100.0)

nest.voltage_trace.from_device(voltmeter)
nest.voltage_trace.show()