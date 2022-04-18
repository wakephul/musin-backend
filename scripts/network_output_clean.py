import glob
import os

def network_output_clean():
    # multimeters
    current_multimeters = glob.glob('*.dat')
    if (len(current_multimeters)):
        for multimeter in current_multimeters:
            os.remove(multimeter)

    # spike_detectors
    current_spike_detectors = glob.glob('*.gdf')
    if(len(current_spike_detectors)):
        for spike_detector in current_spike_detectors:
            os.remove(spike_detector)

if __name__ == '__main__':
    network_output_clean()