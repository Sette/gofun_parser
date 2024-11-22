
import numpy as np
import networkx as nx
import pandas as pd
import json
import ast

# Nós que devem ser ignorados
to_skip = ['root', 'GO0003674', 'GO0005575', 'GO0008150']



def load_json(file_path):
    """
    Loads a JSON file and returns its content.
    
    Args:
        file_path (str): Path to the JSON file.
    
    Returns:
        dict: Parsed JSON data as a dictionary.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


def load_dataset_paths(fun_path, go_path):
    datasets = {
        'cellcycle_FUN': (
            fun_path + '/cellcycle_FUN.train.csv',
            fun_path + '/cellcycle_FUN.valid.csv',
            fun_path + '/cellcycle_FUN.test.csv',
            fun_path + '/cellcycle_FUN-labels.json',
            fun_path + '/cellcycle_FUN.json'
        ),
        'derisi_FUN': (
            fun_path + '/derisi_FUN.train.csv',
            fun_path + '/derisi_FUN.valid.csv',
            fun_path + '/derisi_FUN.test.csv',
            fun_path + '/derisi_FUN-labels.json',
            fun_path + '/derisi_FUN.json'
        ),
        'eisen_FUN': (
            fun_path + '/eisen_FUN.train.csv',
            fun_path + '/eisen_FUN.valid.csv',
            fun_path + '/eisen_FUN.test.csv',
            fun_path + '/eisen_FUN-labels.json',
            fun_path + '/eisen_FUN.json'
        ),
        'expr_FUN': (
            fun_path + '/expr_FUN.train.csv',
            fun_path + '/expr_FUN.valid.csv',
            fun_path + '/expr_FUN.test.csv',
            fun_path + '/expr_FUN-labels.json',
            fun_path + '/expr_FUN.json'
        ),
        'gasch1_FUN': (
            fun_path + '/gasch1_FUN.train.csv',
            fun_path + '/gasch1_FUN.valid.csv',
            fun_path + '/gasch1_FUN.test.csv',
            fun_path + '/gasch1_FUN-labels.json',
            fun_path + '/gasch1_FUN.json'
        ),
        'gasch2_FUN': (
            fun_path + '/gasch2_FUN.train.csv',
            fun_path + '/gasch2_FUN.valid.csv',
            fun_path + '/gasch2_FUN.test.csv',
            fun_path + '/gasch2_FUN-labels.json',
            fun_path + '/gasch2_FUN.json'
        ),
        'seq_FUN': (
            fun_path + '/seq_FUN.train.csv',
            fun_path + '/seq_FUN.valid.csv',
            fun_path + '/seq_FUN.test.csv',
            fun_path + '/seq_FUN-labels.json',
            fun_path + '/seq_FUN.json'
        ),
        'spo_FUN': (
            fun_path + '/spo_FUN.train.csv',
            fun_path + '/spo_FUN.valid.csv',
            fun_path + '/spo_FUN.test.csv',
            fun_path + '/spo_FUN-labels.json',
            fun_path + '/spo_FUN.json'
        ),
        'cellcycle_GO': (
            go_path + '/cellcycle_GO.train.csv',
            go_path + '/cellcycle_GO.valid.csv',
            go_path + '/cellcycle_GO.test.csv',
            go_path + '/cellcycle_GO-labels.json',
            go_path + '/cellcycle_GO.json'
        ),
        'derisi_GO': (
            go_path + '/derisi_GO.train.csv',
            go_path + '/derisi_GO.valid.csv',
            go_path + '/derisi_GO.test.csv',
            go_path + '/derisi_GO-labels.json',
            go_path + '/derisi_GO.json'
        ),
        'eisen_GO': (
            go_path + '/eisen_GO.train.csv',
            go_path + '/eisen_GO.valid.csv',
            go_path + '/eisen_GO.test.csv',
            go_path + '/eisen_GO-labels.json',
            go_path + '/eisen_GO.json'
        ),
        'expr_GO': (
            go_path + '/expr_GO.train.csv',
            go_path + '/expr_GO.valid.csv',
            go_path + '/expr_GO.test.csv',
            go_path + '/expr_GO-labels.json',
            go_path + '/expr_GO.json'
        ),
        'gasch1_GO': (
            go_path + '/gasch1_GO.train.csv',
            go_path + '/gasch1_GO.valid.csv',
            go_path + '/gasch1_GO.test.csv',
            go_path + '/gasch1_GO-labels.json',
            go_path + '/gasch1_GO.json'
        ),
        'gasch2_GO': (
            go_path + '/gasch2_GO.train.csv',
            go_path + '/gasch2_GO.valid.csv',
            go_path + '/gasch2_GO.test.csv',
            go_path + '/gasch2_GO-labels.json',
            go_path + '/gasch2_GO.json'
        ),
        'seq_GO': (
            go_path + '/seq_GO.train.csv',
            go_path + '/seq_GO.valid.csv',
            go_path + '/seq_GO.test.csv',
            go_path + '/seq_GO-labels.json',
            go_path + '/seq_GO.json'
        ),
        'spo_GO': (
            go_path + '/spo_GO.train.csv',
            go_path + '/spo_GO.valid.csv',
            go_path + '/spo_GO.test.csv',
            go_path + '/spo_GO-labels.json',
            go_path + '/spo_GO.json'
        ),
    }
    
    return datasets



class Dataset:
    def __init__(self, csv_file, labels_json, hierarchy_json=None, is_GO=False, is_test=False):
        """
        Initializes the dataset, loading features (X), labels (Y), and optionally the hierarchy graph.
        """
        self.X, self.Y, self.terms, self.g = self.load_data(
            csv_file, labels_json, hierarchy_json, is_GO, is_test
        )
        self.to_eval = [t not in to_skip for t in self.terms]

        # Handle missing values in X
        r_, c_ = np.where(np.isnan(self.X))
        m = np.nanmean(self.X, axis=0)
        for i, j in zip(r_, c_):
            self.X[i, j] = m[j]

    def load_data(self, csv_file, labels_json, hierarchy_json, is_GO, is_test):
        """
        Load features and labels from CSV, and optionally a hierarchy graph from JSON.
        """
        # Load CSV
        df = pd.read_csv(csv_file)

        df['features'] = df.features.apply(lambda x : ast.literal_eval(x))

        # Features (X)
        def process_features(features):
            """
            Convert features from string to a numerical array.
            """
            return np.array([float(f) if f is not None and type(f) != str else f for f in features])

        df['processed_features'] = df['features'].apply(process_features)
        X = np.stack(df['processed_features'].values)

        # Load labels JSON
        with open(labels_json, 'r') as f:
            terms = json.load(f)

        # Labels (Y)
        def process_labels(labels):
            """
            Convert hierarchical labels to binary array.
            """
            y = np.zeros(len(terms))
            for label in labels:
                y[[terms.index(term) for term in label if term in terms]] = 1
            return y

        df['binary_labels'] = df['categories'].apply(process_labels)
        Y = np.stack(df['binary_labels'].values)

        # Load hierarchy JSON (optional)
        if hierarchy_json:
            with open(hierarchy_json, 'r') as f:
                hierarchy = json.load(f)
            g = nx.DiGraph(hierarchy)
        else:
            g = nx.DiGraph()

        return X, Y, terms, g


def initialize_dataset(name, fun_path, go_path):
    """
    Initialize train, validation, and test datasets.
    """
    datasets = load_dataset_paths(fun_path, go_path)
    train_csv, valid_csv, test_csv, labels_json, hierarchy_json = datasets[name]
    train_data = Dataset(train_csv, labels_json, hierarchy_json, is_GO=True)
    val_data = Dataset(valid_csv, labels_json, hierarchy_json, is_GO=True)
    test_data = Dataset(test_csv, labels_json, hierarchy_json, is_GO=True, is_test=True)
    return train_data, val_data, test_data
