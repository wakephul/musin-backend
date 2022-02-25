import pandas as pd

def read_file(filename):
    data = pd.read_csv(filename, sep=',') 
    return data.values

def get_last_row(filename):
    file = read_file(filename)
    return file[-1] if len(file) else None

def write_new_row(filename, values):
    with open(filename, 'a') as file:
        file.write('\n'+','.join(map(str,values)))