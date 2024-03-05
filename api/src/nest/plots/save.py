import nest

def save_raster_results(simulation_results, plot, output_folder = ''):
    
    if (not output_folder): return

    results_dict_complete = nest.GetStatus(simulation_results[plot[0]])[0]	

    senders = [x for _, x in sorted(zip(results_dict_complete['events']['times'], results_dict_complete['events']['senders']))]
    times = sorted (results_dict_complete['events']['times'])

    with open(output_folder+'values/'+plot[0]+'.csv', 'w+') as file:
        file.write(','.join(['sender', 'time'])+'\n')
        for index in range(len(senders)):
            file.write(','.join([str(senders[index]), str(5 * round(times[index]/5))])+'\n')

def save_voltage_results(simulation_results, plot, output_folder = ''):

    if (not output_folder): return

    results_dict_complete = nest.GetStatus(simulation_results[plot[0]])[0]

    with open(output_folder+'values/'+plot[0]+'.csv', 'w+') as file:
        file.write(','.join(['sender', 'voltage', 'time'])+'\n')
        for index in range(len(results_dict_complete['events']['senders'])):
            file.write(','.join([str(results_dict_complete['events']['senders'][index]), str(results_dict_complete['events']['V_m'][index]), str(results_dict_complete['events']['times'][index])])+'\n')