## General Information

The whole project has been developed and tested with Python 3.6 and NEST 2.18. In fact, these have been proven as the only conditions under which we were able to correctly install and import CerebNEST without big changes.

In order to make everything work with ease we dockerized everything, for everybody's convenience.

## Installation

The only requirement is to have **Docker** installed on your system.

If you don't, please go ahead and install it.

After having downloaded this project, enter the main directory.

For security reasons, we have excluded the database password from the git repository. Just go ahead and create a _secrets.env_ file in the environment folder.

It should contain 3 variables:

```

DB_PASSWORD=your_password

PMA_PASSWORD=your_password

MYSQL_ROOT_PASSWORD=your_root_password

```

**Important**: if you change these at some point, you should delete the mysql cache :)

In order to create all the docker images that will be needed, just run:

```bash

docker compose build

```

At this point, you can run:

```bash

docker compose up

```

This will create all containers based on those images.

If you want to run it in detached mode (_recommended usage_), just add the -d flag:

```bash

docker compose up -d

```

#### You should be ready to go.

To test that everything is working as expected, just look at your terminal. If you don't want to, or if everything looks ok, just navigate to http://localhost:5555/ and it should work.

If you want to create a sample database, just navigate to http://localhost:5555/api/delete_db_and_populate_sample

If you want to check the status of your database, you can easily do that thanks to phpMyAdmin, which you can find at http://localhost:8888/

Now you can start simulating your networks!

## Usage

### API calls

In order to interact with the available endpoints, we are working on a web application that will simplify the whole process.

In the meanwhile, you can use an API platform such as [Postman](https://www.postman.com/).

##### Simulating a network

1. Make sure that your network is implemented correctly
2. Make sure that your database contains information about the network you want to simulate and the inputs you want to provide.
   For testing purposes, you can:
   1. Insert network and input parameters inside the welcome.py file;
   2. Navigate to /api/delete_db_and_populate_sample (notice that this will override your database!)
3. GET /api/networks/list/ and obtain information about your networks (inclusing their codes)
4. GET /api/inputs/list/ and obtain information about your inputs
5. POST all the needed information to /api/executions/new/, in the form of (TO BE ADDED)

### Networks

Each network shoud extend **BaseNetwork**. This will enable the usage of:

- self.input_folder
- self.output_folder
- self.plot_folder
- self.nest_data_folder

You should use these paths to save your results.

In order to finally implement your network, please refer to how Cerebellum is implemented. In particular, remember to add it to the imports of run.py and to the available_networks dictionary.

## Support

For support and suggestions, please feel free to open an issue or to email me at riccardo (dot) cavadini (at) polimi (dot) it.

## Authors

- [@wakephul](https://www.twitter.com/wakephul)
- [@albertoantonietti](https://github.com/alberto-antonietti)

![Logo](https://i.ibb.co/zffhCBm/Mu-Si-N-logo.png)
