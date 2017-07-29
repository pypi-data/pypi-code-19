import random
import time
import numpy as np
import os, sys
import glob

def get_prefixes(counts):
    return list(counts.keys())

def get_next_word_weights(counts, prefix):
    d = counts.get(prefix, {})
    total = 0
    for k, v in d.items():
        total += v

    return [ [k, v/total] for k,v in d.items() ]



def get_word_list(input_dir, filter_function=lambda x:x):
    input_files = glob.glob(input_dir + '/*.txt')
    words = []
    word = ''
    for file_path in input_files:
        with open(file_path, 'r') as f:         
            for line in f:            
                clean_line = filter_function(line)
                for i in range(0, len(clean_line)):
                    if clean_line[i] not in [ ' ', '\n', '\t']:
                        word += clean_line[i]
                    elif word is not '':
                        words.append(word)
                        word = ''
    return words
    
def get_ngram_counts(words, n_depth=3):
    counts = {}
    n = n_depth -1
    for i in range(0, len(words) - n):          
        prefix = " ".join(words[i:i+n])  
        next_word = words[i+n]
        counts[prefix][next_word] = counts.setdefault(prefix, {}).setdefault(next_word, 0) +1
    return counts
                    
def generate_text(counts, min_words, end_characters=['.', '?', '!']):
    prefix = random.choice(get_prefixes(counts))

    while not prefix[0].isupper():
        prefix = random.choice(get_prefixes(counts))
    gen_text = [ prefix ]
    word_weights = get_next_word_weights(counts, prefix)
        
    while ((len(gen_text) < min_words) or gen_text[-1][-1] not in end_characters) and len(word_weights) is not 0:          
        choices = [ word[0] for word in word_weights ]     
        probs =  [ word[1] for word in word_weights ]
        next_word = np.random.choice(choices, 1, p=probs)[0] 
        gen_text.append(next_word)
        prefix = prefix.split(' ')[1] + ' ' + next_word      
        word_weights = get_next_word_weights(counts, prefix)
    return ' '.join(gen_text)

        











