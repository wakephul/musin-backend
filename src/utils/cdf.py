from src.nest.plots.generate import moving_average_plot_no_save
from src.nest.output.rates import calculate_response_times
import json

def calculate(filenames = [], output_folder = '', output_title = 'cdf', threshold = 15, plot_type='save'):
    if len(filenames) > 1:
        with open(filenames[0], 'r') as j:
            bin_rates = json.loads(j.read())
        ma_rates_a, times = moving_average_plot_no_save(bin_rates)

        with open(filenames[1], 'r') as j:
            bin_rates = json.loads(j.read())
        ma_rates_b, times = moving_average_plot_no_save(bin_rates)

        ma_rates = [abs(a-b) for a, b in zip(ma_rates_a, ma_rates_b)]

    else:
        ma_rates, times = moving_average_plot_no_save(bin_rates)

    trial_time = 3000
    bin_size = 5

    response_times = []
    resp = calculate_response_times(ma_rates, threshold, trial_time, bin_size)
    for rt in resp:
        response_times.append(rt%1000)

    print('RESPONSE TIMES: ', response_times)

    # CDF plot for spike times
    import numpy as np
    import matplotlib.pyplot as plt

    def cdf_calc(data):
        count, bins_count = np.histogram(data, bins=10)
        try:
            pdf = count / sum(count)
        except:
            pdf = 0
        cdf = np.cumsum(pdf)
        return bins_count, cdf

    bins_count, cdf = cdf_calc(response_times)
    
    plt.xlim(0, 600)
    plt.ylim(0, 1.1)
    # plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    plt.plot(bins_count[1:], cdf, '--o', label="CDF cerebellum")
    plt.legend()

    if plot_type == 'show':
        plt.show()

    elif plot_type == 'save':
        plt.savefig(output_folder+output_title+'.png')