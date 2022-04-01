from PIL import Image
from math import ceil

def merge_images(images, single_size, filename, col_number = 0, color = (240, 240, 240)):
    '''
        images: array di nomi dei file con le immagini da mergiare
        single_size: array con le misure da dare a ciascuna immagine
        filename: il nome da dare al file in output
        optional col_number: il numero di colonne nella nostra immagine finale, altrimenti vengono semplicemente messe in coda una all'altra
        optional color: il colore di background, che di default è grigio chiaro
    '''
    margin = 20

    if col_number:
        width = col_number * (single_size[0] + margin) + margin
        height = (ceil(len(images)/col_number)*single_size[1]) + ceil(len(images)/col_number) * margin + margin
    else:
        width = single_size[0] * len(images)*margin + margin
        height = single_size[1]+margin
    new_image = Image.new('RGB', (width, height), color)

    column_index = 0
    row_index = 0
    x_position = 0
    y_position = margin
    
    for img in images:
        image = Image.open(img)
        image = image.resize(single_size)
        if(column_index == col_number):
            column_index = 0
            row_index += 1
            x_position = margin
            y_position = (single_size[1]*row_index)+(margin*(row_index+1))
        else:
            x_position = (single_size[0]*column_index)+(margin*(column_index+1))
            y_position = (single_size[1]*row_index)+(margin*(row_index+1))
        column_index += 1
        new_position = (x_position, y_position)
        new_image.paste(image, new_position)

    new_image.save(filename ,"JPEG")