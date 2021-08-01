import nest
import random

import numpy

def nest_reset(seed = random.randint(0,1000)):
    nest.ResetKernel()
    dt = 0.10
    msd = seed
    N_vp = nest.GetKernelStatus(['total_num_virtual_procs'])[0]
    # pyrngs = [numpy.random.RandomState(s) for s in range(msd, msd+N_vp)]
    nest.SetKernelStatus({"resolution": dt, "print_time": True, "overwrite_files": True, 'grng_seed': seed, 'rng_seeds' : range(msd+N_vp+1, msd+2*N_vp+1)})
    # nest.sli_run('0 << /grng rngdict/MT19937 :: 101 CreateRNG >> SetStatus')