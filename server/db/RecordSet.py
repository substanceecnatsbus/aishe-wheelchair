import pymongo
from bson.objectid import ObjectId
from model.pymongo_model import SimpleModel, DiffHistoryModelV1, DiffHistoryModelV2
from models.Record import Record
from pymongo.collection import Collection
import json

class RecordSet():
  def __init__(self, collection: Collection):
    self.collection = collection

  def to_json(self, record: Record) -> str:
    return json.dumps(record, default=lambda o: o.__dict__)

  def to_doc(self, record: Record):
    return json.loads(self.to_json(record))

  def insert_one(self, record: Record) -> ObjectId:
    inserted_id = self.collection.insert_one(record.to_doc()).inserted_id
    print(f"Insert Record: {inserted_id}")
    return inserted_id


  def find_by_id(self, id) -> Record:
    found = self.collection.find_one({ "_id": ObjectId(id) })
    if found == None:
      print("Record not Found")
      return None

    record = Record.FromDict(**found)
    print(f"Found Record: {record._id}")
    return record
