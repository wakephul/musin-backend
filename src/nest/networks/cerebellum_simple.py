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

    return spike_monitor, idx_monitored_neurons

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


    imported_stimulus_A = par['imported_stimulus_A']
    imported_stimulus_B = par['imported_stimulus_B']
    # Cell numbers
    GR_num = par['GR_num']
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

    #per PC, IO e DCN crea 2 monitor per le due metà (una + e una -)
    spike_monitor_GR,  idx_monitored_neurons_GR = get_monitors(GR, int(len(GR)))
    spike_monitor_PC,  idx_monitored_neurons_PC = get_monitors(PC, int(len(PC)))
    spike_monitor_IO,  idx_monitored_neurons_IO = get_monitors(IO, int(len(IO)))
    spike_monitor_DCN,  idx_monitored_neurons_DCN = get_monitors(DCN, int(len(DCN)))

    # Connectivity

    # MF-GR excitatory connections
    MFGR_conn_param = {"model": "static_synapse",
                        "weight": {'distribution' : 'uniform', 'low': 0.55, 'high': 0.7},
                        "delay": 1.0}

    #questa regola andrà sovrascritta per descrivere gli stimoli che entrano nelle GR
    #pesco A o B a caso
    #a seconda di quello che ho pescato, prendo due GID visivi e due GID uditivi di quel lato (a o b)
    #creo matrice pre e post (pre con gli id dei neuroni in input e post con gli id delle gr)

    #TODO: prima di eseguire il test, dovremmo avere un periodo di training in cui passiamo solo a1/b1 oppure solo a2/b2,
    #quindi una sola tipologia di stimolo per volta

    input_dendrites_gr = 4
    
    array_pre = []
    array_post = [ item for item in GR for _ in range(input_dendrites_gr) ] 

    max_pos = len(imported_stimulus_A)-1
    for n in range(len(GR)):
        random_side = bool(getrandbits(1))
        stimulus = imported_stimulus_A if random_side else imported_stimulus_B
        stim_1_1 = stimulus['type_1'][randint(0, max_pos)]
        stim_1_2 = stimulus['type_1'][randint(0, max_pos)]
        stim_2_1 = stimulus['type_2'][randint(0, max_pos)]
        stim_2_2 = stimulus['type_2'][randint(0, max_pos)]
        array_pre.extend([stim_1_1, stim_1_2, stim_2_1, stim_2_2])

    input_a_1 = imported_stimulus_A['type_1']
    input_b_1 = imported_stimulus_B['type_1']
    input_a_2 = imported_stimulus_A['type_2']
    input_b_2 = imported_stimulus_B['type_2']

    nest.Connect(array_pre, array_post, "one_to_one", MFGR_conn_param)

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
            
    # MF-DCN excitatory connections
    MFDCN_conn_param = {"model":  "static_synapse",
                        "weight": Init_MFDCN,
                        "delay":  10.0}

    nest.Connect(input_a_1, DCN, "all_to_all", MFDCN_conn_param)
    nest.Connect(input_b_1, DCN, "all_to_all", MFDCN_conn_param)
    # nest.Connect(input_a_2, DCN, "all_to_all", MFDCN_conn_param)
    # nest.Connect(input_b_2, DCN, "all_to_all", MFDCN_conn_param)

    # TODO: ci vuole anche l'input alle IO
    # possiamo connettere lo stimolo in input giocando con l'indegree in modo da arrivare ad un output a 1/2Hz (facendo quindi un downscaling)
    # altra possibilità è quella di crearle come parrot neuron (sono già dei parrot) e generare l'input con dei poisson generator creati 
    # a seconda di qual è il lato dello stimolo (che quindi mi devo passare in input)
    # questi stimoli devono essere tra 400 e 600 ms
    trials_1 = par['trials_1']
    trials_2 = par['trials_2']
    IO_a = IO[:len(IO)//2]
    IO_b = IO[len(IO)//2:]
    for i in range(len(trials_1)):
        pg = nest.Create('poisson_generator', params = {'rate': 1.5, 'start': float((i*3000.00)+400.00), 'stop': float((i*3000.00)+600.00)})
        if trials_1[i]:
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
                   

    nest.Simulate(par['sim_time'])

    ret_vals = dict()

    ret_vals["spike_monitor_GR"] = spike_monitor_GR
    ret_vals["idx_monitored_neurons_GR"] = idx_monitored_neurons_GR

    ret_vals["spike_monitor_PC"] = spike_monitor_PC
    ret_vals["idx_monitored_neurons_PC"] = idx_monitored_neurons_PC
    
    ret_vals["spike_monitor_IO"] = spike_monitor_IO
    ret_vals["idx_monitored_neurons_IO"] = idx_monitored_neurons_IO

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