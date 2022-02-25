import src.file_handling.csv_handling as csv_handling
import calendar
import time

def get_last():
    row = csv_handling.get_last_row('data/db/support.csv')
    return row

def get_last_id():
    row = get_last()
    return row[0] if len(row) else None

def new_row(notes=''):
    last_id = get_last_id()
    new_incremental_id = (last_id+1) if last_id else 1
    csv_handling.write_new_row('data/db/support.csv', [new_incremental_id, notes, calendar.timegm(time.gmtime())])
    return new_incremental_id