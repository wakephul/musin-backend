import pdb
import nest
nest.set_verbosity('M_ERROR')

from random import sample, getrandbits, randint

from api.src.nest.networks.base_network import BaseNetwork

import os
from api.utils import cdf
from api.src.nest.output.rates import calculate_bins
from api.src.managers import file_handling
from api.src.nest.plots.generate import moving_average_plot
from api.src.managers.images.edit import merge_plots

class Cerebellum(BaseNetwork):
    def __init__(self, **execution_params):
        self.name = "cerebellum"
        self.execution_params = execution_params
        self.simulation_results = {}
        self.input_a_1 = []
        self.input_b_1 = []
        self.input_a_2 = []
        self.input_b_2 = []

    def get_monitors(self, pop, monitored_subset_size):
        """Internal helper.
        Args:
            pop: target population of which we record
            monitored_subset_size: max nr of neurons for which a state monitor is registered.
        Returns: monitors for rate, voltage, spikes and monitored neurons indexes.
        """
        monitored_subset_size = min(monitored_subset_size, len(pop))
        
        idx_monitored_neurons = tuple(sample(list(pop), monitored_subset_size))

        rate_monitor = nest.Create("spike_detector")
        nest.SetStatus(rate_monitor, {'withgid': False, 'withtime': True, 'time_in_steps': True})
        nest.SetDefaults('static_synapse', {'weight': 1., 'delay': 0.1})
        nest.Connect(idx_monitored_neurons, rate_monitor)

        spike_monitor = nest.Create("spike_detector", params={"withgid": True, "withtime": True, "to_file": True})
        nest.Connect(idx_monitored_neurons, spike_monitor)

        return spike_monitor, idx_monitored_neurons

    def train_test(self):
        #inputs = [uditivo_a, visivo_a, uditivo_b, visivo_b]

        all_trains = []
        trial_index = 0
        for start_time in range(0, int(self.train_time), int(self.stimulus_duration*3)):
            end_time = start_time+self.stimulus_duration
            random_value = getrandbits(1)
            current_trial = self.trials_side[trial_index]
            if not current_trial: # if trials --> population A
                random_value += 2

            all_trains.append(random_value)

            for input_index in range(len(self.inputs)):
                if input_index != random_value: #azzero i valori in quell'intervallo
                    for neuron in self.inputs[input_index]:
                        neu = nest.GetStatus([neuron])[0]
                        spike_times = neu['spike_times'].tolist()
                        st = [time for time in spike_times if (time < start_time or time > end_time)]
                        st.sort()
                        nest.SetStatus([neuron], {'spike_times': st})
            trial_index += 1
        
        all_tests = []
        #inputs = [type_1_a, type_2_a, type_1_b, type_2_b]
        inputs_to_keep = []
        for test_type_index, test_type in enumerate(self.test_types):
            trial_index = 0
            if test_type == 3:
                inputs_to_keep = [0, 1, 2, 3]
            elif test_type == 1:
                inputs_to_keep = [0, 2]
            elif test_type == 2:
                inputs_to_keep = [1, 3]
            for start_time in range(int(self.train_time+(self.test_time*(test_type_index))), int(self.train_time+(self.test_time*(test_type_index+1))), int(self.stimulus_duration*3)):
                all_tests.append(test_type)
                end_time = start_time+self.stimulus_duration
                current_trial = self.trials_side[trial_index]

                for input_index in range(len(self.inputs)):
                    if input_index not in inputs_to_keep:
                        for neuron in self.inputs[input_index]:
                            neu = nest.GetStatus([neuron])[0]
                            spike_times = neu['spike_times'].tolist()
                            st = [time for time in spike_times if (time < start_time or time > end_time)]
                            st.sort()
                            nest.SetStatus([neuron], {'spike_times': st})
                
                trial_index += 1

        return {"train": all_trains, "test": all_tests}

    def simulate_network(self):
        print('simulating cerebellum')

        # CEREBELLUM
        LTP1 = self.execution_params["LTP1"]
        LTD1 = self.execution_params["LTD1"]
        Init_PFPC = self.execution_params["Init_PFPC"]

        LTP2 = self.execution_params["LTP2"]
        LTD2 = self.execution_params["LTD2"]
        Init_MFDCN = self.execution_params["Init_MFDCN"]
        Init_MFDCN_low = self.execution_params["Init_MFDCN_low"]
        Init_MFDCN_high = self.execution_params["Init_MFDCN_high"]

        LTP3 = self.execution_params["LTP3"]
        LTD3 = self.execution_params["LTD3"]
        Init_PCDCN = self.execution_params["Init_PCDCN"]

        PLAST1 = self.execution_params["PLAST1"]
        PLAST2 = self.execution_params["PLAST2"]
        PLAST3 = self.execution_params["PLAST3"]

        # nest.SetKernelStatus({'resolution' : 1.0})

        """
        Initializes NEST with the neuronal network that has to be simulated
        """
        nest.CopyModel('iaf_cond_exp', 'granular_neuron')
        nest.CopyModel('iaf_cond_exp', 'purkinje_neuron')
        nest.CopyModel('iaf_cond_exp', 'olivary_neuron')
        nest.CopyModel('iaf_cond_exp', 'nuclear_neuron')

        nest.SetDefaults('granular_neuron', {'t_ref': 1.0,
                                                'C_m': 2.0,
                                                'V_th': -40.0,
                                                'V_reset': -70.0,
                                                'g_L': 0.2,
                                                'tau_syn_ex': 0.5,
                                                'tau_syn_in': 10.0})

        nest.SetDefaults('purkinje_neuron', {'t_ref': 2.0,
                                                'C_m': 400.0,
                                                'V_th': -52.0,
                                                'V_reset': -70.0,
                                                'g_L': 16.0,
                                                'tau_syn_ex': 0.5,
                                                'tau_syn_in': 1.6})
                                            #'I_e': 300.0})

        nest.SetDefaults('nuclear_neuron', {'t_ref': 1.0,
                                            'C_m': 2.0,
                                            'V_th': -40.0,
                                            'V_reset': -70.0,
                                            'g_L': 0.2,
                                            'tau_syn_ex': 0.5,
                                            'tau_syn_in': 10.0})

        # Cell numbers
        GR_num = int(self.execution_params['GR_num'])
        PC_num = int(self.execution_params["PC_num"])
        IO_num = int(PC_num)
        DCN_num = int(PC_num//2)
        # DCN_num = PC_num

        self.train_time = self.execution_params['train_time']
        self.test_time = self.execution_params['test_time']
        self.test_types = self.execution_params['test_types']
        self.stimulus_duration = self.execution_params['t_stimulus_duration']

        imported_stimulus_A = []
        imported_stimulus_B = []

        for input_code in self.execution_params['imported_stimuli']:
            imported_stimulus_A.append(self.execution_params['imported_stimuli'][input_code][0])
            imported_stimulus_B.append(self.execution_params['imported_stimuli'][input_code][1])

        print("imported_stimulus_A: ", imported_stimulus_A)
        print("imported_stimulus_B: ", imported_stimulus_B)

        # MF = nest.Create("parrot_neuron", MF_num)
        print("Creating neurons")
        GR = nest.Create("granular_neuron", GR_num)
        PC = nest.Create("purkinje_neuron", PC_num)
        IO = nest.Create("parrot_neuron", IO_num)
        DCN = nest.Create("nuclear_neuron", DCN_num)
        vt = nest.Create("volume_transmitter_alberto",PC_num)
        for n, vti in enumerate(vt):
            nest.SetStatus([vti], {"vt_num": n})
                
        # print('MF: ' + str(min(MF)) + " " + str(max(MF)))
        # print('GR: ' + str(min(GR)) + " " + str(max(GR)))
        # print('PC: ' + str(min(PC)) + " " + str(max(PC)))
        # print('IO: ' + str(min(IO)) + " " + str(max(IO)))
        # print('DCN: ' + str(min(DCN)) + " " + str(max(DCN)))
        # print('vt: ' + str(min(vt)) + " " + str(max(vt)))

        #per PC, IO e DCN crea 2 monitor per le due metà (una + e una -)
        self.spike_monitor_GR, self.idx_monitored_neurons_GR = self.get_monitors(GR, int(len(GR)))
        self.spike_monitor_PC, self.idx_monitored_neurons_PC = self.get_monitors(PC, int(len(PC)))
        self.spike_monitor_IO, self.idx_monitored_neurons_IO = self.get_monitors(IO, int(len(IO)))
        self.spike_monitor_DCN, self.idx_monitored_neurons_DCN = self.get_monitors(DCN, int(len(DCN)))

        self.spike_monitor_DCN_a, self.idx_monitored_neurons_DCN_a = self.get_monitors(DCN[:len(DCN)//2], int(len(DCN))//2)
        self.spike_monitor_DCN_b, self.idx_monitored_neurons_DCN_b = self.get_monitors(DCN[len(DCN)//2:], int(len(DCN))//2)

        # Connectivity

        # MF-GR excitatory connections
        # MFGR_conn_param = {"model": "static_synapse",
        #                     "weight": {'distribution' : 'uniform', 'low': 0.55, 'high': 0.7},
        #                     "delay": 1.0}
        MFGR_conn_param = {"model": "static_synapse",
                            "weight": {'distribution' : 'uniform', 'low': 0.55, 'high': 1.5},
                            "delay": 1.0}

        #nel test mi devo mettere sia il caso audiovisivo che il caso semplice solo audio o solo visivo
        # "weight": {'distribution' : 'uniform', 'low': 0.55, 'high': 0.7}, questo posso usarlo per gestire la distribuzione dei pesi

        input_a_1 = imported_stimulus_A[0]
        input_b_1 = imported_stimulus_B[0]
        input_a_2 = imported_stimulus_A[1]
        input_b_2 = imported_stimulus_B[1]

        self.inputs = [input_a_1, input_a_2, input_b_1, input_b_2]

        self.trials_side = self.execution_params['trials_side']

        train_test_result = self.train_test()

        input_dendrites_gr = 4
        
        array_pre = []
        array_post = [ item for item in GR for _ in range(input_dendrites_gr) ] 

        max_pos = len(imported_stimulus_A)-1
        for n in range(len(GR)):
            random_side = bool(getrandbits(1))
            stimulus = imported_stimulus_A if random_side else imported_stimulus_B
            try:
                #ogni granule riceve due input per tipo (due uditivi e due visivi)
                stim_1_1 = stimulus[0][randint(0, max_pos)]
                stim_1_2 = stimulus[0][randint(0, max_pos)]
                stim_2_1 = stimulus[1][randint(0, max_pos)]
                stim_2_2 = stimulus[1][randint(0, max_pos)]
            except Exception as e:
                print("exception in cerebellum_simple, line 221: ", e)
            array_pre.extend([stim_1_1, stim_1_2, stim_2_1, stim_2_2])

        nest.Connect(array_pre, array_post, "one_to_one", MFGR_conn_param)

        # PF-PC excitatory plastic connections
        # each PC receives the random 80% of the GR
        nest.SetDefaults('stdp_synapse_sinexp',
                        {"A_minus":   LTD1,
                        "A_plus":    LTP1,
                        "Wmin":      0.0,
                        "Wmax":      7.0,
                        "vt":        vt[0]})
        
        PFPC_conn_param = {"model":  'stdp_synapse_sinexp',
                        "weight": Init_PFPC,
                        "delay":  1.0}
        for i, PCi in enumerate(PC):
            nest.Connect(GR, [PCi], {'rule': 'fixed_indegree',
                                    'indegree': int(0.8*GR_num),
                                    "multapses": False},
                        PFPC_conn_param)
            A = nest.GetConnections(GR, [PCi])
            nest.SetStatus(A, {'vt_num': i})
            
        nest.Connect(IO, vt, {'rule': 'one_to_one'},
                            {"model": "static_synapse",
                            "weight": 1.0, "delay": 1.0})
                
        # MF-DCN excitatory connections
        # MFDCN_conn_param = {"model":  "static_synapse",
        #                     "weight": Init_MFDCN,
        #                     "delay":  10.0}
        MFDCN_conn_param = {"model":  "static_synapse",
                            "weight": {'distribution' : 'uniform', 'low': Init_MFDCN_low, 'high': Init_MFDCN_high},
                            "delay":  20.0}

        nest.Connect(input_a_1, DCN, "all_to_all", MFDCN_conn_param)
        nest.Connect(input_b_1, DCN, "all_to_all", MFDCN_conn_param)
        nest.Connect(input_a_2, DCN, "all_to_all", MFDCN_conn_param)
        nest.Connect(input_b_2, DCN, "all_to_all", MFDCN_conn_param)

        IO_a = IO[:len(IO)//2]
        IO_b = IO[len(IO)//2:]
        for i in range(len(self.trials_side)):
            pg = nest.Create('poisson_generator', params = {'rate': 8.5, 'start': float((i*3000.00)+300.00), 'stop': float((i*3000.00)+600.00)})
            if self.trials_side[i]:
                nest.Connect(pg, IO_a)
            else:
                nest.Connect(pg, IO_b)

        # PC-DCN inhibitory plastic connections
        # each DCN receives 2 connections from 2 contiguous PC
        PCDCN_conn_param = {"model": "static_synapse",
                            "weight": Init_PCDCN,
                            "delay": 1.0}

        count_DCN = 0
        for P in range(PC_num):
            nest.Connect([PC[P]], [DCN[count_DCN]],
                                'one_to_one', PCDCN_conn_param)
            if P % 2 == 1:
                count_DCN += 1
                    
        nest.Simulate(self.train_time)
        nest.SetDefaults('stdp_synapse_sinexp', {"A_minus": 0.0, "A_plus":0.0})
        for i in range(len(self.test_types)):
            nest.Simulate(self.test_time)

        self.simulation_results["spike_monitor_GR"] = self.spike_monitor_GR
        self.simulation_results["idx_monitored_neurons_GR"] = self.idx_monitored_neurons_GR

        self.simulation_results["spike_monitor_PC"] = self.spike_monitor_PC
        self.simulation_results["idx_monitored_neurons_PC"] = self.idx_monitored_neurons_PC
        
        self.simulation_results["spike_monitor_IO"] = self.spike_monitor_IO
        self.simulation_results["idx_monitored_neurons_IO"] = self.idx_monitored_neurons_IO

        self.simulation_results["spike_monitor_DCN_a"] = self.spike_monitor_DCN_a
        self.simulation_results["idx_monitored_neurons_DCN_a"] = self.idx_monitored_neurons_DCN_a

        self.simulation_results["spike_monitor_DCN_b"] = self.spike_monitor_DCN_b
        self.simulation_results["idx_monitored_neurons_DCN_b"] = self.idx_monitored_neurons_DCN_b

        self.simulation_results["spike_monitor_DCN"] = self.spike_monitor_DCN
        self.simulation_results["idx_monitored_neurons_DCN"] = self.idx_monitored_neurons_DCN

        self.simulation_results["train"] = train_test_result["train"]
        self.simulation_results["test"] = train_test_result["test"]

        self.simulation_results["DCN"] = DCN

        self.simulation_results["train_time"] = self.train_time
        self.simulation_results["test_time"] = self.test_time
        self.simulation_results["stimulus_duration"] = self.stimulus_duration
        self.simulation_results["trials_side"] = self.trials_side
        self.simulation_results["test_types"] = self.test_types

    def run(self):
        try:
            nest.Install("cerebmodule")
            print("cerebmodule installed correctly")
        except Exception as e:
            print(e)
            print("cerebmodule already installed")

        self.simulation_results = self.simulate_network()
    
    def plot(self):

        test_number = self.test_time/self.stimulus_duration

        senders_spike_monitor_DCN_a = nest.GetStatus(self.spike_monitor_DCN_a, 'events')[0]['senders']
        times_spike_monitor_DCN_a = nest.GetStatus(self.spike_monitor_DCN_a, 'events')[0]['times']
        senders_spike_monitor_DCN_b = nest.GetStatus(self.spike_monitor_DCN_b, 'events')[0]['senders']
        times_spike_monitor_DCN_b = nest.GetStatus(self.spike_monitor_DCN_b, 'events')[0]['times']

        bin_size = 5
        
        times_spike_monitor_DCN_a = [t for t in times_spike_monitor_DCN_a if t > self.train_time]
        times_spike_monitor_DCN_b = [t for t in times_spike_monitor_DCN_b if t > self.train_time]
        bin_rates_DCN_complete_a = calculate_bins(senders_spike_monitor_DCN_a, times_spike_monitor_DCN_a, len(self.idx_monitored_neurons_DCN_a)//2, bin_size, self.train_time, self.train_time+(self.test_time*test_number), test_number)
        bin_rates_DCN_complete_b = calculate_bins(senders_spike_monitor_DCN_b, times_spike_monitor_DCN_b, len(self.idx_monitored_neurons_DCN_a)//2, bin_size, self.train_time, self.train_time+(self.test_time*test_number), test_number)

        cdf_plots = []
        
        for tt_index, tt in enumerate(self.test_types):
            bin_rates_a_portion = bin_rates_DCN_complete_a[tt_index]
            bin_rates_b_portion = bin_rates_DCN_complete_b[tt_index]
            os.makedirs(self.output_folder+'files', exist_ok=True)
            json_title_a = file_handling.dict_to_json(bin_rates_a_portion, self.output_folder+'files/bin_rates_DCN_a_test_'+str(tt_index))
            json_title_b = file_handling.dict_to_json(bin_rates_b_portion, self.output_folder+'files/bin_rates_DCN_b_test_'+str(tt_index))

            moving_average_plot(bin_rates_a_portion, self.output_folder, 'ma_rates_DCN_a_test_'+str(tt_index), (self.train_time+(self.test_time*tt_index), self.train_time+self.test_time+(self.test_time*tt_index)))

            cdf.calculate([json_title_a, json_title_b], self.output_folder, 'cdf_test_'+str(tt_index), 5, 'save')

            # ma_plots.append(['ma_rates_DCN_a', 'ma_rates', 'test'])
            cdf_plots.append(['cdf', 'cdf', 'test'])
        
        # merge_plots(output_folder, cdf_plots, 'cdf_plots', len(test_types))

        # create_folder(output_folder+'multimeters')
        # create_folder(output_folder+'spike_detectors')
        # multimeters_merge(output_folder+'multimeters/')
        # spike_detectors_merge(output_folder+'spike_detectors/')

        # # monitors = ['spike_monitor_DCN_a', 'spike_monitor_DCN_b']
        # # monitored_populations = ['idx_monitored_neurons_DCN_a', 'idx_monitored_neurons_DCN_b']

        # # rates = calculate_average_rate(simulation_results=simulation_results, max_time=test_time*test_number, monitors=monitors, monitored_populations=monitored_populations)

        # # file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nRates: " + ', '.join(map(str, zip(monitors, rates))))
        # file_handling.append_to_file(output_folder+'simulation_notes.txt', f"\nExecution: " + json.dumps(execution))