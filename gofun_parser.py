import csv
import re
from collections import defaultdict
from tqdm.notebook import tqdm
import pandas as pd

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
        self.atributes_names = []
        self.processed_lines = []
        self.data = []

    def load_data(self):
        """
        Load the data from the input file into memory.
        """
        with open(self.input_file, 'r') as file:
            self.data = file.readlines()

    def __process_line(self, line, is_data=False):
        if is_data:
            feature_data = line.strip().split(",")
            return {'features': feature_data}
            
        if line.startswith("@ATTRIBUTE class"):
            # Parse attribute information after "@ATTRIBUTE class"
            hierarchy_data = line.split(maxsplit=2)[2]
            labels = hierarchy_data.strip().split(",")
            labels[0] = labels[0].split(' ')[1]
            return {'labels': labels}
            # Process only @ATTRIBUTE lines for potential issues
        elif line.startswith("@ATTRIBUTE"):
            parts = line.split(maxsplit=2)  # Split only the first two parts
            if len(parts) < 3:
                print(f"Warning: Skipping malformed attribute line: {line.strip()}")
    
            attribute_name = parts[1]
    
            # Replace special characters in attribute names with underscores
            #attribute_name = re.sub(r'[^a-zA-Z0-9_]', '_', attribute_name)
    
            return attribute_name
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
        with open(self.input_file, 'r') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]

        is_data = False
        for line in lines:
            line = self.__process_line(line, is_data=is_data)
            if line != ' ' and line != None:
                if type(line) != dict:
                    self.atributes_names.append(line)
                else:
                    if 'data' in line.keys():
                        is_data = True
                    else:
                        self.processed_lines.append(line)

    def transform_to_csv(self):
        temp_example = []
        separated_examples = []
        for line in self.processed_lines:
            if 'features' in line.keys():
                for feature in line['features']:
                    temp_example.append(feature)
                    # Verifique se é o final de um exemplo com base no padrão categórico
                    if "@" in feature:  # Ajuste esta condição conforme necessário para seu padrão
                        separated_examples.append(temp_example)
                        temp_example = []
        # Criar listas para armazenar os dados
        features = []
        categories = []

        # Separar features e categorias
        for example in separated_examples:
            local_features = []
            for feature in example[:-1]:
                try:
                    x = float(feature)
                except:
                    if feature == '?':
                        x = None
                    else:
                        x = feature
                local_features.append(x)
            features.append(local_features)  # Converter features para inteiros
            categories.append(example[-1])  # Manter categorias como strings

        # Criar o DataFrame
        df = pd.DataFrame(features, columns=self.atributes_names)
        df["Categories"] = categories  # Adicionar a coluna de categorias
        
        # Visualizar o DataFrame
        df.to_csv(self.output_file, index=False)

    def process(self):
        """
        Full process: load data, parse attributes, and transform to CSV format.
        """
        
        self.load_data()
        self.preprocess()
        self.transform_to_csv()
        print(f"Data successfully converted and saved to {self.output_file}")
