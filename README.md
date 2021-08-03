# Environment

The whole project has been developed and tested only with Python 3.6.9 and NEST 2.18. In fact, these have been proven as the only conditions under which we were able to correctly install and import CerebNEST.
The project has been run on Linux (Ubuntu 18.04.5) and MacOS (Catalina 10.15.7).


# How to use

**main.py** is the only file that will have to be executed most of the times.
It accepts two arguments:
- CreateSpikesTable: _boolean_, to be used if the db does not contain the 'spikes' table;
- CreateSpikes: _boolean_, to be used in order to create brand new sets of spikes (one per population). This will generate new pickle files (in the data/spikes/ directory) and add rows to the database.

# Timeline

In order to keep track of the main decisions that have been taken throughout the development process, a google doc file has been created and can be found at this link https://docs.google.com/document/d/1dwEzuM9EzCm5iHnLf5xwrhfLia-iF0Vh1lOtKBGmA1A/edit?usp=sharing
