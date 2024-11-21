import json
import pdb
import matplotlib.pyplot as plt
from src.file_handling.folder_handling import create_folder
import src.file_handling.images.plot_raster_plot as plot_raster_plot
import src.file_handling.images.plot_voltage_trace as plot_voltage_trace
from src.nest.plots.save import save_raster_results, save_voltage_results
from src.file_handling.images.edit import merge_plots

def generate_plots(plots_to_create = [], plots_folder = '', simulation_results = {}, train_time = 1000, test_time = 1000, test_number = 1, train = [], test = [], sides = []):
    
    if (not plots_to_create or not plots_folder or not simulation_results): return


    create_folder(plots_folder+'/values')
    create_folder(plots_folder+'/plots')

    for plot in plots_to_create:
        
        title = plot[0]
        if len(plot) > 2:
            title = title + '_' + plot[2]

        if plot[1] == 'raster':
            try:
                split_population = []
                if (len(plot) > 3 and plot[3] == 'split_population'):
                    split_population = [min(simulation_results[plot[4]]), max(simulation_results[plot[4]])]
                
                train_or_test = 'train'
                start_time = 0.0
                end_time = train_time
                _types = train

                if len(plot) > 2 and plot[2] == 'test':
                    for t in range(test_number):
                        _title=title+'_'+str(t)
                        train_or_test = 'test'
                        start_time = train_time+(test_time*(t))
                        end_time = train_time+(test_time*(t+1))
                        test_start_index = -int(test_time/1000)
                        _sides = sides[test_start_index:]
                        _types = test[(t*len(_sides)):((t+1)*len(_sides))]
                        plt.figure()
                        plot_raster_plot.from_device(simulation_results[plot[0]], False, title=_title, hist=True, xlim=(start_time, end_time), sides=_sides, _types=_types, split_population=split_population, train_or_test=train_or_test)
                        plt.savefig(plots_folder+'plots/'+_title+'.png')
                        plt.close()

                else:
                    train_start_index = int(train_time/1000)
                    _sides = sides[:train_start_index]
                    plt.figure()
                    _title=title+'_0'
                    plot_raster_plot.from_device(simulation_results[plot[0]], False, title=_title, hist=True, xlim=(start_time, end_time), sides=_sides, _types=_types, split_population=split_population, train_or_test=train_or_test)
                    plt.savefig(plots_folder+'plots/'+_title+'.png')
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
                plot_voltage_trace.from_device(simulation_results[plot[0]], None, title=_title, xlim=(start_time, end_time))
                plt.savefig(plots_folder+'plots/'+_title+'.png')
                plt.close()
            except:
                print('error while generating voltage trace: ', plot[0])

    merge_plots(plots_folder, plots_to_create, 'plots', 1+test_number, test_number)

def moving_average_plot(plot_data, plots_folder, plot_name, xlim = []):

    times = list(map(int, list(plot_data.keys())))
    values = list(plot_data.values())
    values = [x for _, x in sorted(zip(times, values))]
    times = sorted(times)

    window_size = 10
    i = window_size//2
    ma = []

    values = [0 for x in range(window_size//2)] + values + [0 for x in range(window_size//2)]

    while i < (len(values) - window_size//2):
        
        window = values[(i - window_size//2) : (i + window_size//2)]
        window_average = round(sum(window) / window_size, 2)
        
        ma.append(window_average)
        
        i += 1
    
    plt.figure()
    plt.title(plot_name)
    
    if xlim:
        plt.xlim(xlim)

    plt.plot(times, ma)
    plt.savefig(plots_folder+plot_name+'.png')

    return ma

def moving_average_plot_no_save(plot_data):

    times = list(map(int, list(plot_data.keys())))
    values = list(plot_data.values())
    values = [x for _, x in sorted(zip(times, values))]
    times = sorted(times)

    window_size = 5
    i = window_size//2
    ma = []

    values = [0 for x in range(window_size//2)] + values + [0 for x in range(window_size//2)]

    while i < (len(values) - window_size//2):
        
        window = values[(i - window_size//2) : (i + window_size//2)]
        window_average = round(sum(window) / window_size, 2)
        
        ma.append(window_average)
        
        i += 1

    return ma, times