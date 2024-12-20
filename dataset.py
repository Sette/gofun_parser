
import numpy as np
import networkx as nx
import pandas as pd
import json
import ast
import keras
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
    def __init__(self, csv_file, labels_json, is_go=False):
        """
        Initializes the dataset, loading features (X), labels (Y), and optionally the hierarchy graph.
        """

        self.g = None
        self.nodes_idx = None
        self.g_t = None
        self.df = None
        self.graph_path = labels_json.replace('-labels.json', '.graphml')
        self.columns_path = labels_json.replace('-labels', '')
        self.load_structure(labels_json, is_go)
        with open(self.columns_path, 'r') as f:
            self.columns = json.load(f)

        self.load_data(
            csv_file, is_go
        )
        self.to_eval = [t not in to_skip for t in self.categories['labels']]


    def load_structure(self, labels_json, is_go):
        # Load labels JSON
        with open(labels_json, 'r') as f:
            self.categories = json.load(f)

        self.g = nx.DiGraph()

        for cat in self.categories['labels']:
            terms = cat.split('/')
            if is_go:
                self.g.add_edge(terms[1], terms[0])
            else:
                if len(terms) == 1:
                    self.g.add_edge(terms[0], 'root')
                else:
                    for i in range(2, len(terms) + 1):
                        self.g.add_edge('.'.join(terms[:i]), '.'.join(terms[:i - 1]))


        ### Save networkx graph
        # Para salvar em formato GraphML
        nx.write_graphml(self.g, self.graph_path)

        nodes = sorted(self.g.nodes(),
                key=lambda x: (nx.shortest_path_length(self.g, x, 'root'), x) if is_go else (len(x.split('.')), x)
        )
        self.nodes_idx = dict(zip(nodes, range(len(nodes))))
        self.g_t = self.g.reverse()



    def load_data(self, csv_file, is_go):
        """
        Load features and labels from CSV, and optionally a hierarchy graph from JSON.
        """
        # Load CSV
        self.df = pd.read_csv(csv_file)

        self.df['features'] = self.df.features.apply(lambda x : ast.literal_eval(x))

        def __process_feature(feature, idx):
            if self.columns['type'][idx] == 'numeric' or self.columns['type'][idx] == 'NUMERIC':
                if feature != '?':
                    return float(feature)
                else:
                    return None
            else:
                cats = self.columns['type'][idx][1:-1].split(',')
                cats_bin = {key:keras.utils.to_categorical(i, len(cats)).tolist() for i,key in enumerate(cats)}
                return cats_bin.get(feature, [0.0]*len(cats))

        # Features (X)
        def process_features(features):
            """
            Convert features from string to a numerical array.
            """
            return [__process_feature(f, i) for i, f in enumerate(features)]

        self.df['processed_features'] = self.df['features'].apply(process_features)




def initialize_dataset(name, fun_path, go_path):
    """
    Initialize train, validation, and test datasets.
    """
    datasets = load_dataset_paths(fun_path, go_path)
    train_csv, valid_csv, test_csv, labels_json, _ = datasets[name]
    train_data = Dataset(train_csv, labels_json, is_go=True)
    val_data = Dataset(valid_csv, labels_json, is_go=True)
    test_data = Dataset(test_csv, labels_json, is_go=True)
    return train_data, val_data, test_data
