import nest
nest.set_verbosity('M_ERROR')

from random import randint

from importlib import import_module

from api.src.reset.reset import nest_reset
from api.src.spikes.spikes import spikesValuesFromInput
from api.src.spikes.generate import generatePoissonSpikes, generateSpikesFromTimes
from api.src.spikes.edit import editSpikesForSimulation

from api.models.inputs import Input

from api.models.networks import Network, NetworkParameter

def run_execution(params):
    # the structure is --> inputsMap: {input_code: [{network_code: side_index}]}
    print('running execution')
    spikes_times_for_inputs = {}
    
    for input_code in params['inputsMap']:
        input = Input.get_one(input_code)
        spikes_times_for_inputs[input_code] = {}
        spikes_values = spikesValuesFromInput(input)
        for spikes in spikes_values:
            rate = spikes['rate']
            start = spikes['first_spike_latency']
            number_of_neurons = spikes['number_of_neurons']
            trial_duration = spikes['trial_duration']
            #this will be a dictionary with sender(keys)-times(array values) pairs
            poisson_spikes = generatePoissonSpikes(rate, start, number_of_neurons, trial_duration)
            spikes_times_for_inputs[input_code] = poisson_spikes

    print('spikes_times_for_inputs: ', spikes_times_for_inputs)

    # now i need to define the side that will be active, for each network, at each trial. all networks will have the same side active at each trial so i only need to define the sequence of sides once.
    # the structure is --> sides_sequence: {network_code: [side_index]}
    # each trial has a specific length, and then i need to create the spikes for each side, for each network, for each trial, depending on the side that is active
    # the structure is --> trials_side: [side_index_for_trial_0, side_index_for_trial_1, ..., side_index_for_trial_n]
    # the structure is --> spikes_times: {network_code: [[side_0_spikes, side_1_spikes, ..., side_n_spikes]]}

    max_number_of_sides = 0
    for network in params['networks']:
        max_number_of_sides = Network.get_one(network['code']).sides if Network.get_one(network['code']).sides > max_number_of_sides else max_number_of_sides
    
    sides_sequence = [randint(0, max_number_of_sides-1) for i in range(params['number_of_trials'])]

    print('sides_sequence: ', sides_sequence)


    #if they are paired, then they will be put on the same side at each trial. If they are not paired, they will be put on random sides
    
    # #TODO: save spikes_times in the database

    # #TODO: merge whatever has to be merged

    # #TO DISCUSS: what is this supposed to be?
    # number_of_cortex = 2
    # for cortex_id in range(1, (number_of_cortex+1)):
    #     nest_reset(randint(0, 10000))
        
    #     for network in params['networks']:
    #         networkParametersFromDB = NetworkParameter.get_by_network_code(network['code'])
    #         networkParameters = {parameter['name']: parameter['value'] for parameter in networkParametersFromDB}
    #         print('network parameters: ', networkParameters)
    #         spikes = []
    #         for side_index, side in enumerate(network['inputsForSides']):
    #             if len(side['inputs']) > 0:
    #                 #TODO: this is hardcoded right now, as it's directly dependent on the merging of the spikes
    #                 input_code = side['inputs'][0]
    #                 spikes.append(generateSpikesFromTimes(spikes_times[network['code']][side_index][input_code][0]))

    #             else:
    #                 spikes.append([]) #right now i need this because the network module expects a list for each side
    #         print('spikes: ', spikes)

    #         networkParameters['imported_stimuli'] = spikes
    #         duration = int(networkParametersFromDB['t_stimulus_duration']) if 't_stimulus_duration' in networkParametersFromDB else 1000
    #         sim_time = int(networkParametersFromDB['sim_time']) if 'sim_time' in networkParametersFromDB else duration
    #         train_time = int(networkParametersFromDB['train_time']) if 'train_time' in networkParametersFromDB else 0
    #         test_time = int(networkParametersFromDB['test_time']) if 'test_time' in networkParametersFromDB else 20000
    #         test_number = int(networkParametersFromDB['test_number']) if 'test_number' in networkParametersFromDB else 1
    #         trials_side = editSpikesForSimulation(spikes, duration, train_time/3, test_time/3, test_number)
    #         print('trials_side: ', trials_side)

    #         #TODO: do not hardcode this, save it in the database
    #         import json
    #         with open(f"api/src/nest/networks/{network['name']}.json", 'r') as file:
    #             data = json.load(file)
            
    #         for key, value in data.items():
    #             networkParameters[key] = value
    #         print('network parameters: ', networkParameters)
    #         print('importe_stimuli: ', networkParameters['imported_stimuli'])

    #         #TODO: save trials_side in the database

    #         networkParameters['sim_time'] = max_time = sim_time*3

    #         simulation_results = {}
    #         try:
    #             network_module = import_module('api.src.nest.networks.'+network['name'])
    #             print('RUNNING SIMULATION on network: ', network['name'])
    #             simulation_results = network_module.run(networkParameters)
    #         except Exception as e:
    #             print(e)
    #             import traceback
    #             print(traceback.format_exc())

    #         print('simulaiton results:', simulation_results)

    #         # # pdb.set_trace()
            
    #         # plots_to_create = plots_config[network] if (network in plots_config) else None
    #         # if plots_to_create:
    #         #     generate_plots(plots_to_create, output_folder, simulation_results, train_time=train_time, test_time=test_time, test_number=test_number, train=simulation_results["train"], test=simulation_results["test"], sides=trials_side)

    #         # plots_to_merge = plots_merge_config[network] if (network in plots_merge_config) else None
            
    #         #TO DISCUSS: questo è tutto hardcodato, probabilmente avrebbe senso avere un file "extra" per ciascuna rete, in cui si definisce il preprocessing e il postprocessing
    #         # senders_spike_monitor_A = nest.GetStatus(simulation_results["spike_monitor_A"], 'events')[0]['senders']
    #         # times_spike_monitor_A = nest.GetStatus(simulation_results["spike_monitor_A"], 'events')[0]['times']
    #         # senders_spike_monitor_B = nest.GetStatus(simulation_results["spike_monitor_B"], 'events')[0]['senders']
    #         # times_spike_monitor_B = nest.GetStatus(simulation_results["spike_monitor_B"], 'events')[0]['times']

    #         # bin_size = 5
            
    #         # bin_rates_A_complete = calculate_bins(senders_spike_monitor_A, times_spike_monitor_A, len(simulation_results["idx_monitored_neurons_A"]), bin_size, train_time, train_time+(test_time*test_number), test_number)
    #         # bin_rates_B_complete = calculate_bins(senders_spike_monitor_B, times_spike_monitor_B, len(simulation_results["idx_monitored_neurons_B"]), bin_size, train_time, train_time+(test_time*test_number), test_number)


    #         # for tt_index, tt in enumerate(test_types):
    #         #     bin_rates_a_portion = bin_rates_A_complete[tt_index]
    #         #     bin_rates_b_portion = bin_rates_B_complete[tt_index]
    #         #     json_title_a = file_handling.dict_to_json(bin_rates_a_portion, output_folder+'bin_rates_A_test_'+str(tt_index))
    #         #     json_title_b = file_handling.dict_to_json(bin_rates_b_portion, output_folder+'bin_rates_B_test_'+str(tt_index))
                