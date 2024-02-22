import nest
nest.set_verbosity('M_ERROR')

from api.src.spikes.spikes import spikesValuesFromInput
from api.src.spikes.generate import generatePoissonSpikes

def run_execution(params):
    spikes_values = {}
    for network in params['networks']:
        network_code = network['code']
        for side in network['inputsForSides']:
            for input in side:
                spikes_values = spikesValuesFromInput(input)
                for spikes in spikes_values:
                        rate = spikes['rate']
                        start = spikes['first_spike_latency']
                        number_of_neurons = spikes['number_of_neurons']
                        trial_duration = spikes['trial_duration']
                        spikesTimes = []
                        number_of_sides = 2 #TODO: to change with the number of sides. Right now, a stimulus is a side. They can be merged or not
                        for i in range(number_of_sides):
                            spikesTimes.append(generatePoissonSpikes(rate, start, number_of_neurons, trial_duration))

                        print('spikesTimes: ', spikesTimes)

    # # Save execution results to a file
    # result_dir = 'results'
    # if not os.path.exists(result_dir):
    #     os.makedirs(result_dir)
    # result_path = os.path.join(result_dir, 'execution_result.txt')
    # with open(result_path, 'w') as f:
    #     f.write(execution_results)

    # # Save execution image to a file
    # image_dir = 'images'
    # if not os.path.exists(image_dir):
    #     os.makedirs(image_dir)
    # image_path = os.path.join(image_dir, 'execution_image.png')
    # with open(image_path, 'wb') as f:
    #     f.write(execution_image)

    # # Store file paths in the database
    # result = ExecutionResult(result_path=result_path, image_path=image_path)