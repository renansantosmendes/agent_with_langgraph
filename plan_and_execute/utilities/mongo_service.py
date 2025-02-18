from pymongo import MongoClient

class MongoDBClient:
    def __init__(
            self,
            uri="mongodb://localhost:27017",
            database="database",
            collection="collection"
    ):
        """Initialize the MongoDB client, database, and collection."""
        self.client = MongoClient(uri)
        self.db = self.client[database]
        self.collection = self.db[collection]

    def insert_document(self, document):
        """Insert a document into the collection."""
        result = self.collection.insert_one(document)
        print(f"Document inserted with ID: {result.inserted_id}")