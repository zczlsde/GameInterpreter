# The Aim of this script is to extract the code blocks from the .txt files and run them to generate the .efg files.

import os
import re
import subprocess

def extract_and_run_code(file_path, output_root):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match all code blocks for case 1 and case 2
    code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)

    # Check if Error in code generation is in content
    if 'Error in code generation. Trying again...' in content:
        error_split_blocks = re.split(r'Error in code generation\. Trying again\.\.\.', content)
        target_code_block = error_split_blocks[-1].strip()
    elif 'Error in code generation. Trying again...' not in content and len(code_blocks) > 1:
        target_code_block = code_blocks[1].strip()
    elif code_blocks:
        target_code_block = code_blocks[0].strip()
    else:
        return False

    # Check if `print(efg)` is in the code block, if not, add it
    if 'print(efg)' not in target_code_block:
        target_code_block += '\nef = g.write(format=\'native\')\nprint(efg)'

    # Generate the output path with the adjusted structure
    relative_path = os.path.relpath(file_path, start=input_folder_path)
    output_file_dir = os.path.join(output_root, os.path.dirname(relative_path))
    os.makedirs(output_file_dir, exist_ok=True)

    output_file_name = os.path.splitext(os.path.basename(file_path))[0] + '.efg'
    output_file_path = os.path.join(output_file_dir, output_file_name)

    try:
        process = subprocess.run(
            ['python', '-c', target_code_block],
            text=True,
            capture_output=True
        )
        
        # Write the output to the .efg file
        with open(output_file_path, 'w', encoding='utf-8') as ef:
            ef.write(process.stdout if process.returncode == 0 else '')

    except Exception as e:
        # If any error occurs, write an empty file
        with open(output_file_path, 'w', encoding='utf-8') as ef:
            ef.write('')

    return True

def process_txt_files(input_root, output_root):
    for subdir, _, files in os.walk(input_root):
        relative_subdir = os.path.relpath(subdir, input_root)
        adjusted_subdir = os.path.join(output_root, relative_subdir)
        os.makedirs(adjusted_subdir, exist_ok=True)

        # If no .txt files, create a .gitkeep file
        txt_files = [file for file in files if file.endswith('.txt')]
        if not txt_files:
            gitkeep_path = os.path.join(adjusted_subdir, ".gitkeep")
            if not os.path.exists(gitkeep_path):
                with open(gitkeep_path, 'w', encoding='utf-8') as gitkeep:
                    gitkeep.write('')

        for file in txt_files:
            file_path = os.path.join(subdir, file)
            extract_and_run_code(file_path, output_root)

# Specify the folder containing the .txt files and the output folder
input_folder_path = ""
output_folder_path = ""
process_txt_files(input_folder_path, output_folder_path)