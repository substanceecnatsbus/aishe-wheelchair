import tensorflow as tf
import pandas as pd
import numpy as np
import math

def load_model(num_features, model_path=None):
    if model_path == None:
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(num_features, )),
            tf.keras.layers.Dense(128, activation=tf.keras.activations.relu),
            tf.keras.layers.Dense(256, activation=tf.keras.activations.relu),
            tf.keras.layers.Dense(128, activation=tf.keras.activations.relu),
            tf.keras.layers.Dense(64, activation=tf.keras.activations.relu),
            tf.keras.layers.Dense(4, activation=tf.keras.activations.softmax)
        ])
        model.compile(
            optimizer = tf.keras.optimizers.Adam(),
            loss = tf.keras.losses.categorical_crossentropy,
            metrics = ["accuracy"]
        )
    else:
        model = tf.keras.models.load_model(model_path)
    return model

# TODO: normalize
def generate_dataset(num_features, split=None):
    corr_df = pd.read_csv("./neural_network/correlation.csv")
    feature_names = list(corr_df)[1:num_features+2]
    features_df = pd.read_csv("./neural_network/records.csv")
    features_df = features_df[feature_names]
    if split == None:
        x_train = features_df.drop("discomfort_level", 1).to_numpy()
        y_train = tf.one_hot(features_df["discomfort_level"].to_numpy(), 4)
        return x_train, y_train
    else:
        train_set = features_df.sample(frac=split)
        test_set = features_df.drop(train_set.index)
        x_train = train_set.drop("discomfort_level", 1).to_numpy()
        y_train = tf.one_hot(train_set["discomfort_level"].to_numpy(), 4)
        x_test = test_set.drop("discomfort_level", 1).to_numpy()
        y_test = tf.one_hot(test_set["discomfort_level"].to_numpy(), 4)
        return ((x_train, y_train), (x_test, y_test))

if __name__ == "__main__":
    num_features = 64
    x, y = generate_dataset(num_features)
    model = load_model(num_features, "./neural_network/model.hdf5")
    model.evaluate(x, y)
    # model.fit(x_train, y_train, epochs=10)
    # model.save("./models/model.hdf5")
    # model.evaluate(x_test, y_test)
    # print(np.argmax(model(np.expand_dims(x_train[0], axis=0))), y_train[0])