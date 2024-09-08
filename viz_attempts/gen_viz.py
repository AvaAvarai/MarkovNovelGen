import os
import random
import re
import time
import networkx as nx
import matplotlib.pyplot as plt
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

# Function to visualize the Markov model as a graph
def visualize_markov_chain(chain, limit=50):
    G = nx.DiGraph()

    # Add edges to the graph with limited transitions for faster visualization
    for state, next_words in list(chain.items())[:limit]:
        for next_word in next_words:
            next_state = state[1:] + (next_word,)
            G.add_edge(state, next_state)

    # Draw the graph
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G, k=0.5, iterations=20)  # Reduced iterations for speed
    nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue', font_size=8, font_weight='bold', edge_color='gray')
    plt.title('Markov Chain Visualization')
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
    
    # Visualize a limited portion of the Markov model for speed
    visualize_markov_chain(markov_chain, limit=50)
    
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
