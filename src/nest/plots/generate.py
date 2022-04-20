import nest
from src.file_handling import plot_voltage_trace, plot_raster_plot
from src.file_handling.file_handling import *
from src.file_handling.support_file import new_row
import matplotlib.pyplot as plt


def generate_plots(plots_to_create = [], output_folder = '', simulation_results = []):
    
    if (not plots_to_create or not output_folder or not simulation_results): return

    for plot in plots_to_create:
        plt.figure()
        if plot[1] == 'raster':
            try:
                plot_raster_plot.from_device(simulation_results[plot[0]], False, title=plot[0], hist=False, xlim =(0, data['max_sim_time']))
            except:
                print('error while generating raster: ', plot[0])

            results_dict_complete = nest.GetStatus(simulation_results[plot[0]])[0]	
            

            senders = [x for _, x in sorted(zip(results_dict_complete['events']['times'], results_dict_complete['events']['senders']))]
            times = sorted (results_dict_complete['events']['times'])

            from src.file_handling.folder_handling import create_folder
            create_folder(output_folder+'/values')
            create_folder(output_folder+'/merged_plots')

            with open(output_folder+'values/'+plot[0]+'.csv', 'w+') as file:
                file.write(','.join(['sender', 'time'])+'\n')
                for index in range(len(senders)):
                    file.write(','.join([str(senders[index]), str(5 * round(times[index]/5))])+'\n')

        elif plot[1] == 'voltage':
            try:
                plot_voltage_trace.from_device(simulation_results[plot[0]], None, title=plot[0])
            except:
                print('error while generating voltage trace: ', plot[0])
            
            results_dict_complete = nest.GetStatus(simulation_results[plot[0]])[0]

            # write to csv to eventually allow it to be used for js plotting
            with open(output_folder+'values/'+plot[0]+'.csv', 'w+') as file:
                file.write(','.join(['sender', 'voltage', 'time'])+'\n')
                for index in range(len(results_dict_complete['events']['senders'])):
                    file.write(','.join([str(results_dict_complete['events']['senders'][index]), str(results_dict_complete['events']['V_m'][index]), str(results_dict_complete['events']['times'][index])])+'\n')

        plt.savefig(output_folder+'merged_plots/'+plot[0]+'.png')
        plt.show()

    #faccio un bel merge dei vari file per semplicità di visualizzazione
    from src.file_handling.merge_images import merge_images
    filenames = [output_folder+'merged_plots/'+plot[0]+'.png' for plot in plots_to_create]
    merge_images(filenames, [500, 500], output_folder+'voltage_and_dynamics.jpg', 3)

    events_A = nest.GetStatus(simulation_results["spike_monitor_A"], "n_events")[0]
    events_B = nest.GetStatus(simulation_results["spike_monitor_B"], "n_events")[0]

    senders_spike_monitor_A = nest.GetStatus(simulation_results["spike_monitor_A"], 'events')[0]['senders']
    times_spike_monitor_A = nest.GetStatus(simulation_results["spike_monitor_A"], 'events')[0]['times']

    # * in questa implementazione quello che faccio è assegnare a ciascun id i propri tempi di sparo
    # monitored_spikes_A = {}
    # for index, sender in enumerate(senders_spike_monitor_A):
    # 	if sender in monitored_spikes_A:
    # 		monitored_spikes_A[sender].append(times_spike_monitor_A[index])
    # 	else:
    # 		monitored_spikes_A[sender] = [times_spike_monitor_A[index]]
    # for id in monitored_spikes_A:
    # 	monitored_spikes_A[id].sort()
    # print('monitored_spikes_A', monitored_spikes_A)

    # * penso che dovrebbe funzionare al contrario, ovvero dovrei assegnare l'elenco degli id a ciascun tempo
    # * in questo modo potrei dividerli già sulla base dei bin (forse), oppure calcolare e poi proseguire con il calcolo
    bin_size = 5 # value in ms
    max_time = int(data['max_sim_time'])
    bins = list(range(bin_size, max_time+1, bin_size))
    monitored_times_A = {}
    for index, time in enumerate(times_spike_monitor_A):
        bin_index = np.digitize(time, bins, right=True)
        if bin_index < len(bins):
            bin_time = np.take(bins, bin_index)
            if bin_time in monitored_times_A:
                monitored_times_A[bin_time].append(senders_spike_monitor_A[index])
            else:
                monitored_times_A[bin_time] = [senders_spike_monitor_A[index]]
    for id in monitored_times_A:
        monitored_times_A[id].sort()
    # print('monitored_times_A', monitored_times_A)
    # * qui fondamentalmente ho un elenco di tutti gli spari che si vedono in ciascun bin
    # * il problema è che ci sono un sacco di duplicati in ciascun bin, cioè mi pare che la frequenza sia un po' alta se ogni neurone spara 2 o 3 volte ogni 5ms
    bin_rates = {}
    for bin_time, spikes_list in monitored_times_A.items():
        bin_rate = len(spikes_list) * 1000 / (bin_size * len(simulation_results["idx_monitored_neurons_A"]))
        bin_rates[bin_time] = bin_rate
        # print(f'rate nel bin {bin_time}: {bin_rate} Hz')

    print('bin_rates', bin_rates)

    # import h5py
    # with h5py.File(output_folder+'test.hdf5', 'w') as f:
    # 	dset = f.create_dataset("default", data = bin_rates)

    rate_A = events_A / data['max_sim_time'] * 1000.0 / len(simulation_results["idx_monitored_neurons_A"])
    rate_B = events_B / data['max_sim_time'] * 1000.0 / len(simulation_results["idx_monitored_neurons_B"])

    print("Population A rate   : %.2f Hz" % rate_A)
    print("Population B rate   : %.2f Hz" % rate_B)

    if data['execution']:
        data['execution'].append(rate_A)
        data['execution'].append(rate_B)
        data['execution'].pop(0)
        new_row('', 'output/multiple_trials/support.csv', data['execution'])
    else:
        append_to_file(output_folder+'trial_notes.txt', f"\n\nPopulation A rate: {rate_A:.2f} Hz\nPopulation B rate: {rate_B:.2f} Hz")