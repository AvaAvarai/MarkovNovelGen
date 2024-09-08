import os
import random
import re
import time
import plotly.express as px
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

# Function to convert words to numerical representation for parallel coordinates
def word_to_num_mapping(chain):
    word_list = list(set([word for state in chain.keys() for word in state] + [word for words in chain.values() for word in words]))
    word_map = {word: i for i, word in enumerate(word_list)}
    return word_map

# Function to visualize the Markov model using plotly parallel coordinates
def visualize_parallel_coordinates(chain):
    word_map = word_to_num_mapping(chain)
    
    # Prepare data for parallel coordinates
    num_axes = max([len(state) for state in chain.keys()]) + 1  # number of axes (order of chain + 1)
    data = []
    
    for state, next_words in chain.items():
        for next_word in next_words:
            # Build a row for each transition
            row = [word_map[word] for word in state] + [word_map[next_word]]
            data.append(row)
    
    data = np.array(data)
    
    # Get words corresponding to each number
    words = [word for word, idx in sorted(word_map.items(), key=lambda x: x[1])]

    # Prepare data for Plotly parallel coordinates plot
    dimensions = []
    for i in range(data.shape[1]):
        dim = dict(range=[0, len(word_map) - 1],
                   tickvals=list(range(len(word_map))),
                   ticktext=words,
                   label=f"Word {i+1}",
                   values=data[:, i])
        dimensions.append(dim)

    # Create parallel coordinates plot
    fig = px.parallel_coordinates(dimensions=dimensions)
    
    fig.update_layout(title="Markov Chain - Parallel Coordinates Visualization of Word Transitions",
                      height=600)
    
    fig.show()

# Main program
def main():
    folder_path = input("Enter the path to the folder with text files: ")
    loaded_text = load_texts(folder_path)
    
    clean_loaded_text = clean_text(loaded_text)
    markov_chain = build_sentence_markov_chain(clean_loaded_text, order=3)
    
    # Visualize the Markov model using plotly parallel coordinates
    visualize_parallel_coordinates(markov_chain)

if __name__ == "__main__":
    main()
