import nest

def nest_reset():
    nest.ResetKernel()
    dt = 0.10
    nest.SetKernelStatus({"resolution": dt, "print_time": True, "overwrite_files": True})