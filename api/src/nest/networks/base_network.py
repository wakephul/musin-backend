class BaseNetwork():
    def __init__(self, **execution_params):
        self.name = "base_network"
        self.execution_params = execution_params
        self.output_folder = ''

    def set_output_folder(self, output_folder):
        self.output_folder = output_folder
    
    @staticmethod
    def run():
        raise NotImplementedError("This method should be implemented in the child class")
    
    @staticmethod
    def get_spikes():
        raise NotImplementedError("This method should be implemented in the child class")