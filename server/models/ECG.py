from typing import Optional

class ECG():
  mean_rri: Optional[float]
  cvrr: Optional[float]
  sdrr: Optional[float]
  sdsd: Optional[float]
  lf: Optional[float]
  hf: Optional[float]
  ratio: Optional[float]
  heart_rate: Optional[float]
  
  def __init__(self, **entries):
    self.mean_rri: Optional[float] = None
    self.cvrr: Optional[float] = None
    self.sdrr: Optional[float] = None
    self.sdsd: Optional[float] = None
    self.lf: Optional[float] = None
    self.hf: Optional[float] = None
    self.ratio: Optional[float] = None
    self.heart_rate: Optional[float] = None
    self.__dict__.update(entries)
  # def __init__(self, mean_rri = None, cvrr = None, sdrr = None, sdsd = None, lf = None, hf = None, ratio = None, heart_rate = None, **entries):
  #   self.mean_rri: Optional[float] = mean_rri
  #   self.cvrr: Optional[float] = cvrr
  #   self.sdrr: Optional[float] = sdrr
  #   self.sdsd: Optional[float] = sdsd
  #   self.lf: Optional[float] = lf
  #   self.hf: Optional[float] = hf
  #   self.ratio: Optional[float] = ratio
  #   self.heart_rate: Optional[float] = heart_rate
