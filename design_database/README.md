
# Database Design Work

Description: Mockups and designs for the database.

**Completed:**
- Mockup ER diagram. Generated mock sql files.
- Wrote script to fetch plant data from the [Perenual Plant Data API](https://perenual.com/) to generate test data for the database.

**TODO:**
- Generate placeholder data records for testing.
- Host the database locally using MySQL and test that it can be queried.

## Setting up a Local Database
- Begin by installing mySQL either by installing [mySQL Workbench](https://dev.mysql.com/downloads/workbench/) or by running:
    ```bash
    brew install mysql
    brew services start mysql
    mysql_secure_installation
    ```
- A MySQL process should now be listening on port 3306. Open a connection:
    ```bash
    mysql -u root -p -h localhost --port=3306
    ```
- Create the plant_project database:
    ```SQL
    CREATE DATABASE plant_project;
    USE plant_project;
    ```
- Create tables for the plant_project database. Find the absolute file path of the **.../design_database/mockup_mysql.sql** file. In the mySQL CLI run:
    ```SQL
    \. <absolute file path>
    ```
- Exit when finished with the connection.
    ```SQL
    exit
    ```
