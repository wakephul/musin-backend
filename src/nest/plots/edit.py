from src.file_handling.merge_images import merge_images
def merge_plots(output_folder = '', plots_to_create = [], merge_title = 'merge_title'):

    if (not output_folder or not plots_to_create): return
    
    filenames = [output_folder+'merged_plots/'+plot[0]+'.png' for plot in plots_to_create]
    merge_images(filenames, [500, 500], output_folder+merge_title'.jpg', 3)