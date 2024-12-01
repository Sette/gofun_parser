import json
import pandas as pd
import os
import keras
from tqdm import tqdm

tqdm.pandas()

class GoFunCSVParser:
    def __init__(self, input_file, output_file):
        """
        Initialize the parser with input and output file paths.

        Args:
            input_file (str): Path to the input file with hierarchical data.
            output_file (str): Path to save the converted CSV file.
        """
        self.input_file = input_file
        self.output_file = output_file
        if 'train' in output_file:
            self.output_atributes_file = output_file.replace('.train', '')
        elif 'test' in output_file:
            self.output_atributes_file = output_file.replace('.test', '')
        else:
            self.output_atributes_file = output_file.replace('.valid', '')
        self.output_atributes_file = self.output_atributes_file.replace('.csv','.json')
        self.output_labels_file = self.output_atributes_file.replace('.json', '-labels.json')
        self.atributes_names = {'name': [], 'type': []}
        self.processed_lines = []
        self.lines = []

    def load_data(self):
        """
        Load the data from the input file into memory.
        """
        with open(self.input_file, 'r') as file:
            self.lines = [line.strip() for line in file.readlines() if line.strip()]

    def __process_line(self, line, is_data=False):
        if is_data:
            dline = line.split('%')[0].strip().split(',')
            label = dline[-1]
            feature_data = dline[:-1]
            return {'features': feature_data, 'categories': label}
            
        if line.startswith("@ATTRIBUTE"):
            if line.startswith("@ATTRIBUTE class"):
                # Parse attribute information after "@ATTRIBUTE class"
                hierarchy_data = line.split(maxsplit=2)[2]
                labels = hierarchy_data.strip().split(",")
                labels[0] = labels[0].split(' ')[1]
                return {'labels': labels}
                # Process only @ATTRIBUTE lines for potential issues
            else:
                _, f_name, f_type = line.split()

            return (f_name, f_type)
        elif line.startswith("@DATA"):
            # Parse attribute information after "@ATTRIBUTE class"
            data = line.split(maxsplit=2)
            return {'data': data}


    def preprocess(self):
        """
        Temporarily preprocesses the .arff file to fix issues with attribute format and duplicate attribute names.

        :param arff_file_path: Path to the .arff file
        :return: Path to the temporary .arff file
        """

        is_data = False
        for line in self.lines:
            line = self.__process_line(line, is_data=is_data)
            if type(line) is tuple:
                f_name, f_type = line
                if f_name != ' ' and f_name != None:
                    self.atributes_names['name'].append(f_name)
                    self.atributes_names['type'].append(f_type)
            elif type(line) == dict:
                if 'data' in line.keys():
                    is_data = True
                elif 'labels' in line.keys():
                    self.labels = line
                else:
                    self.processed_lines.append(line)

    def transform_to_csv(self):
        df = pd.DataFrame(self.processed_lines)
        df.features = df.features.apply(lambda List: [None if x == '?' else x for x in List])
        
        # Parse to HMC format
        df.categories = df.categories.apply(lambda x: x.replace('/', '.'))

        def __process_feature(feature, idx):
            if self.atributes_names['type'][idx] == 'numeric' or self.atributes_names['type'][idx] == 'NUMERIC':
                if feature != '?' and feature is not None:
                    return float(feature)
                else:
                    return None
            else:
                cats = self.atributes_names['type'][idx][1:-1].split(',')
                cats_bin = {key: keras.utils.to_categorical(i, len(cats)).tolist() for i, key in enumerate(cats)}
                return cats_bin.get(feature, [0.0] * len(cats))

        # Features (X)
        def process_features(features):
            """
            Convert features from string to a numerical array.
            """
            return [__process_feature(f, i) for i, f in enumerate(features)]


        print(f"processing features {self.output_file}")
        df['features'] = df['features'].progress_apply(process_features)

        # Save dataframe to CSV
        df.to_csv(self.output_file, index=False)

        # Check if the file already exists
        if not os.path.exists(self.output_labels_file):
            with open(self.output_labels_file, 'w') as fp:
                json.dump(self.labels, fp)
        else:
            print(f"The file '{self.output_labels_file}' already exists and will not be overwritten.")
        
        # Check if the file already exists
        if not os.path.exists(self.output_atributes_file):
            with open(self.output_atributes_file, 'w') as fp:
                json.dump(self.atributes_names, fp)
        else:
            print(f"The file '{self.output_atributes_file}' already exists and will not be overwritten.")

    def process(self):
        """
        Full process: load data, parse attributes, and transform to CSV format.
        """
        
        self.load_data()
        self.preprocess()
        print(f"call transform to csv {self.output_file}")
        self.transform_to_csv()

