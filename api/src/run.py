import nest
nest.set_verbosity('M_ERROR')

from importlib import import_module

from api.src.reset.reset import nest_reset
from api.src.spikes.spikes import spikesValuesFromInput
from api.src.spikes.generate import generatePoissonSpikes, generateSpikesFromTimes
from api.src.spikes.edit import editSpikesForSimulation

from api.src.nest.simulation.results import manage_results

from api.models.inputs import Input

from api.src.managers import file_handling

def run_execution(params):
    # the structure is --> inputsMap: {input_code: [{network_code: side_index}]}
    print('running execution')
    spikes_times_for_inputs = {}
    
    
    for input_code in params['inputsMap']:
        input = Input.get_one(input_code)
        spikes_times_for_inputs[input_code] = {}
        spikes_values = spikesValuesFromInput(input)
        for spikes in spikes_values:
            nest_reset()
            rate = spikes['rate']
            start = spikes['first_spike_latency']
            number_of_neurons = spikes['number_of_neurons']
            trial_duration = spikes['trial_duration']
            #this will be a dictionary with sender(keys)-times(array values) pairs
            poisson_spikes = generatePoissonSpikes(rate, start, number_of_neurons, trial_duration)
            spikes_times_for_inputs[input_code] = poisson_spikes

    print('spikes_times_for_inputs: ', spikes_times_for_inputs)

    for network in params['networks']:
        nest_reset()
        parameters_dict = {parameter['name']: parameter['value'] for parameter in network['parameters']}
        test_types = [int(tt) for tt in parameters_dict['test_types'].split(',')]
        print('test_types: ', test_types)
        parameters_dict.pop('test_types')

        for key, value in parameters_dict.items():
            parameters_dict[key] = float(value)    
    
        parameters_dict['test_types'] = test_types

        duration = parameters_dict.get('t_stimulus_duration', 1000)
        sim_time = parameters_dict.get('sim_time', duration)
        train_time = parameters_dict.get('train_time', 0)
        test_time = parameters_dict.get('test_time', 20000)

        total_simulation_time = int(parameters_dict['test_time'])+int(parameters_dict['train_time'])
        trial_duration = int(parameters_dict['t_stimulus_end'])-int(parameters_dict['t_stimulus_start'])
        number_of_trials = int(total_simulation_time/trial_duration)

        print('inputsMap: ', params['inputsMap'])
        #TODO: manage difference if stimuli are merged or not
        # the structure for NON merged should be spikes = [[side_0_spikes, side_1_spikes, ..., side_n_spikes], [side_0_spikes, side_1_spikes, ..., side_n_spikes], ...
        # the structure for merged should be spikes = [[side_0_spikes, side_1_spikes, ..., side_n_spikes]]
        if params.get('merged', False):
            # merge the spikes for all inputs
            # TODO: implement this
            pass
        else:
            #spike has the same structure as inputMap, but with the spikes instead of the side_index
            spikes = {}
            for input_code in params['inputsMap']:
                spikes[input_code] = {network_code: [] for network_code in params['inputsMap'][input_code]}
                for network_code in params['inputsMap'][input_code]:
                    input_sides = params['inputsMap'][input_code][network_code]
                    for input_side in input_sides:
                        spikes_from_times = generateSpikesFromTimes(spikes_times_for_inputs[input_code])
                        spikes[input_code][network_code].append(spikes_from_times)

        input_for_network = {}
        for input_code in spikes:
            for network_code in spikes[input_code]:
                if network_code == network['code']:
                    input_for_network[input_code] = spikes[input_code][network_code]

        parameters_dict['imported_stimuli'] = input_for_network
        sides_sequence = editSpikesForSimulation(spikes=spikes, duration=duration, train_time=train_time, test_time=test_time, amount_of_test_types=len(test_types), amount_of_sides=network['sides'])
        print('sides_sequence: ', sides_sequence)
        parameters_dict['trials_side'] = sides_sequence

        parameters_dict['sim_time'] = max_time = sim_time*3 #TODO: discuss why this is needed
        print('parameters_dict: ', parameters_dict)

        simulation_results = {}
        try:
            data_path = f"simulations/output/{params['execution_code']}/nest_data/"
            file_handling.create_folder(data_path)
            nest.SetKernelStatus({'data_path': data_path})
            network_module = import_module('api.src.nest.networks.'+network['name'])
            print('RUNNING SIMULATION on network: ', network['name'])
            simulation_results = network_module.run(parameters_dict)
        except Exception as e:
            print(e)
            import traceback
            print(traceback.format_exc())

        print('simulation results:', simulation_results)

        results_management = manage_results(network['name'], simulation_results, params['execution_code'])

        print('results_management: ', results_management)

        return results_management
                