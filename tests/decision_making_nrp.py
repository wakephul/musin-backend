import numpy as np
from random import sample
import time
import os
import matplotlib.pyplot as plt
import nest
import nest.raster_plot
import pandas as pd
import pdb

#'''
#'''**********************************************************************************
def LambertWm1(x):
    return nest.ll_api.sli_func('LambertWm1', float(x))

def ComputePSPNorm(tau_mem, C_mem, tau_syn):
    a = (tau_mem / tau_syn)
    b = (1.0 / tau_syn -1.0 / tau_mem)
    t_max = 1.0 / b * (-LambertWm1(-np.exp(-1.0/a)/a) - 1.0 / a)
    return (np.exp(1.0) / (tau_syn * (C_mem * b) * 
            ((np.exp( -t_max / tau_mem) - np.exp(-t_max / tau_syn)) / b - 
            t_max * np.exp(-t_max / tau_syn)))) 

def simulate_network(coherence, par, col):
    nest.ResetKernel()
    dt_rec = par[col]['dt_rec']
    dt = par[col]['dt']
    dt_update= par[col]['dt_update']
    nest.SetKernelStatus({"resolution": dt, "print_time": False, "overwrite_files": True})
    t0 = nest.GetKernelStatus('time')

    startbuild = time.time()
    simtime = par[col]['simtime']
    order = int(par[col]['order'])
    NB = 2 * order  # number of excitatory neurons in pop B
    NA = 2 * order   # number of excitatory neurons in pop A
    NI = 1 * order   # number of inhibitory neurons

    tau_syn = [par[col]['tau_syn_noise'],par[col]['tau_syn_AMPA'], par[col]['tau_syn_NMDA'], par[col]['tau_syn_GABA']]  # [ms]

    exc_neuron_params = {
        "E_L": par[col]['V_membrane'],
        "V_th": par[col]['V_threshold'],
        "V_reset": par[col]['V_reset'],
        "C_m": par[col]['C_m_ex'],
        "tau_m": par[col]['tau_m_ex'],
        "t_ref": par[col]['t_ref_ex'], 
        "tau_syn": tau_syn
    }
    inh_neuron_params = {
        "E_L": par[col]['V_membrane'],
        "V_th": par[col]['V_threshold'],
        "V_reset": par[col]['V_reset'],
        "C_m": par[col]['C_m_in'],
        "tau_m": par[col]['tau_m_in'],
        "t_ref": par[col]['t_ref_in'], 
        "tau_syn": tau_syn
    }

    nest.CopyModel("iaf_psc_exp_multisynapse", "excitatory_pop", params=exc_neuron_params)
    pop_A = nest.Create("excitatory_pop", NA)
    pop_B = nest.Create("excitatory_pop", NB)

    nest.CopyModel("iaf_psc_exp_multisynapse", "inhibitory_pop", params=inh_neuron_params)
    pop_inh = nest.Create("inhibitory_pop", NI)

    #'''
    #'''**********************************************************************************

    J = par[col]['J'] # mV -> this means that it takes 200 simultaneous events to drive the spiking activity 

    J_unit_noise = ComputePSPNorm(par[col]['tau_m_ex'], par[col]['C_m_ex'], par[col]['tau_syn_noise'])
    J_norm_noise = J / J_unit_noise 

    J_unit_AMPA = ComputePSPNorm(par[col]['tau_m_ex'], par[col]['C_m_ex'], par[col]['tau_syn_AMPA'])
    J_norm_AMPA = J / J_unit_AMPA 

    J_norm_NMDA = 0.05  # the weight for the NMDA is set at 0.05, cannot compute J_unit_NMDA since tau_syn_NMDA is greater then tau_m_ex

    J_unit_GABA = ComputePSPNorm(par[col]['tau_m_in'], par[col]['C_m_in'], par[col]['tau_syn_GABA'])
    J_norm_GABA = J / J_unit_GABA
    #'''
    #'''**********************************************************************************

    # Input noise
    nu_th_noise_ex = (np.abs(par[col]['V_threshold']) * par[col]['C_m_ex']) / (J_norm_noise * np.exp(1) * par[col]['tau_m_ex'] * par[col]['tau_syn_noise'])
    nu_ex = par[col]['eta_ex'] * nu_th_noise_ex
    p_rate_ex = 1000.0 * nu_ex

    nu_th_noise_in = (np.abs(par[col]['V_threshold']) * par[col]['C_m_in']) / (J_norm_noise * np.exp(1) * par[col]['tau_m_in'] * par[col]['tau_syn_noise'])
    nu_in = par[col]['eta_in'] * nu_th_noise_in
    p_rate_in = 1000.0 * nu_in

    #nest.SetDefaults("poisson_generator", {"rate": p_rate_ex})    #poisson generator for the noise in input to popA and popB
    PG_noise_to_B = nest.Create("poisson_generator")
    PG_noise_to_A = nest.Create("poisson_generator")

    #nest.SetDefaults("poisson_generator", {"rate": p_rate_in})   #poisson generator for the noise in input to popinh
    PG_noise_to_inh = nest.Create("poisson_generator")

    nest.CopyModel("static_synapse", "noise_syn",
                {"weight": J_norm_noise, "delay": par[col]['delay_noise']})
    noise_syn = {"model": "noise_syn",
                    "receptor_type": 1}

    
    nest.Connect(PG_noise_to_A, pop_A, syn_spec=noise_syn)
    nest.Connect(PG_noise_to_B, pop_B, syn_spec=noise_syn)
    nest.Connect(PG_noise_to_inh, pop_inh, syn_spec=noise_syn)

    #'''
    #'''**********************************************************************************
    
    # Input stimulus
    PG_input_AMPA_B = nest.Create("poisson_generator")
    PG_input_AMPA_A = nest.Create("poisson_generator")

    nest.CopyModel("static_synapse", "excitatory_AMPA_input",
                {"weight": J_norm_AMPA, "delay": par[col]['delay_AMPA']})
    AMPA_input_syn = {"model": "excitatory_AMPA_input",
                    "receptor_type": 2} 
  
    nest.Connect(PG_input_AMPA_A, pop_A, syn_spec=AMPA_input_syn)
    nest.Connect(PG_input_AMPA_B, pop_B, syn_spec=AMPA_input_syn)

    # Define the stimulus: two PoissonInput with time-dependent mean.
    mean_p_rate_stimulus =  p_rate_ex / par[col]['ratio_stim_rate']   #rate for the input Poisson generator to popA (scaled with respect to the noise)
    std_p_rate_stimulus = mean_p_rate_stimulus / par[col]['std_ratio']

    def update_poisson_stimulus(t):

        rate_noise_B = np.random.normal(p_rate_ex, p_rate_ex/par[col]['std_noise'])
        rate_noise_A = np.random.normal(p_rate_ex, p_rate_ex/par[col]['std_noise'])
        rate_noise_inh = np.random.normal(p_rate_in, p_rate_in/par[col]['std_noise'])
        nest.SetStatus(PG_noise_to_A, "rate", rate_noise_A)
        nest.SetStatus(PG_noise_to_B, "rate", rate_noise_B)
        nest.SetStatus(PG_noise_to_inh, "rate", rate_noise_inh)

        if t >= par[col]['start_stim']  and t < par[col]['end_stim']:
            offset_A = mean_p_rate_stimulus * (0.5 - (0.5 * coherence))
            offset_B = mean_p_rate_stimulus * (0.5 + (0.5 * coherence))

            rate_B = np.random.normal(offset_B, std_p_rate_stimulus)
            rate_B = (max(0., rate_B)) #no negative rate
            rate_A = np.random.normal(offset_A, std_p_rate_stimulus)
            rate_A = (max(0., rate_A)) #no negative rate 

        elif t >= par[col]['end_stim']  and t < par[col]['end_stim_rev']:
            offset_A = mean_p_rate_stimulus * (0.5 - (0.5 * par[col]['coh_rev']))
            offset_B = mean_p_rate_stimulus * (0.5 + (0.5 * par[col]['coh_rev']))

            rate_B = np.random.normal(offset_B, std_p_rate_stimulus)
            rate_B = (max(0., rate_B)) #no negative rate
            rate_A = np.random.normal(offset_A, std_p_rate_stimulus)
            rate_A = (max(0., rate_A)) #no negative rate      

        else:
            rate_A = 0.0
            rate_B = 0.0

        nest.SetStatus(PG_input_AMPA_A, "rate", rate_A)
        nest.SetStatus(PG_input_AMPA_B, "rate", rate_B)

        return rate_A, rate_B, rate_noise_A, rate_noise_B

    #'''
    #'''**********************************************************************************

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
        nest.SetDefaults('static_synapse', {'weight': 1., 'delay': dt})
        nest.Connect(idx_monitored_neurons, rate_monitor)

        spike_monitor = nest.Create("spike_detector", params={"withgid": True, "withtime": True, "to_file": False})
        nest.Connect(idx_monitored_neurons, spike_monitor)

        return rate_monitor, spike_monitor, idx_monitored_neurons

    # data collection of a subset of neurons:
    rec_pop=par[col]['rec_pop']
    rate_monitor_A, spike_monitor_A,  idx_monitored_neurons_A = get_monitors(pop_A, int(rec_pop*len(pop_A)))
    rate_monitor_B, spike_monitor_B,  idx_monitored_neurons_B = get_monitors(pop_B, int(rec_pop*len(pop_B)))
    rate_monitor_inh, spike_monitor_inh,  idx_monitored_neurons_inh = get_monitors(pop_inh, int(rec_pop*len(pop_inh)))

    #'''
    #'''**********************************************************************************

    # Populations

    nest.CopyModel("static_synapse", "excitatory_AMPA_AB_BA",
                {"weight": J_norm_AMPA*par[col]['w_minus'], "delay": par[col]['delay_AMPA']})
    AMPA_AB_BA_syn = {"model": "excitatory_AMPA_AB_BA",
                    "receptor_type": 2}
    nest.CopyModel("static_synapse", "excitatory_NMDA_AB_BA",
                {"weight": J_norm_NMDA*par[col]['w_minus'], "delay": par[col]['delay_NMDA']})
    NMDA_AB_BA_syn = {"model": "excitatory_NMDA_AB_BA",
                    "receptor_type": 3}               

    nest.CopyModel("static_synapse", "excitatory_AMPA_AI_BI",
                {"weight": J_norm_AMPA*par[col]['w_plus'], "delay": par[col]['delay_AMPA']})
    AMPA_AI_BI_syn = {"model": "excitatory_AMPA_AI_BI",
                    "receptor_type": 2}                  
    nest.CopyModel("static_synapse", "excitatory_NMDA_AI_BI",
                {"weight": J_norm_NMDA*par[col]['w_plus'], "delay": par[col]['delay_NMDA']})
    NMDA_AI_BI_syn = {"model": "excitatory_NMDA_AI_BI",
                    "receptor_type": 3}  

    nest.CopyModel("static_synapse", "inhibitory_IA_IB",
                {"weight": -J_norm_GABA*par[col]['w_plus'], "delay": par[col]['delay_GABA']})
    GABA_IA_IB_syn = {"model": "inhibitory_IA_IB",
                    "receptor_type": 4} 

    nest.CopyModel("static_synapse", "excitatory_AMPA_recurrent",
                {"weight": J_norm_AMPA, "delay": par[col]['delay_AMPA']})
    AMPA_recurrent_syn = {"model": "excitatory_AMPA_recurrent",
                    "receptor_type": 2}    
    nest.CopyModel("static_synapse", "excitatory_NMDA_recurrent",
                {"weight": J_norm_NMDA*par[col]['w_plus_NMDA'], "delay": par[col]['delay_NMDA']})
    NMDA_recurrent_syn = {"model": "excitatory_NMDA_recurrent",
                    "receptor_type": 3} 
    nest.CopyModel("static_synapse", "inhibitory_recurrent",
                {"weight": -J_norm_GABA, "delay": par[col]['delay_GABA']})
    GABA_recurrent_syn = {"model": "inhibitory_recurrent",
                    "receptor_type": 4} 

    #Connecting populations
    conn_params_ex_AB_BA = {'rule': 'pairwise_bernoulli', 'p':par[col]['epsilon_ex_AB_BA']}
    conn_params_ex_reccurent = {'rule': 'pairwise_bernoulli', 'p':par[col]['epsilon_ex_reccurent']}
    conn_params_ex_AI_BI = {'rule': 'pairwise_bernoulli', 'p':par[col]['epsilon_ex_AI_BI']}
    conn_params_in_IA_IB = {'rule': 'pairwise_bernoulli', 'p':par[col]['epsilon_in_IA_IB']}
    conn_params_in_recurrent = {'rule': 'pairwise_bernoulli', 'p':par[col]['epsilon_in_recurrent']}

    # pop A
    # Recurrent
    nest.Connect(pop_A, pop_A, conn_params_ex_reccurent, AMPA_recurrent_syn)
    nest.Connect(pop_A, pop_A, conn_params_ex_reccurent, NMDA_recurrent_syn)
    # To pop B
    nest.Connect(pop_A, pop_B, conn_params_ex_AB_BA, AMPA_AB_BA_syn)
    nest.Connect(pop_A, pop_B, conn_params_ex_AB_BA, NMDA_AB_BA_syn)
    # To pop inh.
    nest.Connect(pop_A, pop_inh, conn_params_ex_AI_BI, AMPA_AI_BI_syn)
    nest.Connect(pop_A, pop_inh, conn_params_ex_AI_BI, NMDA_AI_BI_syn)

    # pop B
    # Recurrent
    nest.Connect(pop_B, pop_B, conn_params_ex_reccurent, AMPA_recurrent_syn)
    nest.Connect(pop_B, pop_B, conn_params_ex_reccurent, NMDA_recurrent_syn)
    # To pop B
    nest.Connect(pop_B, pop_A, conn_params_ex_AB_BA, AMPA_AB_BA_syn)
    nest.Connect(pop_B, pop_A, conn_params_ex_AB_BA, NMDA_AB_BA_syn)
    # To pop inh.
    nest.Connect(pop_B, pop_inh, conn_params_ex_AI_BI, AMPA_AI_BI_syn)
    nest.Connect(pop_B, pop_inh, conn_params_ex_AI_BI, NMDA_AI_BI_syn)

    # pop inhib
    # Recurrent
    nest.Connect(pop_inh, pop_inh, conn_params_in_recurrent, GABA_recurrent_syn)
    # To pop A
    nest.Connect(pop_inh, pop_A, conn_params_in_IA_IB, GABA_IA_IB_syn)
    # To pop B
    nest.Connect(pop_inh, pop_B, conn_params_in_IA_IB, GABA_IA_IB_syn)

    #'''
    #'''**********************************************************************************

    endbuild = time.time()
    
    sim_steps = np.arange(0,simtime, dt_update)

    stimulus_A = np.zeros((int(simtime)))
    stimulus_B = np.zeros((int(simtime)))

    noise_A = np.zeros((int(simtime)))
    noise_B = np.zeros((int(simtime)))


    for i, step in enumerate(sim_steps):
        rate_A, rate_B, rate_noise_A, rate_noise_B = update_poisson_stimulus(step)

        stimulus_A[int(step):int(step+dt_update)] = rate_A
        stimulus_B[int(step):int(step+dt_update)] = rate_B

        noise_A[int(step):int(step+dt_update)] = rate_noise_A
        noise_B[int(step):int(step+dt_update)] = rate_noise_B

        nest.Simulate(dt_update)

    endsimulate = time.time()

    ret_vals = dict()

    ret_vals["rate_monitor_A"] = rate_monitor_A
    ret_vals["spike_monitor_A"] = spike_monitor_A
    ret_vals["idx_monitored_neurons_A"] = idx_monitored_neurons_A

    ret_vals["rate_monitor_B"] = rate_monitor_B
    ret_vals["spike_monitor_B"] = spike_monitor_B
    ret_vals["idx_monitored_neurons_B"] = idx_monitored_neurons_B

    ret_vals["rate_monitor_inh"] = rate_monitor_inh
    ret_vals["spike_monitor_inh"] = spike_monitor_inh
    ret_vals["idx_monitored_neurons_inh"] = idx_monitored_neurons_inh

    smA = nest.GetStatus(ret_vals["spike_monitor_A"])[0]
    rmA = nest.GetStatus(ret_vals["rate_monitor_A"])[0]	
    smB = nest.GetStatus(ret_vals["spike_monitor_B"])[0]
    rmB = nest.GetStatus(ret_vals["rate_monitor_B"])[0]          	
    smIn = nest.GetStatus(ret_vals["spike_monitor_inh"])[0]
    rmIn = nest.GetStatus(ret_vals["rate_monitor_inh"])[0] 

    evsA = smA["events"]["senders"]
    tsA = smA["events"]["times"]
    t = np.arange(0., simtime, dt_rec)
    A_N_A = np.ones((t.size, 1)) * np.nan
    trmA = rmA["events"]["times"]
    trmA = trmA * dt - t0
    bins = np.concatenate((t, np.array([t[-1] + dt_rec])))
    A_N_A = np.histogram(trmA, bins=bins)[0] / order*2 / dt_rec
    A_N_A = A_N_A*1000

    evsB = smB["events"]["senders"]
    tsB = smB["events"]["times"]
    B_N_B = np.ones((t.size, 1)) * np.nan
    trmB = rmB["events"]["times"]
    trmB = trmB * dt - t0
    bins = np.concatenate((t, np.array([t[-1] + dt_rec])))
    B_N_B = np.histogram(trmB, bins=bins)[0] / order*2 / dt_rec
    B_N_B = B_N_B*1000

    evsIn = smIn["events"]["senders"]
    tsIn = smIn["events"]["times"]
    I_N_I = np.ones((t.size, 1)) * np.nan
    trmIn = rmIn["events"]["times"]
    trmIn = trmIn * dt - t0
    bins = np.concatenate((t, np.array([t[-1] + dt_rec])))
    I_N_I = np.histogram(trmIn, bins=bins)[0] / order*1*rec_pop / dt_rec
    I_N_I = I_N_I*1000

    raster_A = pd.DataFrame({'ID neuron pop_A':evsA, 'event time pop_A':tsA})
    raster_B = pd.DataFrame({ 'ID neuron pop_B':evsB, 'event time pop_B':tsB})
    raster_In = pd.DataFrame({ 'ID neuron pop_inh':evsIn, 'event time pop_inh':tsIn})
    activity = pd.DataFrame({'time':t,'activity (Hz) pop_A': A_N_A, 'activity (Hz) pop_B': B_N_B, 'activity (Hz) pop_inh': I_N_I})
    inputs =  pd.DataFrame({'stimulus pop A': stimulus_A,'stimulus pop B': stimulus_B, 'noise pop A': noise_A,'noise pop B': noise_B})

    
    build_time = endbuild - startbuild
    sim_time = endsimulate - endbuild

    return ret_vals, raster_A, raster_B, raster_In, activity, inputs

def main():

    current_path = os.getcwd()+'/tests/'
    sim_parameters = pd.read_csv(current_path+'decision_making_parameters.csv', index_col=0)
    sim_col='standard'
    coherence = 0.512
    pdb.set_trace()
    ret_vals, raster_A, raster_B, raster_In, activity, inputs = simulate_network(coherence,sim_parameters,sim_col)     
    plt.plot(activity['time'].to_numpy(), activity['activity (Hz) pop_A'].to_numpy(), color='red', label ='pop A')
    plt.plot(activity['time'].to_numpy(), activity['activity (Hz) pop_B'].to_numpy(), color='blue', label ='pop B')
    plt.plot(inputs['stimulus pop A'].to_numpy()/20, color='orange')
    plt.plot(inputs['stimulus pop B'].to_numpy()/20, color='lightblue')
    plt.legend()
    plt.show()
    

if __name__ == "__main__":
	main()

    