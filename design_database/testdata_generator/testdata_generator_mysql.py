
import os
import sys
# import unicodedata
import csv
import json
import random
from decimal import Decimal
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode
from faker import Faker
import bcrypt
import torch
from transformers import pipeline, AutoModelForCausalLM,  AutoTokenizer

MYSQL_DB_NAME = 'plant_project'
FILE_DATA_PLANTS = 'data_plants.json'
FILE_PLAINTEXTPASSWORDS = 'data_users_plaintextpasswords.csv'

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

print(f"Starting Data Generation for Database {MYSQL_DB_NAME}...")
load_dotenv()

config = {
    'user': os.getenv('MYSQL_DB_USER'),
    'password': os.getenv('MYSQL_DB_PASSWORD'),
    'database': MYSQL_DB_NAME,
    'raise_on_warnings': True
}

if not os.path.exists(FILE_DATA_PLANTS):
    raise FileNotFoundError(f"Missing '{FILE_DATA_PLANTS}'. Please run 'python3 data_plants_fetcher.py' first.")

with open(FILE_DATA_PLANTS, 'r', encoding='utf-8') as file:
    data_plants = json.load(file)

if LISTING_GENERATE_DESCRIPTIONS:
    print("Setting up LLM for listings description generation...")
    listing_description_tokenizer = AutoTokenizer.from_pretrained(LISTING_DESCRIPTION_MODEL_ID)
    listing_description_model = AutoModelForCausalLM.from_pretrained(LISTING_DESCRIPTION_MODEL_ID, low_cpu_mem_usage=True)

    listing_description_pipeline = pipeline (
        "text-generation",
        model=listing_description_model,
        tokenizer=listing_description_tokenizer,
    )

def print_progress_bar(iteration, total, prefix='', length=40):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '░' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% Complete')
    sys.stdout.flush()
    if iteration == total:
        print()

def listing_description_create(generator, username, quantity, plant_name, scientific_name, address):
    prompt_messages = [
        {
            "role": "system", 
            "content": (
                "Write a casual online Marketplace listing description for a plant item. "
                "The description must sound like a regular person selling from home. Do NOT make an advertisement for a plant nursery. "
                "It is okay to include a brief bullet-point list of features or care tips. "
                "You may wish to allow the seller's personality to be reflected in their choice of words and formatting.\n\n"
                "Ensure your last line ends completely—do not leave sentences cut off."
            )
        },
        {
            "role": "user", 
            "content": (
                "Context for the listing description:\n"
                f"Plant Name: {plant_name} ({scientific_name})\n"
                f"Quantity available: {quantity}\n"
                f"Seller's Username: {username}\n"
                f"Location: Pickup from {address}\n\n"
            )
        }
    ]

    prompt = generator.tokenizer.apply_chat_template(
        prompt_messages, 
        tokenize=False, 
        add_generation_prompt=True
    )

    with torch.inference_mode():
        outputs = generator(
            prompt, 
            do_sample=True, 
            temperature=0.5,   
            top_p=0.9,
            max_new_tokens=200,
            eos_token_id=generator.tokenizer.eos_token_id, 
            pad_token_id=generator.tokenizer.eos_token_id,
            clean_up_tokenization_spaces=True
        )

    generated_description = outputs[0]['generated_text'][len(prompt):].strip()

    # The code block below manually removes the last sentence if the model gets cut off.
    # def is_valid_ending(char):
    #     if char in {'.', '!', ')', '"', '-', '\n'}:
    #         return True
    #     return unicodedata.category(char) in ['So', 'Sk'] # allow emojis
    
    # if generated_description and not is_valid_ending(generated_description[-1]):
    #     last_good_index = -1
    #     for i in range(len(generated_description) - 1, -1, -1):
    #         if is_valid_ending(generated_description[i]):
    #             last_good_index = i
    #             break
    #     if last_good_index != -1:
    #         generated_description = generated_description[:last_good_index + 1].strip()
    
    return generated_description

cnx = None
cursor = None

