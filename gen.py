import os
import random
import re
import time
import csv

# Function to load text files from a folder
def load_texts(folder_path):
    text = ""
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            with open(os.path.join(folder_path, file_name), 'r', encoding='utf-8') as file:
                text += file.read() + " "
    return text

# Function to clean and tokenize text (preserving sentence structure)
def clean_text(text):
    text = re.sub(r'[^A-Za-z\s.!?]', ' ', text)  # Retain sentence-ending punctuation
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    return text

# Function to build a sentence-based Markov Chain model
def build_markov_chain(text, order=2):
    words = text.split()
    markov_chain = {}
    for i in range(len(words) - order):
        key = tuple(words[i:i + order])
        next_word = words[i + order]
        if key not in markov_chain:
            markov_chain[key] = []
        markov_chain[key].append(next_word)
    return markov_chain

# Function to load titles and authors from CSV file
def load_titles_and_authors(csv_file):
    titles = []
    authors = []
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            title, author = row[1], row[2]
            if title != "Unknown Title" and author != "Unknown Author":
                titles.append(title)
                authors.append(author)
    return ' '.join(titles), ' '.join(authors)

# Function to generate text based on Markov Chain model
def generate_from_chain(chain, seed, length=5):
    random.seed(seed)
    valid_keys = list(chain.keys())
    
    if not valid_keys:
        return ''
    
    start = random.choice(valid_keys)
    generated_words = list(start)
    
    for _ in range(length - len(start)):
        state = tuple(generated_words[-len(start):])
        next_word_options = chain.get(state)
        if not next_word_options:
            start = random.choice(valid_keys)
            generated_words.extend(list(start))
        else:
            next_word = random.choice(next_word_options)
            generated_words.append(next_word)

    return ' '.join(generated_words)

# Function to save generated book with title and author
def save_book(text, folder, title, author):
    safe_title = "".join(c if c.isalnum() or c in (' ', '_', '-') else "_" for c in title)
    file_path = os.path.join(folder, f"{safe_title}.txt")
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"Title: {title}\n")
        file.write(f"Author: {author}\n\n")
        file.write(text)

# Main program
def main():
    # Step 1: Load the CSV containing titles and authors
    csv_file = 'extracted_titles_and_authors.csv'
    titles_text, authors_text = load_titles_and_authors(csv_file)
    
    # Step 2: Build Markov Chains for titles and authors
    title_chain = build_markov_chain(titles_text, order=2)
    author_chain = build_markov_chain(authors_text, order=2)
    
    # Step 3: Load text files from a folder and clean the text
    folder_path = input("Enter the path to the folder with text files: ")
    loaded_text = load_texts(folder_path)
    clean_loaded_text = clean_text(loaded_text)
    
    # Step 4: Build the Markov Chain model for the content
    markov_chain = build_markov_chain(clean_loaded_text, order=3)
    
    # Step 5: Ask for the number of books to generate, their length, and the initial random seed
    n_books = int(input("Enter the number of books to generate: "))
    book_length = int(input("Enter the length of each generated book (in words): "))
    base_seed = int(input("Enter a base random seed: "))
    
    # Step 6: Create a timestamped folder for the new books
    output_folder = time.strftime("%Y%m%d_%H%M%S_generated_books")
    os.makedirs(output_folder, exist_ok=True)

    # Step 7: Generate new books with different seeds per book
    for i in range(n_books):
        current_seed = base_seed + i  # Unique seed for each book
        
        # Generate the title and author using the Markov Chains
        book_title = generate_from_chain(title_chain, current_seed, length=5)
        author = generate_from_chain(author_chain, current_seed, length=2)
        
        # Generate the text for the book
        generated_text = generate_from_chain(markov_chain, current_seed, length=book_length)
        
        if generated_text:
            save_book(generated_text, output_folder, book_title, author)
            print(f"Generated: {book_title} by {author} (Seed: {current_seed})")
        else:
            print(f"Failed to generate text for {book_title}")

    print(f"All generated books saved in folder: {output_folder}")

if __name__ == "__main__":
    main()
