import matplotlib.pyplot as plt
from api.src.managers.images.edit import merge_plots
import api.src.managers.images.plot_raster_plot as plot_raster_plot
import api.src.managers.images.plot_voltage_trace as plot_voltage_trace

class BaseNetwork():
    def __init__(self, **execution_params):
        self.name = "base_network"
        self.execution_params = execution_params
        self.output_folder = ''
        self.plots_to_create = []

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
    
    def generate_plots(self):

        print('generating plots')

        for plot in self.plots_to_create:    
            title = plot[0]
            if len(plot) > 2:
                title = title + '_' + plot[2]

            if plot[1] == 'raster':
                try:
                    split_population = []
                    if (len(plot) > 3 and plot[3] == 'split_population'):
                        split_population = [min(self.simulation_results[plot[4]]), max(self.simulation_results[plot[4]])]
                    
                    start_time = 0.0
                    end_time = self.train_time
                    _types = self.train

                    if len(plot) > 2 and plot[2] == 'test':
                        for t in range(self.test_number):
                            _title=title+'_'+str(t)
                            start_time = self.train_time+(self.test_time*(t))
                            end_time = self.train_time+(self.test_time*(t+1))
                            index_start = int(start_time/1000)
                            index_end = int(end_time/1000)
                            _sides = self.trials_side[index_start:index_end]
                            _types = self.test[(t*len(_sides)):((t+1)*len(_sides))]
                            
                            plt.figure()    
                            plot_raster_plot.from_device(self.simulation_results[plot[0]], False, title=_title, hist=True, xlim=(start_time, end_time), sides=_sides, _types=_types, split_population=split_population, train_or_test='test')
                            plt.savefig(self.plots_folder+_title+'.png')
                            plt.close()

                    else:
                        index_start = int(start_time/1000)
                        index_end = int(end_time/1000)
                        _sides = self.trials_side[index_start:index_end]
                        _title=title+'_0'

                        plt.figure()
                        plot_raster_plot.from_device(self.simulation_results[plot[0]], False, title=_title, hist=True, xlim=(start_time, end_time), sides=_sides, _types=_types, split_population=split_population, train_or_test='train')
                        plt.savefig(self.plots_folder+_title+'.png')
                        plt.close()

                except Exception as e:
                    print('error while generating raster: ', plot[0])
                    print(e)
                    import traceback
                    print(traceback.format_exc())

                # save_raster_results(simulation_results, plot)

            elif plot[1] == 'voltage':
                try:
                    plt.figure()
                    _title=plot[0]
                    plot_voltage_trace.from_device(self.simulation_results[plot[0]], None, title=_title, xlim=(start_time, end_time))
                    plt.savefig(self.plots_folder+_title+'.png')
                    plt.close()
                except:
                    print('error while generating voltage trace: ', plot[0])

        merge_plots(self.plots_folder, self.plots_to_create, 'plots', self.test_number+1, self.test_number)