try:
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    fake = Faker(FAKER_LOCALE)

    query_next_userid = """
        SELECT AUTO_INCREMENT FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'user';
    """
    cursor.execute(query_next_userid, (MYSQL_DB_NAME,))
    next_userid = cursor.fetchone()[0]

    query_next_listingid = """
        SELECT AUTO_INCREMENT FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'listing';
    """
    cursor.execute(query_next_listingid, (MYSQL_DB_NAME,))
    next_listingid = cursor.fetchone()[0]

    add_user = """
        INSERT INTO user (
            email,
            password_hash,
            username,
            phone
        ) VALUES (%s, %s, %s, %s);
    """
    
    data_users = []
    data_users_plaintextpasswords = []

    print_progress_bar(0, NUM_USERS, prefix='user data', length=40)
    for i in range(NUM_USERS):
        username = fake.unique.user_name()
        password_plaintext = fake.password()
        password_hash = (
            bcrypt.hashpw(password_plaintext.encode('utf-8'), bcrypt.gensalt())
                .decode('utf-8')
        )

        data_users.append((
            f"{username}@{fake.free_email_domain()}",
            password_hash,
            username,
            fake.phone_number() if random.random() < USER_PROBABILITY_OF_PHONE else None
        ))
        data_users_plaintextpasswords.append([password_plaintext])

        print_progress_bar(i+1, NUM_USERS, prefix='user data', length=40)

    add_follow = """
        INSERT INTO follows (
            following_user_id,
            followed_user_id
        ) VALUES (%s, %s);
    """

    data_follows = []
    
    print_progress_bar(0, NUM_USERS, prefix='follow data', length=40)
    for i in range(NUM_USERS):
        user_id = next_userid + i
        num_follows = random.randint(USER_MIN_FOLLOWERS, min(USER_MAX_FOLLOWERS, NUM_USERS-1))

        follower_ids = random.sample(
            [id for id in range(next_userid, next_userid + NUM_USERS) if id != user_id],
            k=num_follows
        )
        for follower_id in follower_ids:
            data_follows.append((follower_id, user_id))

        print_progress_bar(i+1, NUM_USERS, prefix='follow data', length=40)

    add_listing = """
        INSERT INTO listing (
            name, scientific_name, quantity, price_perunit, currency_code, address_line_1, address_line_2,
            suburb, state, postal_code, country_code, description, seller_user_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    add_favorite = """
        INSERT INTO favorites (
            listing_id,
            user_id
        ) VALUES (%s, %s);
    """
    
    data_listings = []
    data_favorites = []

    print_progress_bar(0, NUM_LISTINGS, prefix='listing data', length=40)
    for i, random_plant in enumerate(random.choices(data_plants, k=NUM_LISTINGS)):
        quantity = random.randint(LISTING_MIN_QUANTITY, LISTING_MAX_QUANTITY)
        price_perunit = Decimal(str(round(random.uniform(LISTING_MIN_PRICE, LISTING_MAX_PRICE), 2)))
        suburb = fake.city()
        state = fake.state_abbr()
        country_code = fake.country_code(representation='alpha-2')
        description = ""
        seller_user_id = random.choice(list(range(next_userid, next_userid + NUM_USERS)))

        if LISTING_GENERATE_DESCRIPTIONS:
            description = listing_description_create(
                listing_description_pipeline,
                plant_name=random_plant["name"],
                scientific_name=random_plant["scientific_name"],
                quantity=quantity,
                address=suburb+", "+state,
                username=data_users[seller_user_id-next_userid][2]
            )

        data_listings.append((
            random_plant['name'], random_plant['scientific_name'], quantity, price_perunit, LISTING_CURRENCY_CODE,
            fake.street_address(), fake.secondary_address() if random.random() < LISTING_PROBABILITY_OF_SECONDARYADDRESS else None,
            suburb, state, fake.postcode(), country_code, description, seller_user_id,
        ))

        num_favorites = random.randint(LISTING_MIN_FAVORITES, min(LISTING_MAX_FAVORITES, NUM_USERS-1))
        favoriter_ids = random.sample(
            [id for id in range(next_userid, next_userid + NUM_USERS) if id != seller_user_id],
            k=num_favorites
        )
        for favoriter_id in favoriter_ids:
            data_favorites.append((next_listingid+i, favoriter_id))

        print_progress_bar(i+1, NUM_LISTINGS, prefix='listing data', length=40)

    cursor.executemany(add_user, data_users)
    cursor.executemany(add_follow, data_follows)
    cursor.executemany(add_listing, data_listings)
    cursor.executemany(add_favorite, data_favorites)

    cnx.commit()

    if FILE_PLAINTEXTPASSWORDS:
        with open(FILE_PLAINTEXTPASSWORDS, 'w', newline="", encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(data_users_plaintextpasswords)

except mysql.connector.Error as err:
    if cnx:
        cnx.rollback()
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Access Denied: Invalid username or password.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist.")
    else:
        print(err)
    sys.exit(1)
except Exception as err:
    if cnx:
        cnx.rollback()
    print(err)
    sys.exit(1)
finally:
    if cursor:
        cursor.close()
    if cnx and cnx.is_connected():
        cnx.close()
    print("Data Generation Script Complete.")
