from pymongo import MongoClient
import pandas as pd

ecg_headers = [
    "mean_rri",
    "cvrr",
    "sdrr", 
    "sdsd",
    "lf", 
    "hf",
    "ratio",
    "heart_rate"
]
gsr_headers = [
    "mini",
    "maxi",
    "mean" ,
    "median",
    "std",
    "variance"
]
matrices = ["pressure_matrix", "wetness_matrix"]
discomfort_level_values = {
    "No Discomfort": 0,
    "Mild Discomfort": 1,
    "Moderate Discomfort": 2,
    "Severe Discomfort": 3
}

def get_records(output_path):
    client = MongoClient("mongodb+srv://user_1:RYHUNEPzmAlsE5VT@gagongcluster.ybsgq.mongodb.net/test?authSource=admin&replicaSet=atlas-1k9mdx-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true")

    db = client.wheelchairDB
    records = db.records.find()

    with open(output_path, "w") as fout:

        # write headers
        for ecg_header in ecg_headers:
            fout.write(f"{ecg_header},")
        for gsr_header in gsr_headers:
            fout.write(f"{gsr_header},")
        for matrix in matrices:
            for row in range(8):
                for col in range(8):
                    fout.write(f"{matrix}_{row}_{col},")
        fout.write("discomfort_level\n")

        # retrieve records
        for record in records:
            for key,val in record.items():
                if key == "ecg" or key == "gsr":
                    for k, v in val.items():
                        fout.write(f"{v},")
                elif key == "pressure_matrix" or key == "wetness_matrix":
                    for i, row in enumerate(val):
                        for j, col in enumerate(row):
                            fout.write(f"{col},")
                elif key == "discomfort_level":
                    fout.write(f"{discomfort_level_values[val]}\n")

def get_correlation_matrix(input_path, output_path):
    df = pd.read_csv(input_path)
    corr_df = df.corr()
    corr_df = corr_df.abs()
    corr_df = corr_df.sort_values("discomfort_level", ascending=False)
    corr_df = corr_df.transpose()
    corr_df.to_csv(output_path)
    
if __name__ == "__main__":
    import sys
    records_path = sys.argv[1]
    corr_path = sys.argv[2]
    get_records(records_path)
    get_correlation_matrix(records_path, corr_path)
    df = pd.read_csv(corr_path)
    for i, feature in enumerate(list(df)[2:]):
        print(i+1, feature)