
# Database Design Work

Description: Mockups and designs for the database.

**Completed:**
- Mockup ER diagram. Generated mock sql files.
- Wrote script to fetch plant data from the [Perenual Plant Data API](https://perenual.com/) to generate test data for the database.
- Generate placeholder data records for testing.
- Host the database locally using MySQL and test that it can be queried.

**TODO:**
- Host the database locally using Postgres and test that it can be queried.
- Host the database on [Supabase](https://supabase.com/) and test that it can be queried.
- Investigate containerisation with Docker.

## Setting up a Local MySQL Database
- Begin by installing mySQL either by installing [mySQL Workbench](https://dev.mysql.com/downloads/workbench/) or by running:
    ```bash
    $ brew install mysql
    $ brew services start mysql
    $ mysql_secure_installation
    ```
- A MySQL process should now be listening on port 3306. Open a connection:
    ```bash
    $ mysql -u root -p -h localhost --port=3306
    ```
- Create the **plant_project** database:
    ```SQL
    CREATE DATABASE plant_project;
    USE plant_project;
    ```
- Create tables for the **plant_project** database. Find the absolute file path of the **`.../design_database/mockup_mysql.sql`** file. In the mySQL CLI run:
    ```SQL
    \. <absolute file path>
    ```
    An empty **plant_project** database with empty tables has been created.
- Exit when finished with the connection.
    ```SQL
    exit
    ```

## Inserting Test Data
- Install Python dependencies:
    ```bash
    $ pip install python-dotenv
    $ pip install mysql-connector-python
    $ pip install Faker
    $ pip install bcrypt
    $ pip install torch
    $ pip install transformers
    $ pip install accelerate
    $ pip install sentencepiece
    ```
- Create a `.env` file in the `design_database` directory containing your mySQL username and password:
    ```bash
    $ cd design_database/testdata_generator
    $ touch .env
    ```
    Open the file and edit it's contents:
    ```
    DB_USER=root
    DB_PASSWORD=<your_secure_password>
    ```
- Generate test data by running the Python script:
    ```bash
    $ python3 testdata_generator_mysql.py
    ```
    The **plant_project** database will now be populated with test data.

    To modify the behaviour of the script, you can tweak the parameters found at the top of the `testdata_generator_mysql.py` file:
    ```SQL
    NUM_USERS = 150
    USER_MIN_FOLLOWERS = 0
    USER_MAX_FOLLOWERS = 40
    NUM_LISTINGS = 300
    LISTING_MAX_QUANTITY = 20
    LISTING_PROBABILITY_OF_SECONDARYADDRESS = 0.5
    LISTING_GENERATE_DESCRIPTIONS = True
    LISTING_DESCRIPTION_MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
    LISTING_MIN_FAVORITES = 0
    LISTING_MAX_FAVORITES = 100
    ```
    The script performs the following actions when generating testing data:
    - For each user, a fake username and password is generated. The password is salted and hashed with bcrypt.
    For reference, the plaintext passwords are also saved to a csv file (although this file is not configured to be tracked by git).
    - Each user has between `USER_MIN_FOLLOWERS` and `USER_MAX_FOLLOWERS` followers generated, drawn without replacement.
    These are added to the follows table.
    - For each listing, a random plant from `data_plants.json` is selected, with replacement.
    `data_plants.json` supplies the common and scientific name of the plant.
    A random quantity between `1` and `LISTING_MAX_QUANTITY` is selected.
    A fake address is generated.
    A random user is selected to be the seller.
    If `LISTING_GENERATE_DESCRIPTIONS = True` then the Qwen 2.5 model will be pulled from [Hugging Face](https://huggingface.co/) (if it is not already cached) and this model will be used to generate a description of the listing.
    Note that the bulk of the runtime is dominated by LLM inference. If `LISTING_GENERATE_DESCRIPTIONS = False` then the script runs very quickly.
    - Each listing has between `LISTING_MIN_FAVORITES` and `LISTING_MAX_FAVORITES` favorites generated, drawn without replacement.
    These are added to the favorites table.
