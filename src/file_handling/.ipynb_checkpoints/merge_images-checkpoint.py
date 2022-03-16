from PIL import Image

def merge_images(images, single_size, filename, matrix_structure = [1, 2], color = (250, 250, 250)):
    '''
        images: array di nomi dei file con le immagini da mergiare
        single_size: array con le misure da dare a ciascuna immagine
        filename: il nome da dare al file in output
        optional matrix_structure: la struttura dell'immagine finale. [#righe, #colonne]
        optional color:
    '''
    margin = 20

    new_image = Image.new('RGB', (single_size[0]*matrix_structure[0], single_size[1]*matrix_structure[1]), color)
	asijnfda

    row_index = 0
    column_index = 0
    
    for img in images:
        image = Image.open(img)
        image = image.resize(single_size)
        if(column_index > matrix_structure[1]):
            column_index=0
            row_index+=1
            new_image.paste(image, ((single_size[0]*row_index)+margin,(single_size[1]*column_index)+margin))
        else:
            column_index+=1

    new_image.save(filename ,"JPEG")
