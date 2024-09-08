import os
import random
import re
import time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
from scipy.sparse import lil_matrix

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
def build_sentence_markov_chain(text, order=3):
    sentences = re.split(r'(?<=[.!?])\s+', text)  # Split text into sentences
    markov_chain = defaultdict(list)
    for sentence in sentences:
        words = sentence.split()
        for i in range(len(words) - order):
            key = tuple(words[i:i + order])
            next_word = words[i + order]
            markov_chain[key].append(next_word)
    return markov_chain

# Function to calculate transition matrix in pieces
def build_transition_matrix(chain, vocab_size=1000, resolution=10):
    # Get the top `vocab_size` most common words
    all_words = [word for state in chain.keys() for word in state] + [word for words in chain.values() for word in words]
    common_words = [word for word, count in Counter(all_words).most_common(vocab_size)]
    
    word_index = {word: i for i, word in enumerate(common_words)}
    
    # Initialize transition matrix with lower resolution
    matrix_size = len(common_words) // resolution
    transition_matrix = np.zeros((matrix_size, matrix_size))

    for state, next_words in chain.items():
        if all(word in word_index for word in state):  # Ensure all words in the state are in the vocabulary
            state_index = [word_index[word] for word in state]
            for next_word in next_words:
                if next_word in word_index:
                    next_word_index = word_index[next_word]
                    # Downscale the index based on resolution
                    scaled_state_idx = state_index[-1] // resolution
                    scaled_next_idx = next_word_index // resolution
                    transition_matrix[scaled_state_idx, scaled_next_idx] += 1  # Count transitions

    # Normalize rows to represent probabilities
    row_sums = transition_matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # Avoid division by zero
    transition_matrix = transition_matrix / row_sums  # Element-wise division
    
    return transition_matrix, common_words

# Function to generate a heatmap of the transition matrix
def generate_heatmap(transition_matrix, folder_name, resolution):
    plt.figure(figsize=(12, 10))
    sns.heatmap(transition_matrix, cmap="Blues", cbar=True)
    plt.title(f'Markov Chain Transition Matrix Heatmap (Resolution: {resolution})')
    plt.xlabel('Next Word Index (Scaled)')
    plt.ylabel('Current Word Index (Scaled)')
    
    # Save heatmap as PNG
    heatmap_path = os.path.join(folder_name, f'markov_chain_heatmap_res_{resolution}.png')
    plt.savefig(heatmap_path)
    plt.close()
    print(f"Heatmap saved as {heatmap_path}")

# Function to fix capitalization of sentences and standalone 'i'
def fix_capitalization(text):
    sentences = re.split(r'([.!?]\s+)', text)
    sentences = [sentences[i].capitalize() if i % 2 == 0 else sentences[i] for i in range(len(sentences))]
    fixed_text = ''.join(sentences)
    fixed_text = re.sub(r'\bi\b', 'I', fixed_text)
    return fixed_text

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
            start = random.choice(valid_keys)
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
    
    # Create a timestamped folder for the new books and heatmap
    output_folder = time.strftime("%Y%m%d_%H%M%S_generated_books")
    os.makedirs(output_folder, exist_ok=True)
    
    # Generate and save heatmap with lower resolution
    vocab_size = int(input("Enter vocabulary size for the heatmap: "))
    resolution = int(input("Enter resolution scale (higher values reduce resolution): "))
    transition_matrix, _ = build_transition_matrix(markov_chain, vocab_size=vocab_size, resolution=resolution)
    generate_heatmap(transition_matrix, output_folder, resolution)
    
    # Generate books
    n_books = int(input("Enter the number of books to generate: "))
    book_length = int(input("Enter the length of each generated book (in words): "))
    base_seed = int(input("Enter a base random seed: "))
    
    for i in range(n_books):
        current_seed = base_seed + i
        book_title = f"Generated_Book_{i+1}_Seed_{current_seed}"
        generated_text = generate_text(markov_chain, current_seed, length=book_length)
        
        if generated_text:
            save_book(generated_text, output_folder, book_title)
            print(f"Generated: {book_title}.txt with seed {current_seed}")
        else:
            print(f"Failed to generate text for {book_title}.txt")
    
    print(f"All generated books and heatmap saved in folder: {output_folder}")

if __name__ == "__main__":
    main()
