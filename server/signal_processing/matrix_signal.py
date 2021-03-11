class Matrix_Signal:

    def __init__(self, name, threshold=0):
        self.clear_matrix()
        self.threshold = threshold
        self.name = name

    def update_cell(self, row, column, value, time):
        self.matrix[row][column] = value
        count += 1
        if count >= 64:
            count = 0
            print(f"{self.name} average: {self.get_average()}")
            if get_average() >= self.threshold: return 1
            else: return 2
        else: return 0
        # # use running average
        # previous_value = self.matrix[row][column]
        # if previous_value == 0:
        #     self.matrix[row][column] = value
        # else:
        #     self.matrix[row][column] = (self.matrix[row][column] + value) / 2

    def get_average(self):
        sum = 0
        for i in range(8):
            for j in range(8):
                sum += self.matrix[i][j]
        return sum / 64

    def clear_matrix(self):
        self.matrix = [[0 for __ in range(8)] for _ in range(8)]
        self.count = 0
