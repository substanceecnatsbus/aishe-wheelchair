from typing import Optional

class GSR():
  mini: Optional[float]
  maxi: Optional[float]
  mean: Optional[float]
  median: Optional[float]
  std: Optional[float]
  variance: Optional[float]

  def __init__(self, **entries):
    self.mini: Optional[float] = None
    self.maxi: Optional[float] = None
    self.mean: Optional[float] = None
    self.median: Optional[float] = None
    self.std: Optional[float] = None
    self.variance: Optional[float] = None
    self.__dict__.update(entries)

  # def __init__(self, mini = None, maxi = None, mean = None, median = None, std = None, variance = None):
  #   self.mini: Optional[float] = mini
  #   self.maxi: Optional[float] = maxi
  #   self.mean: Optional[float] = mean
  #   self.median: Optional[float] = median
  #   self.std: Optional[float] = std
  #   self.variance: Optional[float] = variance
