import nest
nest.set_verbosity('M_ERROR')

from api.src.managers import file_handling
from api.src.nest.plots.generate import generate_plots

from importlib import import_module

def manage_results(network_name, results, execution_code):
    if not results:
        return False
    
    train_time = results["train_time"]
    test_time = results["test_time"]
    test_number = results["test_time"]/results["stimulus_duration"]
    train = results["train"]
    test = results["test"]
    sides = results["trials_side"]
    test_types = results["test_types"]

    output_folder = f"simulations/output/{execution_code}/plots/"

    output_folder = file_handling.create_folder(output_folder)

    plots_config = file_handling.read_json("api/data/config/plots/config.json")
    
    #if they are paired, then they will be put on the same side at each trial. If they are not paired, they will be put on random sides          
    plots_to_create = plots_config.get(network_name, {}).get('plots', None)

    if plots_to_create:
        generate_plots(plots_to_create, output_folder, results, train_time=train_time, test_time=test_time, test_number=test_number, train=train, test=test, sides=sides)
        # plots_to_merge = plots_config.get(network_name, {}).get('plots_merge', None) #TODO: what was this for?

    try:
        network_postprocessing_module = import_module('api.src.nest.postprocessing.'+network_name)
        network_postprocessing_module.postprocessing(results, test_types, train_time, test_time, test_number, output_folder)
    except Exception as e:
        print(e)
        import traceback
        print(traceback.format_exc())

    return True