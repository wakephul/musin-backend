import numpy as np
from random import sample
import time
import os
import matplotlib.pyplot as plt
import nest
nest.set_verbosity('M_ERROR')
import nest.raster_plot
import pandas as pd
import pdb

from api.src.nest.networks.base_network import BaseNetwork
from api.utils import cdf
from api.src.nest.output.rates import calculate_bins
from api.src.managers import file_handling
from api.src.nest.plots.generate import moving_average_plot
from api.src.managers.images.edit import merge_plots

class DecisionMaking(BaseNetwork):
    def __init__(self, **execution_params):
        self.name = "cortex"
        self.execution_params = execution_params
        self.simulation_results = {}
        self.plots_to_create = [
            ["spike_monitor_A", "raster", "test"],
            ["spike_monitor_B", "raster", "test"],
            ["spike_monitor_inh", "raster", "test"]
        ]

    def LambertWm1(self, x):
        return nest.ll_api.sli_func('LambertWm1', float(x))

    def ComputePSPNorm(self, tau_mem, C_mem, tau_syn):
        a = (tau_mem / tau_syn)
        b = (1.0 / tau_syn -1.0 / tau_mem)
        t_max = 1.0 / b * (-self.LambertWm1(-np.exp(-1.0/a)/a) - 1.0 / a)
        return (np.exp(1.0) / (tau_syn * (C_mem * b) * 
                ((np.exp( -t_max / tau_mem) - np.exp(-t_max / tau_syn)) / b - 
                t_max * np.exp(-t_max / tau_syn)))) 
    
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
            nest.SetDefaults('static_synapse', {'weight': 1., 'delay': self.dt})
            nest.Connect(idx_monitored_neurons, rate_monitor)

            spike_monitor = nest.Create("spike_detector", params={"withgid": True, "withtime": True, "to_file": True})
            nest.Connect(idx_monitored_neurons, spike_monitor)

            voltage_monitor = nest.Create("multimeter")
            nest.SetStatus(voltage_monitor, {"withtime": True, "record_from":["V_m"], "to_file": True})
            nest.Connect(voltage_monitor, idx_monitored_neurons)

            return rate_monitor, voltage_monitor, spike_monitor, idx_monitored_neurons

    def simulate_network(self, coherence, par):
        # nest.ResetKernel()
        self.dt = par['dt']
        # nest.SetKernelStatus({"resolution": dt, "print_time": False, "overwrite_files": True})
        # t0 = nest.GetKernelStatus('time')

        # startbuild = time.time()
        order = int(par['order'])
        NB = 2 * order  # number of excitatory neurons in pop B
        NA = 2 * order   # number of excitatory neurons in pop A
        NI = 1 * order   # number of inhibitory neurons

        tau_syn = [par['tau_syn_noise'],par['tau_syn_AMPA'], par['tau_syn_NMDA'], par['tau_syn_GABA']]  # [ms]

        exc_neuron_params = {
            "E_L": par['V_membrane'],
            "V_th": par['V_threshold'],
            "V_reset": par['V_reset'],
            "C_m": par['C_m_ex'],
            "tau_m": par['tau_m_ex'],
            "t_ref": par['t_ref_ex'], 
            "tau_syn": tau_syn
        }
        inh_neuron_params = {
            "E_L": par['V_membrane'],
            "V_th": par['V_threshold'],
            "V_reset": par['V_reset'],
            "C_m": par['C_m_in'],
            "tau_m": par['tau_m_in'],
            "t_ref": par['t_ref_in'], 
            "tau_syn": tau_syn
        }

        nest.CopyModel("iaf_psc_exp_multisynapse", "excitatory_pop", params=exc_neuron_params)
        pop_A = nest.Create("excitatory_pop", NA)
        pop_B = nest.Create("excitatory_pop", NB)

        nest.CopyModel("iaf_psc_exp_multisynapse", "inhibitory_pop", params=inh_neuron_params)
        pop_inh = nest.Create("inhibitory_pop", NI)

        #'''
        #'''**********************************************************************************

        J = par['J'] # mV -> this means that it takes 200 simultaneous events to drive the spiking activity 

        J_unit_noise = self.ComputePSPNorm(par['tau_m_ex'], par['C_m_ex'], par['tau_syn_noise'])
        J_norm_noise = J / J_unit_noise 

        J_unit_AMPA = self.ComputePSPNorm(par['tau_m_ex'], par['C_m_ex'], par['tau_syn_AMPA'])
        J_norm_AMPA = J / J_unit_AMPA 

        J_norm_NMDA = 0.05  # the weight for the NMDA is set at 0.05, cannot compute J_unit_NMDA since tau_syn_NMDA is greater then tau_m_ex

        J_unit_GABA = self.ComputePSPNorm(par['tau_m_in'], par['C_m_in'], par['tau_syn_GABA'])
        J_norm_GABA = J / J_unit_GABA
        #'''
        #'''**********************************************************************************

        # Input noise
        nu_th_noise_ex = (np.abs(par['V_threshold']) * par['C_m_ex']) / (J_norm_noise * np.exp(1) * par['tau_m_ex'] * par['tau_syn_noise'])
        nu_ex = par['eta_ex'] * nu_th_noise_ex
        p_rate_ex = 1000.0 * nu_ex

        nu_th_noise_in = (np.abs(par['V_threshold']) * par['C_m_in']) / (J_norm_noise * np.exp(1) * par['tau_m_in'] * par['tau_syn_noise'])
        nu_in = par['eta_in'] * nu_th_noise_in
        p_rate_in = 1000.0 * nu_in

        #nest.SetDefaults("poisson_generator", {"rate": p_rate_ex})    #poisson generator for the noise in input to popA and popB
        PG_noise_to_B = nest.Create("poisson_generator")
        PG_noise_to_A = nest.Create("poisson_generator")

        #nest.SetDefaults("poisson_generator", {"rate": p_rate_in})   #poisson generator for the noise in input to popinh
        PG_noise_to_inh = nest.Create("poisson_generator")

        nest.CopyModel("static_synapse", "noise_syn",
                    {"weight": J_norm_noise, "delay": par['delay_noise']})
        noise_syn = {"model": "noise_syn",
                        "receptor_type": 1}

        
        nest.Connect(PG_noise_to_A, pop_A, syn_spec=noise_syn)
        nest.Connect(PG_noise_to_B, pop_B, syn_spec=noise_syn)
        nest.Connect(PG_noise_to_inh, pop_inh, syn_spec=noise_syn)

        #'''
        #'''**********************************************************************************
        
        # Input stimulus
        PG_input_AMPA_A = nest.Create("poisson_generator") if (not 'imported_stimulus_A' in par) else par['imported_stimulus_A']
        PG_input_AMPA_B = nest.Create("poisson_generator")if (not 'imported_stimulus_B' in par) else par['imported_stimulus_B']

        # print('INPUT A:', nest.GetStatus(PG_input_AMPA_A, 'spike_times'))
        # print('INPUT B:', nest.GetStatus(PG_input_AMPA_B, 'spike_times'))

        nest.CopyModel("static_synapse", "excitatory_AMPA_input",
                    {"weight": J_norm_AMPA, "delay": par['delay_AMPA']})
        AMPA_input_syn = {"model": "excitatory_AMPA_input",
                        "receptor_type": 2} 
    
        nest.Connect(PG_input_AMPA_A, pop_A, syn_spec=AMPA_input_syn)
        nest.Connect(PG_input_AMPA_B, pop_B, syn_spec=AMPA_input_syn)

        # Define the stimulus: two PoissonInput with time-dependent mean.
        mean_p_rate_stimulus =  p_rate_ex / par['ratio_stim_rate']   #rate for the input Poisson generator to popA (scaled with respect to the noise)
        std_p_rate_stimulus = mean_p_rate_stimulus / par['std_ratio']

        # data collection of a subset of neurons:
        rec_pop=par['rec_pop']
        rate_monitor_A, voltage_monitor_A, spike_monitor_A,  idx_monitored_neurons_A = self.get_monitors(pop_A, int(rec_pop*len(pop_A)))
        rate_monitor_B, voltage_monitor_B, spike_monitor_B,  idx_monitored_neurons_B = self.get_monitors(pop_B, int(rec_pop*len(pop_B)))
        rate_monitor_inh, voltage_monitor_inh, spike_monitor_inh,  idx_monitored_neurons_inh = self.get_monitors(pop_inh, int(rec_pop*len(pop_inh)))

        # Populations

        nest.CopyModel("static_synapse", "excitatory_AMPA_AB_BA",
                    {"weight": J_norm_AMPA*par['w_minus'], "delay": par['delay_AMPA']})
        AMPA_AB_BA_syn = {"model": "excitatory_AMPA_AB_BA",
                        "receptor_type": 2}
        nest.CopyModel("static_synapse", "excitatory_NMDA_AB_BA",
                    {"weight": J_norm_NMDA*par['w_minus'], "delay": par['delay_NMDA']})
        NMDA_AB_BA_syn = {"model": "excitatory_NMDA_AB_BA",
                        "receptor_type": 3}               

        nest.CopyModel("static_synapse", "excitatory_AMPA_AI_BI",
                    {"weight": J_norm_AMPA*par['w_plus'], "delay": par['delay_AMPA']})
        AMPA_AI_BI_syn = {"model": "excitatory_AMPA_AI_BI",
                        "receptor_type": 2}                  
        nest.CopyModel("static_synapse", "excitatory_NMDA_AI_BI",
                    {"weight": J_norm_NMDA*par['w_plus'], "delay": par['delay_NMDA']})
        NMDA_AI_BI_syn = {"model": "excitatory_NMDA_AI_BI",
                        "receptor_type": 3}  

        nest.CopyModel("static_synapse", "inhibitory_IA_IB",
                    {"weight": -J_norm_GABA*par['w_plus'], "delay": par['delay_GABA']})
        GABA_IA_IB_syn = {"model": "inhibitory_IA_IB",
                        "receptor_type": 4} 

        nest.CopyModel("static_synapse", "excitatory_AMPA_recurrent",
                    {"weight": J_norm_AMPA, "delay": par['delay_AMPA']})
        AMPA_recurrent_syn = {"model": "excitatory_AMPA_recurrent",
                        "receptor_type": 2}    
        nest.CopyModel("static_synapse", "excitatory_NMDA_recurrent",
                    {"weight": J_norm_NMDA*par['w_plus_NMDA'], "delay": par['delay_NMDA']})
        NMDA_recurrent_syn = {"model": "excitatory_NMDA_recurrent",
                        "receptor_type": 3} 
        nest.CopyModel("static_synapse", "inhibitory_recurrent",
                    {"weight": -J_norm_GABA, "delay": par['delay_GABA']})
        GABA_recurrent_syn = {"model": "inhibitory_recurrent",
                        "receptor_type": 4} 

        #Connecting populations
        conn_params_ex_AB_BA = {'rule': 'pairwise_bernoulli', 'p':par['epsilon_ex_AB_BA']}
        conn_params_ex_reccurent = {'rule': 'pairwise_bernoulli', 'p':par['epsilon_ex_reccurent']}
        conn_params_ex_AI_BI = {'rule': 'pairwise_bernoulli', 'p':par['epsilon_ex_AI_BI']}
        conn_params_in_IA_IB = {'rule': 'pairwise_bernoulli', 'p':par['epsilon_in_IA_IB']}
        conn_params_in_recurrent = {'rule': 'pairwise_bernoulli', 'p':par['epsilon_in_recurrent']}

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

        rate_noise_B = np.random.normal(p_rate_ex, p_rate_ex/par['std_noise'])
        rate_noise_A = np.random.normal(p_rate_ex, p_rate_ex/par['std_noise'])
        rate_noise_inh = np.random.normal(p_rate_in, p_rate_in/par['std_noise'])
        nest.SetStatus(PG_noise_to_A, "rate", rate_noise_A)
        nest.SetStatus(PG_noise_to_B, "rate", rate_noise_B)
        nest.SetStatus(PG_noise_to_inh, "rate", rate_noise_inh)

        nest.Simulate(par['test_time'])

        self.simulation_results["rate_monitor_A"] = rate_monitor_A
        self.simulation_results["voltage_monitor_A"] = voltage_monitor_A
        self.simulation_results["spike_monitor_A"] = spike_monitor_A
        self.simulation_results["idx_monitored_neurons_A"] = idx_monitored_neurons_A

        self.simulation_results["rate_monitor_B"] = rate_monitor_B
        self.simulation_results["voltage_monitor_B"] = voltage_monitor_B
        self.simulation_results["spike_monitor_B"] = spike_monitor_B
        self.simulation_results["idx_monitored_neurons_B"] = idx_monitored_neurons_B

        self.simulation_results["rate_monitor_inh"] = rate_monitor_inh
        self.simulation_results["voltage_monitor_inh"] = voltage_monitor_inh
        self.simulation_results["spike_monitor_inh"] = spike_monitor_inh
        self.simulation_results["idx_monitored_neurons_inh"] = idx_monitored_neurons_inh
        
        self.simulation_results["train"] = []
        self.simulation_results["test"] = par["trials_side"]

    def run(self, sim_parameters):
        coherence = 0.512
        ret_vals = self.simulate_network(coherence, sim_parameters)
        return ret_vals
    
    def plot(self):

        self.generate_plots()
        
        # bin_size = 5
        
        # times_spike_monitor_DCN_a = [t for t in times_spike_monitor_DCN_a if t > self.train_time]
        # times_spike_monitor_DCN_b = [t for t in times_spike_monitor_DCN_b if t > self.train_time]
        # bin_rates_DCN_complete_a = calculate_bins(senders_spike_monitor_DCN_a, times_spike_monitor_DCN_a, len(self.idx_monitored_neurons_DCN_a)//2, bin_size, self.train_time, self.train_time+(self.test_time*self.test_number), self.test_number)
        # bin_rates_DCN_complete_b = calculate_bins(senders_spike_monitor_DCN_b, times_spike_monitor_DCN_b, len(self.idx_monitored_neurons_DCN_a)//2, bin_size, self.train_time, self.train_time+(self.test_time*self.test_number), self.test_number)

        # cdf_plots = []
        
        # for tt_index, tt in enumerate(self.test_types):
        #     bin_rates_a_portion = bin_rates_DCN_complete_a[tt_index]
        #     bin_rates_b_portion = bin_rates_DCN_complete_b[tt_index]
        #     json_title_a = file_handling.dict_to_json(bin_rates_a_portion, self.files_folder+'/bin_rates_DCN_a_test_'+str(tt_index))
        #     json_title_b = file_handling.dict_to_json(bin_rates_b_portion, self.files_folder+'/bin_rates_DCN_b_test_'+str(tt_index))

        #     moving_average_plot(bin_rates_a_portion, self.plots_folder, 'ma_rates_DCN_a_test_'+str(tt_index), (self.train_time+(self.test_time*tt_index), self.train_time+self.test_time+(self.test_time*tt_index)))

        #     cdf.calculate([json_title_a, json_title_b], self.plots_folder, 'cdf_test_'+str(tt_index), 5, 'save')

        #     # ma_plots.append(['ma_rates_DCN_a', 'ma_rates', 'test'])
        
        # cdf_plots = ['cdf', 'cdf', 'test']
        # merge_plots(self.plots_folder, cdf_plots, 'cdf', self.test_number, self.test_number)
    