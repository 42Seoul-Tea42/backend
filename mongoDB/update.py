import os
import pprint

from dotenv import load_dotenv
from pymongo import MongoClient

# Import objectId from bson package to enable querying by objectid
from bson.objectid import ObjectId

# load config from .env file
load_dotenv()
MONGODB_URI = os.environ["MONGODB_URI"]

#connect to mongoDB cluster with mongoClient
client = MongoClient(MONGODB_URI)

# get reference to 'bank' database
db = client.bank

# get reference to 'accounts' collection
account_collection = db.accounts

# Filter
document_to_update = {"_id": ObjectId("62d6e04ecab6d8e130497482")}

# Update
add_to_balance = {"$inc": {"balance": 100}}

# Print original document
pprint.pprint(accounts_collection.find_one(document_to_update))

# Write an expression that adds to the target account balance by the specified amount.
result = accounts_collection.update_one(document_to_update, add_to_balance)
print("Documents updated: " + str(result.modified_count))

# Print updated document
pprint.pprint(accounts_collection.find_one(document_to_update))

# Filter
select_accounts = {"account_type": "savings"}

# Update
set_field = {"$set": {"minimum_balance": 100}}

# Write an expression that adds a 'minimum_balance' field to each savings acccount and sets its value to 100.
result = accounts_collection.update_many(select_accounts, set_field)

print("Documents matched: " + str(result.matched_count))
print("Documents updated: " + str(result.modified_count))
pprint.pprint(accounts_collection.find_one(select_accounts))


client.close()



## ====================
# Filter
select_companies = {"name": { "$in" : ["Facebook", "LinkedIn"]}}

# Update
set_ipo = {"$set": {"ipo": True}}

result = companies_collection.update_many(select_companies, set_ipo)
