import os
from ast import parse

import pandas as pd
import arff  # from liac-arff
import zipfile
from scipy.io import arff as scipyarff
import re

from gofun_parser import GoFunCSVParser

from collections import defaultdict

def extract_all_zips(input_dir, output_dir):
    """
    Extracts all .zip files from the input directory into separate folders in the output directory.

    :param input_dir: Directory containing the .zip files
    :param output_dir: Directory to save the extracted files
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Iterate through all files in the input directory
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.zip'):
            zip_path = os.path.join(input_dir, file_name)
            extract_folder = os.path.join(output_dir, os.path.splitext(file_name)[0])

            # Create a separate folder for each .zip file
            os.makedirs(extract_folder, exist_ok=True)

            # Extract the .zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)

            print(f"Extracted {file_name} to {extract_folder}")


def extract_specific_zips(input_path, output_dir):
    """
    Recursively extracts 'train.zip', 'test.zip', and 'val.zip' from subdirectories of the input path.

    :param input_path: Root directory containing subdirectories with .zip files
    :param output_dir: Directory to save the extracted files
    """
    os.makedirs(output_dir, exist_ok=True)

    for root, dirs, files in os.walk(input_path):
        for file_name in files:
            if file_name.endswith('.zip'):
                zip_path = os.path.join(root, file_name)

                extract_folder = os.path.join(output_dir, os.path.relpath(root, input_path),
                                              os.path.splitext(file_name)[0])
                os.makedirs(extract_folder, exist_ok=True)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_folder)

                print(f"Extracted {file_name} from {root} to {extract_folder}")



def arff_to_csv_scipy(arff_file_path, csv_file_path):
    """
    Converts an .arff file to .csv format using scipy.io.arff.

    :param arff_file_path: Path to the .arff file
    :param csv_file_path: Path to save the .csv file
    """
    data, meta = scipyarff.loadarff(arff_file_path)
    df = pd.DataFrame(data)
    df.to_csv(csv_file_path, index=False)
    print(f"Converted {arff_file_path} to {csv_file_path}")

def arff_to_csv_liac(arff_file_path, csv_file_path):
    """
    Converts an .arff file to .csv format using liac-arff.

    :param arff_file_path: Path to the .arff file
    :param csv_file_path: Path to save the .csv file
    """
    # Load the .arff file using liac-arff
    with open(arff_file_path, 'r') as f:
        data = arff.load(f)
    print(data)

    # Convert to pandas DataFrame
    #df = pd.DataFrame(data['data'], columns=[attr[0] for attr in data['attributes']])

    # Save as .csv
    #df.to_csv(csv_file_path, index=False)
    #print(f"Converted {arff_file_path} to {csv_file_path}")


def convert_arffs_to_csvs(output_dir):
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.arff'):
                arff_file_path = os.path.join(root, file)
                csv_file_path = os.path.splitext(arff_file_path)[0] + '.csv'
                arff_to_csv_liac(arff_file_path, csv_file_path)
                #arff_to_csv_scipy(arff_file_path, csv_file_path)


def __process_line(line):
    if line.startswith("@ATTRIBUTE class"):
        # Parse attribute information after "@ATTRIBUTE class"
        hierarchy_data = line.split(maxsplit=2)[2]
        labels = hierarchy_data.strip().split(",")
        return {'labels': labels}
        # Process only @ATTRIBUTE lines for potential issues
    elif line.startswith("@ATTRIBUTE"):
        parts = line.split(maxsplit=2)  # Split only the first two parts
        if len(parts) < 3:
            print(f"Warning: Skipping malformed attribute line: {line.strip()}")

        attribute_name = parts[1]
        attribute_type = parts[2].strip()

        # Replace special characters in attribute names with underscores
        attribute_name = re.sub(r'[^a-zA-Z0-9_]', '_', attribute_name)


        # Fix attribute types if they contain complex or unsupported types
        if "=" in attribute_type or ("{" in attribute_type and "}" in attribute_type):
            attribute_type = "string"  # Replace complex types with "string"

        return {attribute_name: attribute_type}


def preprocess_arff_file(arff_file_path):
    """
    Temporarily preprocesses the .arff file to fix issues with attribute format and duplicate attribute names.

    :param arff_file_path: Path to the .arff file
    :return: Path to the temporary .arff file
    """
    with open(arff_file_path, 'r') as file:
        lines = file.readlines()

    processed_lines = []
    attribute_names = defaultdict(int)

    for line in lines:

        line = __process_line(line)
        processed_lines.append(line)

    # Write the modified lines to a temporary file
    #temp_file_path = arff_file_path + ".temp"
    #with open(temp_file_path, 'w') as file:
    #    file.writelines(processed_lines)

    return processed_lines

# Example usage
input_dir = r'C:\Users\bruno\storage\GO'  # Directory containing the .zip files
extracted_dir = r'C:\Users\bruno\storage\GO_extraced'  # Directory to save the extracted files


if __name__ == "__main__":
    input_dir = extracted_dir

    output_dir = r'C:\Users\bruno\storage\GO_csv'
    arff_file_path = r'C:\Users\bruno\storage\GO_extraced\expr_GO\datasets_GO\expr_GO\expr_GO.test.arff\expr_GO.test.arff'
    arff_file_path_parsed = r'C:\Users\bruno\storage\GO_extraced\expr_GO\datasets_GO\expr_GO\expr_GO.test.arff\expr_GO.test.csv'

    #parser = GoFunCSVParser(arff_file_path, arff_file_path_parsed)
    #parser.process()

    extract_all_zips(input_dir, output_dir)
    #extract_specific_zips(extracted_dir, extracted_dir)
    # Step 2: Convert .arff files to .csv

    preprocess_arff_file(arff_file_path)

    #with open(arff_file_path+'.temp', 'r') as f:
    #    data = arff.load(f)
    #print(data)
    #arff_to_csv_liac(arff_file_path)
    #convert_arffs_to_csvs(extracted_dir)