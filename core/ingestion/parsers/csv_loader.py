import csv
import os

class CSVLoader:
    def load_dtcs(self, path):
        """Returns dict {code: description}"""
        data = {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        # Format: B0001,Driver Frontal Stage 1...
                        code = row[0].strip()
                        desc = row[1].strip()
                        data[code] = desc
        except Exception as e:
            print(f"Error loading DTCs: {e}")
        return data

    def load_nrcs(self, path):
        """Returns dict {code_hex: description}"""
        data = {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        # Format: 10,General Reject
                        code = row[0].strip()
                        desc = row[1].strip()
                        data[code] = desc
        except Exception as e:
            print(f"Error loading NRCs: {e}")
        return data

    def load_fault_types(self, path):
        """Returns dict {type_hex: description}"""
        data = {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        # Format: 01,General Electrical Failure
                        code = row[0].strip()
                        desc = row[1].strip()
                        data[code] = desc
        except Exception as e:
            print(f"Error loading Fault Types: {e}")
        return data
