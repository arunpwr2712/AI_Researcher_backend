from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "research_summaries"
COLLECTION_NAME = "summaries"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
summaries_collection = db[COLLECTION_NAME]


def get_summary_from_db(doi: str = None, title: str = None):
    query = {}
    if doi:
        query["doi"] = doi
    elif title:
        query["title"] = title

    return summaries_collection.find_one(query)


def save_summary_to_db(summary: dict):
    summaries_collection.update_one(
        {"doi": summary.get("doi")},
        {"$set": summary},
        upsert=True
    )
