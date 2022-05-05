from src.file_handling.merge_images import merge_images

plots_to_create = [
	['spike_monitor_A', 'raster'],
	['spike_monitor_B', 'raster'],
	['spike_monitor_Z', 'raster'],
	['spike_monitor_inhib', 'raster'],
	['voltage_monitor_A', 'voltage'],
	['voltage_monitor_B', 'voltage'],
	['voltage_monitor_Z', 'voltage'],
	['voltage_monitor_inhib', 'voltage']
]
current_plots_folder = 'output/plots/34/'
filenames = [current_plots_folder+'plots/'+plot[0]+'.png' for plot in plots_to_create]
merge_images(filenames, [500, 500], current_plots_folder+'plots.jpg', 3)