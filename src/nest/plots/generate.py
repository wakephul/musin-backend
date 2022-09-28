import json
import pdb
import matplotlib.pyplot as plt
from src.file_handling.folder_handling import create_folder
import src.file_handling.images.plot_raster_plot as plot_raster_plot
import src.file_handling.images.plot_voltage_trace as plot_voltage_trace
from src.nest.plots.save import save_raster_results, save_voltage_results
from src.file_handling.images.edit import merge_plots

def generate_plots(plots_to_create = [], output_folder = '', simulation_results = {}, train_time = 1000, test_time = 1000, train = [], test = [], sides = []):
    
    if (not plots_to_create or not output_folder or not simulation_results): return


    create_folder(output_folder+'/values')
    create_folder(output_folder+'/plots')

    for plot in plots_to_create:
        plt.figure()
        
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
                    train_or_test = 'test'
                    start_time = train_time
                    end_time = train_time+test_time
                    _types = test
                    test_start_index = -int(test_time/3000)
                    _sides = sides[test_start_index:]
                else:
                    train_start_index = int(train_time/3000)
                    _sides = sides[:train_start_index]

                plot_raster_plot.from_device(simulation_results[plot[0]], False, title=title, hist=True, xlim=(start_time, end_time), sides=_sides, _types=_types, split_population=split_population, train_or_test=train_or_test)

            except Exception as e:
                print('error while generating raster: ', plot[0])
                print(e)
                import traceback
                print(traceback.format_exc())

            # save_raster_results(simulation_results, plot)

        elif plot[1] == 'voltage':
            try:
                plot_voltage_trace.from_device(simulation_results[plot[0]], None, title=plot[0], xlim=(start_time, end_time))
            except:
                print('error while generating voltage trace: ', plot[0])
            
            # save_voltage_results(simulation_results, plot, output_folder)

        plt.savefig(output_folder+'plots/'+title+'.png')
        plt.close()
        # plt.show()

    # plt.figure()
    # plot_raster_plot.from_device(simulation_results['spike_monitor_GR'], False, hist=False, xlim =(0, 1000))
    # plt.savefig(output_folder+'plots/gr_0-1000.png')
    # plt.close()
    # plt.figure()
    # plot_raster_plot.from_device(simulation_results['spike_monitor_GR'], False, hist=False, xlim =(3000, 4000))
    # plt.savefig(output_folder+'plots/gr_3000-4000.png')
    # plt.close()

    #faccio un merge dei vari file per semplicità di visualizzazione
    merge_plots(output_folder, plots_to_create, 'plots')

def moving_average_plot(plot_data, output_folder, plot_name, xlim = []):

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