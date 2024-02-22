from api.src.combinations.combinations import generateCombinations

def spikesValuesFromInput(input):
    spikes_values = {
            'rate': [],
            'first_spike_latency': [],
            'number_of_neurons': [],
            'trial_duration': []
        }
    if input['multiple']:
        for value in range(
                        int(input['rate_start']*1000),
                        int(input['rate_stop']*1000),
                        int(input['rate_step']*1000)
                    ):
            spikes_values['rate'].append(float(value/1000))
        for value in range(
                        int(input['first_spike_latency_start']*1000),
                        int(input['first_spike_latency_end']*1000),
                        int(input['first_spike_latency_step']*1000)
                    ):
            spikes_values['first_spike_latency'].append(float(value/1000))
        for value in range(
                        int(input['number_of_neurons_start']*1000),
                        int(input['number_of_neurons_end']*1000),
                        int(input['number_of_neurons_step']*1000)
                    ):
            spikes_values['number_of_neurons'].append(float(value/1000))
        for value in range(
                        int(input['trial_duration_start']*1000),
                        int(input['trial_duration_end']*1000),
                        int(input['trial_duration_step']*1000)
                    ):
            spikes_values['trial_duration'].append(float(value/1000))
    
    else:
        spikes_values['rate'] = [float(input['rate_start'])]
        spikes_values['first_spike_latency'] = [float(input['first_spike_latency_start'])]
        spikes_values['number_of_neurons'] = [float(input['number_of_neurons_start'])]
        spikes_values['trial_duration'] = [float(input['trial_duration_start'])]
    
    spikes_combinations = generateCombinations(spikes_values)
    return spikes_combinations