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
3. copy config/config_EXAMPLES.py and rename the copy to config.py
4. change passwords in db_config.py and config.py to the passwords you set by creating user 'riotam_backend' and 'riotam-website'
5. replace USER_PRIVILEGED and PASSWORD_PRIVILEGED by your values
6. go to setup/ and run 'python db_setup.py'
7. update the database with running 'python db_update.py'
8. to create or update a stripped version of the RIOT repository run 'python strip_riot_repo.py'

### More Information
Graphics are editable with [yEd](http://www.yworks.com/products/yed "http://www.yworks.com/products/yed")

## LICENSE
* The project is licensed under the GNU Lesser General Public License
  (LGPL) version 2.1 as published by the Free Software Foundation.

All code files contain licensing information.