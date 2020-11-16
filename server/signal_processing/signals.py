class Signal:

    def __init__(self, feature_extractor):
        self.feature_extractor = feature_extractor
        self.t_points = []
        self.y_points = []

    def add_point(self, t, y):
        self.t_points.append(t)
        self.y_points.append(y)

    def clear_points(self):
        self.t_points = []
        self.y_points = []

    def get_duration(self):
        if len(self.t_points) < 2:
            return 0
        start_time = self.t_points[0]
        end_time = self.t_points[-1]
        return end_time - start_time

    def get_lag(self):
        if len(self.t_points) < 2:
            return 0
        previous_time = self.t_points[-2]
        current_time = self.t_points[-1]
        return current_time - previous_time

    def extract_features(self):
        return self.feature_extractor(self.t_points, self.y_points)

def main():
    # xD
    pass

if __name__ == "__main__":
    main()