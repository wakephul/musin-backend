# Environment

The whole project has been developed and tested only with Python 3.6 and NEST 2.18. In fact, these have been proven as the only conditions under which we were able to correctly install and import CerebNEST.
In order to make everything work with ease we dockerized everything, for everybody's convenience.

# How to use

**docker-compose build** creates all the docker images that will be needed.

For security reasons, we have excluded the database password from the git repository. Just go ahead and create a secrets.env file in the environment folder.
It should contain 3 variables:
DB_PASSWORD=your_db_password
PMA_PASSWORD=your_pma_password
MYSQL_ROOT_PASSWORD=your_root_password

**docker-compose up** will create the containers based on those images. You will be ready to go.


