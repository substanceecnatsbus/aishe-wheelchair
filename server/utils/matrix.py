import random
from models.MatrixItem import MatrixItem
from typing import List


class Matrix():

  # Method to create matrix with random values
  @staticmethod
  def RandomMatrix(matrix_size: int):
    matrix = []
    for _ in range(matrix_size):
      row = [random.randint(1, 500) for c in range(matrix_size)]
      matrix.append(row)

    return matrix

  @staticmethod
  def ToMatrixItems(matrix) -> List[MatrixItem]:
    # Assert lang para mas madali
    assert(len(matrix) != 0)
    assert(len(matrix[0]) != 0)

    result = []
    for r in range(len(matrix)):
      for c in range(len(matrix[0])):
        matrixItem = MatrixItem(row=r, col=c, value=matrix[r][c])
        result.append(matrixItem)
    
    return result

  # Method to print matrix
  @staticmethod
  def PrintMatrix(matrix, title=None, trail_newline=True):
    if title: print(f"==> {title}\n----------")
    for row in matrix:
      print(row)
    
    if trail_newline: print()

  @staticmethod
  def PrintItems(matrix_items, less=True, max_row = 10, title=None, trail_newline=True):
    if title: print(f"==> {title}\n----------")

    length = len(matrix_items)
    print_until = max_row if less else length

    for i in range(print_until):
      print(matrix_items[i].__dict__)

    if less:
      print("...")
      print(f"Showing {max_row} of {length} items...")

    if trail_newline: print()

  @staticmethod
  def FromDbToMatrixItems(matrix) -> List[MatrixItem]:
    result = []
    for item in matrix:
      result.append(MatrixItem(row=item['row'], col=item['col'], value=item['value']))

    return result
