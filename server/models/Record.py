from models.ECG import ECG
from models.GSR import GSR
from models.MatrixItem import MatrixItem
from typing import Optional
import json
from datetime import datetime
from bson.timestamp import Timestamp
from bson.objectid import ObjectId
from utils.matrix import Matrix
from typing import List


class Record():
  '''Model for database data'''

  def __init__(self):
    self._id: ObjectId = None
    self.time: Timestamp = None
    self.ecg: ECG = ECG()
    self.gsr: GSR = GSR()
    self.pressure_matrix: List[MatrixItem] = []
    self.wetness_matrix: List[MatrixItem] = []
    self.discomfort_level: str = None

  @staticmethod
  def FromDict(**entries):
    record = Record()
    record.__dict__.update(entries)
    record.ecg = ECG(**record.ecg)
    record.gsr = GSR(**record.gsr)
    record.pressure_matrix = Matrix.FromDbToMatrixItems(record.pressure_matrix)
    record.wetness_matrix = Matrix.FromDbToMatrixItems(record.wetness_matrix)
    return record

  def to_json(self):
    # delete _id, para ung database mag generate ng _id, nagkakaproblem kase sa serialization ng id dito
    if self._id == None:
      del self._id

    return json.dumps(self, default=lambda o: o.__dict__)

  def to_doc(self):
    return json.loads(self.to_json())

  def dump(self, title=""):
    print(f"==> Record {title}\n----------")
    print(json.dumps(self, default=lambda o: o.__dict__ if hasattr(o, "__dict__") else o.__str__(), indent=4))
