def create_spikes_table():
    return " \
        CREATE TABLE IF NOT EXISTS spikes ( \
            spikeID integer PRIMARY KEY AUTOINCREMENT, \
            filename varchar(255) NOT NULL, \
            updated boolean NOT NULL, \
            creation timestamp DEFAULT CURRENT_TIMESTAMP \
        ); \
    "

def select_existing_spikes():
    return " \
        SELECT * FROM spikes \
        WHERE updated = 1 \
        ORDER BY creation ASC \
    "

def insert_new_spikes():
    return " \
        INSERT INTO spikes(filename, updated) \
        VALUES(?,?) \
        ; \
    "