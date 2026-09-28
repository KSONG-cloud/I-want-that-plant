
# Database Design Work

Description: Mockups and designs for the database.

**Completed:**
- Mockup ER diagram. Generated mock sql files.
- Wrote script to fetch plant data from the [Perenual Plant Data API](https://perenual.com/) to generate test data for the database.
- Generate placeholder data records for testing.
- Host the database locally using MySQL and test that it can be queried.
- Host the database locally using Postgres and test that it can be queried.

**TODO:**
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

## Inserting Test Data into Local MySQL Database
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
    FAKER_LOCALE = "en_AU"
    NUM_USERS = 150
    USER_PROBABILITY_OF_PHONE = 0.8
    USER_MIN_FOLLOWERS = 0
    USER_MAX_FOLLOWERS = 40
    NUM_LISTINGS = 300
    LISTING_MIN_QUANTITY = 1
    LISTING_MAX_QUANTITY = 20
    LISTING_MIN_PRICE = 0
    LISTING_MAX_PRICE = 500
    LISTING_CURRENCY_CODE = "AUD"
    LISTING_PROBABILITY_OF_SECONDARYADDRESS = 0.5
    LISTING_GENERATE_DESCRIPTIONS = False
    LISTING_DESCRIPTION_MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
    LISTING_MIN_FAVORITES = 0
    LISTING_MAX_FAVORITES = 100
    ```
    The script performs the following actions when generating testing data:
    - Fake data is generated with geographical bias according to `FAKER_LOCALE`.
    - For each user, a fake email, password, username and phone number is generated. The password is salted and hashed with bcrypt.
    For reference, the plaintext passwords are also saved to a csv file (although this file is not configured to be tracked by git).
    - Each user has between `USER_MIN_FOLLOWERS` and `USER_MAX_FOLLOWERS` followers generated, drawn without replacement.
    These are added to the follows table.
    - For each listing, a random plant from `data_plants.json` is selected, with replacement.
    `data_plants.json` supplies the common and scientific name of the plant.
    A random quantity between `LISTING_MIN_QUANTITY` and `LISTING_MAX_QUANTITY` is selected.
    A random price between `LISTING_MIN_PRICE` and `LISTING_MAX_PRICE` is selected (currency code is currently hardcoded to "AUD").
    A fake address is generated.
    A random user is selected to be the seller.
    If `LISTING_GENERATE_DESCRIPTIONS = True` then the Qwen 2.5 model will be pulled from [Hugging Face](https://huggingface.co/) (if it is not already cached) and this model will be used to generate a description of the listing.
    Note that the bulk of the runtime is dominated by LLM inference. If `LISTING_GENERATE_DESCRIPTIONS = False` then the script runs very quickly.
    - Each listing has between `LISTING_MIN_FAVORITES` and `LISTING_MAX_FAVORITES` favorites generated, drawn without replacement.
    These are added to the favorites table.

## Setting up a Local Postgres Database
- Begin by installing Postgres (on macOS) by running:
    ```bash
    $ brew install postgresql@17
    $ brew services start postgresql@17
    ```
- A Postgres process should now be listening on TCP port 5432. Open a connection:
    ```bash
    $ psql postgres
    ```
- Setup password authentication.
    ```SQL
    ALTER SYSTEM SET password_encryption = 'scram-sha-256';
    SELECT current_user;
    \password
    SHOW hba_file;
    \q
    ```
    Open the hba_file and edit all entries in the `METHOD` column to `scram-sha-256`.
    They should not say `trust`.
    Now restart postgres to ensure that authentication has been enabled.
    You should be prompted to enter the password that you just set.
    ```bash
    $ brew services restart postgresql@17
    $ psql -h localhost -U YOUR_USERNAME -d postgres
    ```
- Setup a mock certificate authority and Postgres server certificate to enable TLS.
    - First we simulate a root certificate authority. Make a directory for the mock CA. Create a private key and generate a self signed certificate.
        ```bash
        $ mkdir -p ~/.mock_CA
        $ chmod 700 ~/.mock_CA
        $ cd ~/.mock_CA
        $ openssl genrsa -out mock_ca.key 4096
        $ chmod 600 mock_ca.key
        $ openssl req -x509 -new -key mock_ca.key -sha256 -days 3650 -out mock_ca.crt \
            -subj "/C=AU/O=Mock Root CA/CN=Mock Root CA"
        ```
    - Open a seperate terminal in your project directory and make a directory for the mock server certificate. Create a private key and certificate signing request. Specify desired certificate extensions in `.ext` file. Send the request to the mock root CA for signing.
        ```bash
        $ cd <project_directory>/design_database/testdata_generator
        $ mkdir -p mock_tlscert
        $ chmod 700 mock_tlscert
        $ cd mock_tlscert
        $ openssl genrsa -out mock_psqlserver.key 2048
        $ chmod 600 mock_psqlserver.key
        $ openssl req -new -key mock_psqlserver.key -out mock_psqlserver.csr \
            -subj "/C=AU/O=Local PostgreSQL Test/CN=localhost"
        $ cat > mock_psqlserver.ext <<'EOF'
        subjectAltName = DNS:localhost,IP:127.0.0.1,IP:::1
        extendedKeyUsage = serverAuth
        EOF
        $ cp mock_psqlserver.csr ~/.mock_CA
        $ cp mock_psqlserver.ext ~/.mock_CA
        ```
    - In `~/.mock_CA`, sign the certificate request. Send the signed certificate as well as the root CA public certificate to the server:
        ```bash
        $ cd ~/.mock_CA
        $ openssl x509 -req -in mock_psqlserver.csr -CA mock_ca.crt -CAkey mock_ca.key -CAcreateserial \
            -out mock_psqlserver.crt -days 825 -sha256 -extfile mock_psqlserver.ext
        $ cp mock_psqlserver.crt <project_directory>/design_database/testdata_generator/mock_tlscert/
        $ cp mock_ca.crt <project_directory>/design_database/testdata_generator/mock_tlscert/
        ```
    We now have a full simulated trust relationship. When the client receives `mock_psqlserver.crt` from the server, it can verify that this certificate was signed by its trusted root CA using `mock_ca.crt` which is publically available. For instance, run:
    ```bash
    $ openssl verify -CAfile mock_ca.crt mock_psqlserver.crt
    ```
- Configure postgres to require TLS connections only:
    ```bash
    $ psql -h localhost -U YOUR_USERNAME -d postgres
    ```
    ```SQL
    ALTER SYSTEM SET ssl = 'on';
    ALTER SYSTEM SET ssl_cert_file = 'mock_psqlserver.crt';
    ALTER SYSTEM SET ssl_key_file = 'mock_psqlserver.key';
    SHOW data_directory;
    \q
    ```
    Move the certificates into the data directory:
    ```bash
    $ cd <project_directory>/design_database/testdata_generator/mock_tlscert
    $ cp mock_psqlserver.crt <data_directory_path>/
    $ cp mock_psqlserver.key <data_directory_path>/
    $ chmod 600 <data_directory_path>/mock_psqlserver.key
    ```
    Open the hba_file and edit localhost TCP rules from host to hostssl. That is, all instances of `host` in the `TYPE` column should be changed to `hostssl`.
    Restart the Postgres process and log in with TLS:
    ```bash
    $ cd <project_directory>/design_database/testdata_generator/mock_tlscert
    $ brew services restart postgresql@17
    $ psql "host=localhost dbname=postgres user=YOUR_USERNAME sslmode=verify-full sslrootcert=mock_ca.crt"
    ```
    We now have a TLS encrypted active connection with Postgres.
- Create the **plant_project** database:
    ```SQL
    CREATE DATABASE plant_project;
    \c plant_project
    ```
- Create tables for the **plant_project** database. Find the absolute file path of the **`.../design_database/mockup_postgres.sql`** file. In the Postgres CLI run:
    ```SQL
    \i <absolute file path>
    \q
    ```
    An empty **plant_project** database with empty tables has been created.
- To insert testing data:
    ```bash
    $ pip install python-dotenv
    $ pip install psycopg
    $ pip install Faker
    $ pip install bcrypt
    $ pip install torch
    $ pip install transformers
    $ pip install accelerate
    $ pip install sentencepiece

    $ python3 testdata_generator_postgres.py
    ```
    The **plant_project** database will now be populated with test data.
- Stop the Postgres process when finished.
    ```bash
    $ brew services stop postgresql@17
    ```
