import numpy
import src.file_handling.csv_handling as csv_handling
import calendar
import time

def get_last(file_path):
    row = csv_handling.get_last_row(file_path)
    return row

def get_last_id(file_path):
    row = get_last(file_path)
    return row[0] if isinstance(row, numpy.ndarray) else None

def new_row(notes='', file_path='data/db/support.csv', data=None, heading=None):
    new_incremental_id = 1
    if not heading:
        last_id = get_last_id(file_path)
        new_incremental_id = (last_id+1) if last_id else 1
        if not data:
            csv_handling.write_row(file_path, [new_incremental_id, notes, calendar.timegm(time.gmtime())])
        else:
            csv_handling.write_row(file_path, [new_incremental_id]+data)
    else:
        csv_handling.write_row(file_path, heading, new=False)
        
    return new_incremental_id