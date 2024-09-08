import os
import random
import re
import time

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
    # Remove any non-alphabetic characters except sentence-ending punctuation
    text = re.sub(r'[^A-Za-z\s.!?]', ' ', text)  # Retain sentence-ending punctuation
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    return text

# Function to build a sentence-based Markov Chain model
def build_sentence_markov_chain(text, order=3):
    sentences = re.split(r'(?<=[.!?])\s+', text)  # Split text into sentences
    markov_chain = {}
    for sentence in sentences:
        words = sentence.split()
        for i in range(len(words) - order):
            key = tuple(words[i:i + order])
            next_word = words[i + order]
            if key not in markov_chain:
                markov_chain[key] = []
            markov_chain[key].append(next_word)
    return markov_chain

# Function to fix capitalization of sentences and standalone 'i'
def fix_capitalization(text):
    # Capitalize the first word of each sentence
    sentences = re.split(r'([.!?]\s+)', text)
    sentences = [sentences[i].capitalize() if i % 2 == 0 else sentences[i] for i in range(len(sentences))]
    fixed_text = ''.join(sentences)

    # Replace all occurrences of standalone "i" with "I"
    fixed_text = re.sub(r'\bi\b', 'I', fixed_text)
    
    return fixed_text

# Function to generate a new book based on the Markov Chain model
def generate_text(chain, seed, length=5000):
    random.seed(seed)
    
    # Ensure that there are valid keys to start with
    valid_keys = list(chain.keys())
    
    if not valid_keys:
        print("Error: No valid starting keys found in the Markov chain.")
        return ''
    
    # Start with a random key and generate based on the Markov chain
    start = random.choice(valid_keys)
    generated_words = list(start)
    
    for _ in range(length - len(start)):
        state = tuple(generated_words[-len(start):])
        next_word_options = chain.get(state)
        if not next_word_options:
            # If no next word is found, randomly restart with another key
            start = random.choice(valid_keys)
            generated_words.extend(list(start))
        else:
            next_word = random.choice(next_word_options)
            generated_words.append(next_word)

    raw_text = ' '.join(generated_words)
    return fix_capitalization(raw_text)

# Function to save generated book
def save_book(text, folder, title):
    # Create a safe title for the filename
    safe_title = "".join(c if c.isalnum() or c in (' ', '_', '-') else "_" for c in title)
    file_path = os.path.join(folder, f"{safe_title}.txt")
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text)

# Main program
def main():
    # Step 1: Load text files from a folder
    folder_path = input("Enter the path to the folder with text files: ")
    loaded_text = load_texts(folder_path)
    
    # Step 2: Clean and tokenize the loaded text
    clean_loaded_text = clean_text(loaded_text)
    
    # Step 3: Build the Markov Chain model
    markov_chain = build_sentence_markov_chain(clean_loaded_text, order=3)
    
    # Step 4: Ask for the number of books to generate, their length, and the initial random seed
    n_books = int(input("Enter the number of books to generate: "))
    book_length = int(input("Enter the length of each generated book (in words): "))
    base_seed = int(input("Enter a base random seed: "))
    
    # Step 5: Create a timestamped folder for the new books
    output_folder = time.strftime("%Y%m%d_%H%M%S_generated_books")
    os.makedirs(output_folder, exist_ok=True)

    # Step 6: Generate new books with different seeds per book
    for i in range(n_books):
        current_seed = base_seed + i  # Unique seed for each book
        book_title = f"Generated_Book_{i+1}_Seed_{current_seed}"
        generated_text = generate_text(markov_chain, current_seed, length=book_length)
        
        if generated_text:
            save_book(generated_text, output_folder, book_title)
            print(f"Generated: {book_title}.txt with seed {current_seed}")
        else:
            print(f"Failed to generate text for {book_title}.txt")
    
    print(f"All generated books saved in folder: {output_folder}")

if __name__ == "__main__":
    main()
