from typing import List, ClassVar, Optional

class MatrixItem():
  row: Optional[int]
  col: Optional[int]
  value: Optional[float]

  def __init__(self, **entries):
    self.row: Optional[int] = None
    self.col: Optional[int] = None
    self.value: Optional[float] = None
    self.__dict__.update(entries)

  # def __init__(self, row = None, col = None, value = None):
  #   self.row: Optional[int] = row
  #   self.col: Optional[int] = col
  #   self.value: Optional[float] = value
