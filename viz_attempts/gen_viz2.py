import os
import random
import re
import time
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# Function to load text files from a folder
def load_texts(folder_path):
    text = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            with open(os.path.join(folder_path, file_name), 'r', encoding='utf-8') as file:
                text.append(file.read())
    return " ".join(text)

# Precompile regex patterns for faster execution
non_alpha = re.compile(r'[^A-Za-z\s.!?]')
multi_space = re.compile(r'\s+')

# Function to clean and tokenize text
def clean_text(text):
    text = non_alpha.sub(' ', text)  # Remove any non-alphabetic characters except sentence-ending punctuation
    return multi_space.sub(' ', text).strip()  # Replace multiple spaces with a single space

# Function to build a sentence-based Markov Chain model
def build_sentence_markov_chain(text, order=3):
    sentences = re.split(r'(?<=[.!?])\s+', text)  # Split text into sentences
    markov_chain = defaultdict(list)  # Use defaultdict for efficiency
    for sentence in sentences:
        words = sentence.split()
        for i in range(len(words) - order):
            key = tuple(words[i:i + order])
            next_word = words[i + order]
            markov_chain[key].append(next_word)
    return markov_chain

# Function to prepare data for parallel coordinates visualization
def prepare_parallel_coordinates_data(chain, limit=50):
    keys = list(chain.keys())[:limit]
    
    data = []
    for key in keys:
        if chain[key]:  # Ensure the state has transitions
            for next_word in chain[key]:
                row = list(key) + [next_word]
                data.append(row)
    
    return data

# Function to visualize the Markov model as parallel coordinates using Matplotlib
def visualize_parallel_coordinates(data):
    # Convert word data into numerical form for visualization
    all_words = set(word for row in data for word in row)
    word_to_num = {word: i for i, word in enumerate(all_words)}
    
    num_data = [[word_to_num[word] for word in row] for row in data]
    num_data = np.array(num_data)
    
    # Plot parallel coordinates
    plt.figure(figsize=(10, 6))
    for i in range(len(num_data)):
        plt.plot(range(len(num_data[i])), num_data[i], marker='o', color='b', alpha=0.5)
    
    # Set axis labels as the word positions
    plt.xticks(range(len(data[0])), [f'Word {i+1}' for i in range(len(data[0]))])
    
    # Label words on the axes
    for i in range(len(data[0])):
        unique_values = np.unique(num_data[:, i])
        word_labels = [list(word_to_num.keys())[list(word_to_num.values()).index(val)] for val in unique_values]
        plt.yticks(unique_values, word_labels)
    
    plt.title('Markov Chain Visualization (Parallel Coordinates)')
    plt.show()

# Function to fix capitalization of sentences and standalone 'i'
def fix_capitalization(text):
    sentences = re.split(r'([.!?]\s+)', text)
    sentences = [sentences[i].capitalize() if i % 2 == 0 else sentences[i] for i in range(len(sentences))]
    fixed_text = ''.join(sentences)
    return re.sub(r'\bi\b', 'I', fixed_text)  # Fix standalone 'i'

# Function to generate a new book based on the Markov Chain model
def generate_text(chain, seed, length=5000):
    random.seed(seed)
    
    valid_keys = list(chain.keys())
    if not valid_keys:
        print("Error: No valid starting keys found in the Markov chain.")
        return ''
    
    start = random.choice(valid_keys)
    generated_words = list(start)
    
    for _ in range(length - len(start)):
        state = tuple(generated_words[-len(start):])
        next_word_options = chain.get(state)
        if not next_word_options:
            start = random.choice(valid_keys)  # Restart with another key if no next word
            generated_words.extend(list(start))
        else:
            next_word = random.choice(next_word_options)
            generated_words.append(next_word)

    raw_text = ' '.join(generated_words)
    return fix_capitalization(raw_text)

# Function to save generated book
def save_book(text, folder, title):
    safe_title = "".join(c if c.isalnum() or c in (' ', '_', '-') else "_" for c in title)
    file_path = os.path.join(folder, f"{safe_title}.txt")
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text)

# Main program
def main():
    folder_path = input("Enter the path to the folder with text files: ")
    loaded_text = load_texts(folder_path)
    
    clean_loaded_text = clean_text(loaded_text)
    markov_chain = build_sentence_markov_chain(clean_loaded_text, order=3)
    
    # Prepare data for parallel coordinates
    parallel_data = prepare_parallel_coordinates_data(markov_chain, limit=50)
    
    # Visualize the Markov model using parallel coordinates
    visualize_parallel_coordinates(parallel_data)
    
    n_books = int(input("Enter the number of books to generate: "))
    book_length = int(input("Enter the length of each generated book (in words): "))
    base_seed = int(input("Enter a base random seed: "))
    
    output_folder = time.strftime("%Y%m%d_%H%M%S_generated_books")
    os.makedirs(output_folder, exist_ok=True)

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
