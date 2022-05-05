def merge_sort_dicts_of_lists(dict1, dict2):
    print('\n', dict1, '\n\n', dict2, '\n')
    result_dict = dict1
    for i, j in dict2.items():
        if i in result_dict:
            result_dict[i]+=j
    
    return sort_dict_of_lists(result_dict)

def sort_dict_of_lists(dictionary):
    sorted_dict = {key : sorted(dictionary[key]) for key in sorted(dictionary)}
    return sorted_dict