class Matrix_Signal:

    def __init__(self):
        self.clear_matrix()

    def update_cell(self, row, column, value, time):
        self.matrix[row][column] = value
        # # use running average
        # previous_value = self.matrix[row][column]
        # if previous_value == 0:
        #     self.matrix[row][column] = value
        # else:
        #     self.matrix[row][column] = (self.matrix[row][column] + value) / 2

    def clear_matrix(self):
        self.matrix = [[0 for __ in range(8)] for _ in range(8)]
