import os
import re

def preprocess_text(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        input_file_path = os.path.join(input_folder, file_name)
        output_file_path = os.path.join(output_folder, file_name)

        with open(input_file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        # Remove Gutenberg headers and footers
        processed_text = remove_disclaimers(text)

        # Save the processed text to the new file
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(processed_text)

def remove_disclaimers(text):
    # Define patterns for Project Gutenberg headers and footers
    header_pattern = r"\*\*\* START OF THIS PROJECT GUTENBERG EBOOK.*?\*\*\*"
    footer_pattern = r"\*\*\* END OF THIS PROJECT GUTENBERG EBOOK.*?\*\*\*"
    
    # Define pattern for the specific blurb
    blurb_pattern = r"This ebook is for the use of anyone anywhere.*?before using this eBook\."

    # Remove header, footer, and specific blurb
    text = re.sub(header_pattern, "", text, flags=re.DOTALL)
    text = re.sub(footer_pattern, "", text, flags=re.DOTALL)
    text = re.sub(blurb_pattern, "", text, flags=re.DOTALL)
    
    return text.strip()

if __name__ == "__main__":
    input_folder = '25_open'
    output_folder = '25_open_clean'
    preprocess_text(input_folder, output_folder)
