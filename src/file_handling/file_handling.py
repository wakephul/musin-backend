import time, codecs, json
import numpy as np
import pickle

def ndarray_to_json(list_of_lists, file_name = ''):

    file_path = 'data/' + file_name + '{}.json'.format(int(time.time()))

    # to solve "TypeError: Object of type 'ndarray' is not JSON serializable" and varous other conversion problems
    array = json.dumps(list(np.array([json.dumps(list(map(str, list(np.array(xi))))) for xi in list_of_lists])))
    arr = []
    for x in list_of_lists:
        arr.append(list(map(str,(list(np.array(x))))))
    
    if (file_name):
        dump_to_json(arr, file_path)

    return arr

def dict_to_json(dictionary, file_name):
    file_path = 'data/' + file_name + '{}.json'.format(int(time.time()))

    dump_to_json(dictionary, file_path)
    return file_path

def dump_to_json(obj, file_path):
    json.dump(obj, codecs.open(file_path, 'w+', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4) ### this saves the array in .json format

def read_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_to_file(object, file_name):
    file_path = 'data/' + file_name + '{}.p'.format(int(time.time()))

    with open(file_path, 'wb+') as fp:
        pickle.dump(object, fp, protocol=pickle.HIGHEST_PROTOCOL)

    return file_path

def file_open(file_path):
    
    with open(file_path, 'rb') as fp:
        file_contents = pickle.load(fp)
    
    return file_contents

def write_to_file(filename, string):
    with open(filename, "w+") as file:
        file.write(string) 