class BaseNetwork():
    def __init__(self, **execution_params):
        self.name = "base_network"
        self.execution_params = execution_params
        self.output_folder = ''

    def set_simulation_folder(self, simulation_folder):
        self.input_folder = f"{simulation_folder}/input/"
        self.output_folder = f"{simulation_folder}/output/"
        self.plots_folder = f"{self.output_folder}plots/"
        self.files_folder = f"{self.output_folder}files/"
        self.nest_data_folder = f"{self.files_folder}nest/"
    
    @staticmethod
    def run():
        raise NotImplementedError("This method should be implemented in the child class")
    
    @staticmethod
    def get_spikes():
        raise NotImplementedError("This method should be implemented in the child class")