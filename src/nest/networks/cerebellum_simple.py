import nest
from random import sample, getrandbits, randint

def get_monitors(pop, monitored_subset_size):
        
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

    voltage_monitor = nest.Create("multimeter")
    # nest.SetStatus(voltage_monitor, {"withtime": True, "record_from":["V_m"], "to_file": True})
    # nest.Connect(voltage_monitor, idx_monitored_neurons)

    return rate_monitor, voltage_monitor, spike_monitor, idx_monitored_neurons

def simulate_network(par):
    # CEREBELLUM
    LTP1 = par["LTP1"]
    LTD1 = par["LTD1"]
    Init_PFPC = par["Init_PFPC"]

    LTP2 = par["LTP2"]
    LTD2 = par["LTD2"]
    Init_MFDCN = par["Init_MFDCN"]

    LTP3 = par["LTP3"]
    LTD3 = par["LTD3"]
    Init_PCDCN = par["Init_PCDCN"]

    PLAST1 = par["PLAST1"]
    PLAST2 = par["PLAST2"]
    PLAST3 = par["PLAST3"]

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
    MF_num = par["MF_num"]
    GR_num = MF_num*20
    PC_num = par["PC_num"]
    IO_num = PC_num
    DCN_num = PC_num//2
    # DCN_num = PC_num


    # MF = nest.Create("parrot_neuron", MF_num)
    GR = nest.Create("granular_neuron", GR_num)
    PC = nest.Create("purkinje_neuron", PC_num)
    IO = nest.Create("parrot_neuron", IO_num)
    DCN = nest.Create("nuclear_neuron", DCN_num)
    vt = nest.Create("volume_transmitter_alberto",PC_num)
    for n, vti in enumerate(vt):
        nest.SetStatus([vti], {"vt_num": n})
            
    # print('MF: ' + str(min(MF)) + " " + str(max(MF)))
    print('GR: ' + str(min(GR)) + " " + str(max(GR)))
    print('PC: ' + str(min(PC)) + " " + str(max(PC)))
    print('IO: ' + str(min(IO)) + " " + str(max(IO)))
    print('DCN: ' + str(min(DCN)) + " " + str(max(DCN)))
    print('vt: ' + str(min(vt)) + " " + str(max(vt)))

    rate_monitor_GR, voltage_monitor_GR, spike_monitor_GR,  idx_monitored_neurons_GR = get_monitors(GR, int(len(GR)))
    rate_monitor_PC, voltage_monitor_PC, spike_monitor_PC,  idx_monitored_neurons_PC = get_monitors(PC, int(len(PC)))
    rate_monitor_IO, voltage_monitor_IO, spike_monitor_IO,  idx_monitored_neurons_IO = get_monitors(IO, int(len(IO)))
    rate_monitor_DCN, voltage_monitor_DCN, spike_monitor_DCN,  idx_monitored_neurons_DCN = get_monitors(DCN, int(len(DCN)))

    # Connectivity

    # MF-GR excitatory connections
    MFGR_conn_param = {"model": "static_synapse",
                        "weight": {'distribution' : 'uniform', 'low': 0.55, 'high': 0.7},
                        "delay": 1.0}

    #questa regola andrà sovrascritta per descrivere gli stimoli che entrano nelle GR
    #pesco A o B a caso
    #a seconda di quello che ho pescato, prendo due GID visivi e due GID uditivi di quel lato (a o b)
    #creo matrice pre e post (pre con gli id dei neuroni in input e post con gli id delle gr)
    imported_stimulus_A = par['imported_stimulus_A']
    imported_stimulus_B = par['imported_stimulus_B']

    input_dendrites_gr = 4
    num_stimuli = len(imported_stimulus_A['type_1'])
    num_stimuli_tot = num_stimuli*input_dendrites_gr
    
    array_pre = []
    array_post = [ item for item in GR for _ in range(input_dendrites_gr) ] 

    max_stim = num_stimuli-1
    for n in range(num_stimuli_tot):
        random_side = bool(getrandbits(1))
        stimulus = imported_stimulus_A if random_side else imported_stimulus_B
        a_1_1 = stimulus['type_1'][randint(0, max_stim)]
        a_1_2 = stimulus['type_1'][randint(0, max_stim)]
        a_2_1 = stimulus['type_2'][randint(0, max_stim)]
        a_2_2 = stimulus['type_2'][randint(0, max_stim)]
        array_pre.extend([a_1_1, a_1_2, a_2_1, a_2_2])

    nest.Connect(array_pre, array_post, {'rule': 'fixed_indegree', 'indegree': 4, "multapses": False}, MFGR_conn_param)
    #valutare frequenza GR (accettabile tra 2 e 10 Hz)

    if PLAST1:
        # PF-PC excitatory plastic connections
        # each PC receives the random 80% of the GR
        nest.SetDefaults('stdp_synapse_sinexp',
                        {"A_minus":   LTD1,
                        "A_plus":    LTP1,
                        "Wmin":      0.0,
                        "Wmax":      4.0,
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
    else:
        PFPC_conn_param = {"model":  'static_synapse',
                            "weight": Init_PFPC,
                            "delay":  1.0}

        for i, PCi in enumerate(PC):
            nest.Connect(GR, [PCi], {'rule': 'fixed_indegree',
                                    'indegree': int(0.8*GR_num),
                                    "multapses": False},
                                    PFPC_conn_param)
            
    # MF-DCN excitatory connections
    if PLAST2:
        vt2 = nest.Create("volume_transmitter_alberto", DCN_num)
        for n, vti in enumerate(vt2):
            nest.SetStatus([vti], {"vt_num": n})
    if PLAST2:
        # MF-DCN excitatory plastic connections
        # every MF is connected with every DCN
        nest.SetDefaults('stdp_synapse_cosexp',
                                {"A_minus":   LTD2,
                                "A_plus":    LTP2,
                                "Wmin":      0.0,
                                "Wmax":      0.25,
                                "vt":        vt2[0]})
        MFDCN_conn_param = {"model": 'stdp_synapse_cosexp',
                            "weight": Init_MFDCN,
                            "delay": 10.0}
    
    # RICORDA! qui è stato cambiato perché non abbiamo più le MF, ma l'array_pre direttamente sulle GR

    #     for i, DCNi in enumerate(DCN):
    #         nest.Connect(MF, [DCNi], 'all_to_all', MFDCN_conn_param)
    #         A = nest.GetConnections(MF, [DCNi])
    #         # nest.SetStatus(A, {'vt_num': float(i)})
    #         nest.SetStatus(A, {'vt_num': i})
    # else:
    #     MFDCN_conn_param = {"model":  "static_synapse",
    #                         "weight": Init_MFDCN,
    #                         "delay":  10.0}
    #     nest.Connect(MF, DCN, 'all_to_all', MFDCN_conn_param) 
    # 
        for i, DCNi in enumerate(DCN):
            nest.Connect(array_pre, [DCNi], {'rule': 'fixed_indegree', 'indegree': 4, "multapses": False}, MFDCN_conn_param)
            A = nest.GetConnections(array_pre, [DCNi])
            nest.SetStatus(A, {'vt_num': i})
    else:
        MFDCN_conn_param = {"model":  "static_synapse",
                            "weight": Init_MFDCN,
                            "delay":  10.0}
        # nest.Connect(MF, DCN, 'all_to_all', MFDCN_conn_param)
        nest.Connect(array_pre, DCN, {'rule': 'fixed_indegree', 'indegree': 4, "multapses": False}, MFDCN_conn_param)                       

    # PC-DCN inhibitory plastic connections
    # each DCN receives 2 connections from 2 contiguous PC
    if PLAST3:
        nest.SetDefaults('stdp_synapse', {"tau_plus": 30.0,
                                                "lambda": LTP3,
                                                "alpha": LTD3/LTP3,
                                                "mu_plus": 0.0,   # Additive STDP
                                                "mu_minus": 0.0,  # Additive STDP
                                                "Wmax": -1.0,
                                                "weight": Init_PCDCN,
                                                "delay": 1.0})
        PCDCN_conn_param = {"model": "stdp_synapse"} 
    else:
        PCDCN_conn_param = {"model": "static_synapse",
                            "weight": Init_PCDCN,
                            "delay": 1.0}
    count_DCN = 0
    for P in range(PC_num):
        nest.Connect([PC[P]], [DCN[count_DCN]],
                            'one_to_one', PCDCN_conn_param)
        if PLAST2:
            nest.Connect([PC[P]], [vt2[count_DCN]], 'one_to_one',
                                {"model":  "static_synapse",
                                "weight": 1.0,
                                "delay":  1.0})
        if P % 2 == 1:
            count_DCN += 1
            
            
    # Input_generation = nest.Create("spike_generator", MF_num)
    # nest.Connect(Input_generation,MF,'one_to_one')
    # MFinput_file = open("/home/mizzou/.opt/nrpStorage/USER_DATA/MF_100Trial_VOR.dat",'r')
    # for MFi in Input_generation:
    #     Spikes_s = MFinput_file.readline()
    #     Spikes_s = Spikes_s.split()
    #     Spikes_f = []
    #     for elements in Spikes_s:
    #         Spikes_f.append(float(elements))
    #     nest.SetStatus([MFi],{'spike_times' : Spikes_f})


    # conn1 = nest.GetConnections(source=GR, target=PC)
    # conn2 = nest.GetConnections(source=array_pre, target=DCN)
    # conn3 = nest.GetConnections(source=PC, target=DCN)

    nest.Simulate(par['sim_time'])

    ret_vals = dict()

    # ret_vals["rate_monitor_GR"] = rate_monitor_GR
    # ret_vals["voltage_monitor_GR"] = voltage_monitor_GR
    ret_vals["spike_monitor_GR"] = spike_monitor_GR
    ret_vals["idx_monitored_neurons_GR"] = idx_monitored_neurons_GR

    # ret_vals["rate_monitor_PC"] = rate_monitor_PC
    # ret_vals["voltage_monitor_PC"] = voltage_monitor_PC
    ret_vals["spike_monitor_PC"] = spike_monitor_PC
    ret_vals["idx_monitored_neurons_PC"] = idx_monitored_neurons_PC
    
    # ret_vals["rate_monitor_IO"] = rate_monitor_IO
    # ret_vals["voltage_monitor_IO"] = voltage_monitor_IO
    ret_vals["spike_monitor_IO"] = spike_monitor_IO
    ret_vals["idx_monitored_neurons_IO"] = idx_monitored_neurons_IO

    # ret_vals["rate_monitor_DCN"] = rate_monitor_DCN
    # ret_vals["voltage_monitor_DCN"] = voltage_monitor_DCN
    ret_vals["spike_monitor_DCN"] = spike_monitor_DCN
    ret_vals["idx_monitored_neurons_DCN"] = idx_monitored_neurons_DCN

    return ret_vals

def run(simulation_parameters):
    try:
        nest.Install("cerebmodule")
        print("cerebmodule installed correctly")
    except Exception as e:  # DynamicModuleManagementError
        print(e)
        print("cerebmodule already installed")

    return_values = simulate_network(simulation_parameters)
    return return_values