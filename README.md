# Backend for the RIOT App Market

## Prerequisites
* Apache2 webserver
* MySQL database
* python
* python-mysqldb

## Setup
0. Important to notice: Please run every command with 'sudo -u www-data'
1. go to setup/ and run 'python db_create' with your privileged user login data OR do it manually:
    * create database 'riot_os'
    * add a new user 'riotam_backend' with following privileges only for 'riot_os' database (NOT GLOBAL!): SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER
    * add a new user 'riotam_website' with following privileges only for 'riot_os' database (NOT GLOBAL!): SELECT
2. copy setup/db_config_EXAMPLES.py and rename the copy to db_config.py
3. copy config/db_config_EXAMPLES.py and rename the copy to db_config.py
4. change passwords in both of the db_config.py files to the passwords you set by creating user 'riotam_backend' and 'riotam-website'
5. go to setup/ and run 'python db_setup.py'
6. update the database with running 'python db_update.py'
7. to create or update a stripped version of the RIOT repository run 'python strip_riot_repo.py'
