# %% combine_python_files.py
import os
import argparse

def combine_python_files(input_dir, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    outfile.write(f'# File: {file_path}\n')
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                        outfile.write('\n\n')

if __name__ == "__main__":
    input_dir = 'src/rental'
    output_file = 'combined_rental_files.py'
    combine_python_files(input_dir, output_file)