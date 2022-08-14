import json
import pdb
import matplotlib.pyplot as plt
from src.file_handling.folder_handling import create_folder
import src.file_handling.images.plot_raster_plot as plot_raster_plot
import src.file_handling.images.plot_voltage_trace as plot_voltage_trace
from src.nest.plots.save import save_raster_results, save_voltage_results
from src.file_handling.images.edit import merge_plots

def generate_plots(plots_to_create = [], output_folder = '', simulation_results = {}, max_time = 1000):
    
    if (not plots_to_create or not output_folder or not simulation_results): return


    create_folder(output_folder+'/values')
    create_folder(output_folder+'/plots')

    for plot in plots_to_create:
        plt.figure()
        if plot[1] == 'raster':
            try:
                plot_raster_plot.from_device(simulation_results[plot[0]], False, title=plot[0], hist=True, xlim =(0, max_time))
            except:
                print('error while generating raster: ', plot[0])

            # save_raster_results(simulation_results, plot)

        elif plot[1] == 'voltage':
            try:
                plot_voltage_trace.from_device(simulation_results[plot[0]], None, title=plot[0], xlim=(0, max_time))
            except:
                print('error while generating voltage trace: ', plot[0])
            
            # save_voltage_results(simulation_results, plot, output_folder)

        plt.savefig(output_folder+'plots/'+plot[0]+'.png')
        # plt.show()

    #faccio un merge dei vari file per semplicità di visualizzazione
    merge_plots(output_folder, plots_to_create, 'plots')

def moving_average_plot(plot_data, output_folder, plot_name):

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
    plt.plot(times, ma)
    plt.savefig(output_folder+plot_name+'.png')

    return ma

def moving_average_plot_no_save(plot_data):

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

    return ma