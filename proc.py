import os
import re
import csv

# Function to preprocess text files by extracting titles, authors, and removing disclaimers
def preprocess_text(input_folder, output_folder, csv_file_path):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['filename', 'work title', 'author name'])  # Write CSV headers

        for file_name in os.listdir(input_folder):
            input_file_path = os.path.join(input_folder, file_name)
            output_file_path = os.path.join(output_folder, file_name)
            
            with open(input_file_path, 'r', encoding='utf-8') as file:
                text = file.read()

            # Extract the title and author
            title, author = extract_title_and_author(text)
            
            # Write to CSV file
            writer.writerow([file_name, title, author])
            
            # Remove disclaimers (headers and footers) from the text
            processed_text = remove_disclaimers(text)

            # Save the processed text to the new file
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(processed_text)

# Function to extract title and author from text
def extract_title_and_author(text):
    # Basic regex to find title and author near the beginning of the text
    title_match = re.search(r'(title:\s*)([^\n]+)', text, re.IGNORECASE)
    author_match = re.search(r'(author:\s*)([^\n]+)', text, re.IGNORECASE)
    
    title = title_match.group(2).strip() if title_match else "Unknown Title"
    author = author_match.group(2).strip() if author_match else "Unknown Author"
    
    return title, author

# Function to remove Gutenberg disclaimers from the text
def remove_disclaimers(text):
    header_pattern = r"\*\*\* START OF THIS PROJECT GUTENBERG EBOOK.*?\*\*\*"
    footer_pattern = r"\*\*\* END OF THIS PROJECT GUTENBERG EBOOK.*?\*\*\*"
    blurb_pattern = r"This ebook is for the use of anyone anywhere.*?before using this eBook\."
    
    text = re.sub(header_pattern, "", text, flags=re.DOTALL)
    text = re.sub(footer_pattern, "", text, flags=re.DOTALL)
    text = re.sub(blurb_pattern, "", text, flags=re.DOTALL)
    
    return text.strip()

if __name__ == "__main__":
    input_folder = 'train_raw'  # Folder containing raw text files
    output_folder = 'train'  # Folder for processed text
    csv_file_path = 'extracted_titles_and_authors.csv'  # CSV to store filenames, titles, and authors

    preprocess_text(input_folder, output_folder, csv_file_path)
