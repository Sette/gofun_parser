import csv


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
        self.attributes = []
        self.data = []

    def load_data(self):
        """
        Load the data from the input file into memory.
        """
        with open(self.input_file, 'r') as file:
            self.data = file.readlines()

    def parse_attributes(self):
        """
        Parse the attribute line to extract class hierarchy information.

        Returns:
            list: Parsed hierarchy structure as a list.
        """
        for line in self.data:
            if line.startswith("@ATTRIBUTE class"):
                hierarchy_data = line.split()[2:]  # Adjust based on the file format
                self.attributes = hierarchy_data[0].split(",")
                break

    def transform_to_csv_format(self):
        """
        Transform hierarchical data to CSV format and save it to the output file.
        """
        csv_data = []
        csv_data.append(self.attributes)  # Add attributes as headers
        # Example transformation: Adjust this based on your specific needs
        for line in self.data:
            if not line.startswith("@"):
                # Process each line to extract values based on hierarchy
                csv_row = line.strip().split()  # Adjust based on file format
                csv_data.append(csv_row)

        # Save the transformed data to CSV
        with open(self.output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csv_data)

    def process(self):
        """
        Full process: load data, parse attributes, and transform to CSV format.
        """
        self.load_data()
        attributes = self.parse_attributes()
        self.transform_to_csv_format()
        print(f"Data successfully converted and saved to {self.output_file}")
