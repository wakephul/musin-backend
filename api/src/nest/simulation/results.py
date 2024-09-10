import nest
nest.set_verbosity('M_ERROR')

from api.src.managers import file_handling
from api.src.nest.plots.generate import generate_plots

from importlib import import_module

def create_output_folder(execution_code):

    output_folder = f"simulations/output/{execution_code}/plots"
    output_folder = file_handling.create_folder(output_folder)

    return output_folder