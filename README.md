# How to use

**main.py** is the only file that will have to be executed most of the times.
It accepts two arguments:
- CreateSpikesTable: _boolean_, to be used if the db does not contain the 'spikes' table;
- CreateSpikes: _boolean_, to be used in order to create brand new sets of spikes (one per population). This will generate new pickle files (in the data/spikes/ directory) and add rows to the database.