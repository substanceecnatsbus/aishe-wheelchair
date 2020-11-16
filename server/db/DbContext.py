from pymongo import MongoClient
from pymongo.database import Database
from models.Record import Record
from pymongo.collection import Collection, ObjectId
from db.RecordSet import RecordSet

class DbContext:

  def __init__(self, db_username, db_name, db_password):
    self.client = MongoClient(f"mongodb+srv://{db_username}:{db_password}@gagongcluster.ybsgq.mongodb.net/{db_name}?retryWrites=true&w=majority")
    self.db: Database = self.client.wheelchairDB

    # self.records: DbSet[Record] = DbSet[Record](self.db.records)
    # self.records: = RecordSet
    # self.db.

    self.records: Collection = RecordSet(self.db.records)