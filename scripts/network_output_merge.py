import glob
import os
import sys

from pathlib import Path

def create_folder(directory):
    Path(directory).mkdir(parents=True, exist_ok=True)


if len(sys.argv) > 1:
    folder_id = str(sys.argv[1])
    if len(sys.argv) > 2:
        cortex_id = sys.argv[2]
    else:
        cortex_id = 'cortex_1/1'
    
    output_folder = "./output/executions/"+folder_id+"simulations/"+cortex_id
    create_folder(output_folder+'multimeters')
    create_folder(output_folder+'spike_detectors')

    # multimeters
    
    current_multimeters = glob.glob('*.dat')
    if (len(current_multimeters)):
        old_multimeters = glob.glob('./output/multimeters/*.dat')
        for old_multimeter in old_multimeters:
            os.remove(old_multimeter)

        new_multimeters = sorted(glob.glob("*.dat"))
        for multimeter in new_multimeters:
            multimeter_id = multimeter.split("-")[1]
            datfile = open(multimeter, "r")
            dattext = datfile.read()
            multimeter_filename = output_folder+"/multimeters/multimeter-"+multimeter_id+".dat"
            with open(multimeter_filename, "a+") as multimeter_file:
                multimeter_file.write(dattext)

        for multimeter in current_multimeters:
            os.remove(multimeter)

    # spike_detectors

    current_spike_detectors = glob.glob('*.gdf')
    if(len(current_spike_detectors)):
        old_spike_detectors = glob.glob('./output/spike_detectors/*.gdf')
        for old_spike_detector in old_spike_detectors:
            os.remove(old_spike_detector)

        new_spike_detectors = sorted(glob.glob("*.gdf"))
        for spike_detector in new_spike_detectors:
            spike_detector_id = spike_detector.split("-")[1]
            datfile = open(spike_detector, "r")
            dattext = datfile.read()
            spike_detector_filename = output_folder+"/spike_detectors/spike_detector-"+spike_detector_id+".gdf"
            with open(spike_detector_filename, "a+") as spike_detector_file:
                spike_detector_file.write(dattext)

        for spike_detector in current_spike_detectors:
            os.remove(spike_detector)