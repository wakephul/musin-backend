
## General Information

The whole project has been developed and tested with Python 3.6 and NEST 2.18. In fact, these have been proven as the only conditions under which we were able to correctly install and import CerebNEST without big changes.
In order to make everything work with ease we dockerized everything, for everybody's convenience.
## Installation

The only requirement is to have **Docker** installed on your system.\
If you don't, please go ahead and install it.

After having downloaded this project, enter the main directory.

In order to create all the docker images that will be needed, just run:
```bash
docker-compose build
```

For security reasons, we have excluded the database password from the git repository. Just go ahead and create a *secrets.env* file in the environment folder.
It should contain 3 variables:
```
DB_PASSWORD=your_db_password
PMA_PASSWORD=your_pma_password
MYSQL_ROOT_PASSWORD=your_root_password
```

At this point, you can run:
```bash
docker-compose up
```
This will create all containers based on those images.

#### You should be ready to go.

To test that everything is working as expected, just look at your terminal. If you don't want to, or if everything looks ok, just navigate to http://localhost:5555/ and it should work.

If you want to create a test database, just navigate to http://localhost:5555/api/delete_db_and_populate_sample

Now you can start simulating your networks with the MuSiN!
## Support

For support and suggestions, please feel free to open an issue or to email me at riccardo (dot) cavadini (at) polimi (dot) it.
## Authors

- [@wakephul](https://www.twitter.com/wakephul)


![Logo](https://i.ibb.co/zffhCBm/Mu-Si-N-logo.png)