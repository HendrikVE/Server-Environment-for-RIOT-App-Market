# Backend for the RIOT App Market

## Prerequisites
* Apache2 webserver
* MySQL database
* python
* python-mysqldb

## Setup
* create database 'riot_devices' and 'riot_os'
* add a new user 'backend_script' with following privileges only for 'riot_os' database (NOT GLOBAL!):
    * SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER
* change password for 'backend_script' in riotam-backend/db_config.py and riotam-backend/setup/db_config.py by the password you set by creating user 'backend_script'
* go to riotam-backend/setup and run 'python db_setup.py'
* update the database with db_update.py
* to create or update a stripped version of the RIOT repository run strip_riot_repo.py
