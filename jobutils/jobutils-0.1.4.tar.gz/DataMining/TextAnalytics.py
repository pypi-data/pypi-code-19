import nltk
import numpy as np
import pandas as pd
import networkx as nx

from Utils import divide_nullable_values
from DataAccess.FileSystemIO import FileSystemIO
from Utils.TextFunctions import remove_non_alphabetical_characters_from_text, remove_stop_words

io = FileSystemIO()

adjacent_names = io.read_csv('Datasets/adjacent_names.csv')


def calculate_text_relative_intersection(text_set_a, text_set_b):
    """

    :param text_set_a:
    :param text_set_b:
    :return:
    """
    min_set_len = min(len(text_set_a), len(text_set_b))

    try:
        return divide_nullable_values(len(text_set_a.intersection(text_set_b)), min_set_len)
    except:
        return 0


def calculate_text_intersection(text_a, text_b):
    """

    :param text_a:
    :param text_b:
    :return:
    """
    tokens_a = set(text_a.split())
    tokens_b = set(text_b.split())

    text_min_len = min(len(tokens_a), len(tokens_b))

    intersection = tokens_a.intersection(tokens_b)

    if len(intersection) == text_min_len:
        return 1

    return len(intersection) / (1.0 * text_min_len)


def calculate_names_intersection(names_a, names_b):
    """

    :param names_a:
    :param names_b:
    :return:
    """
    min_names_len = min(len(names_a), len(names_b))
    max_names_len = max(len(names_a), len(names_b))

    if min_names_len == max_names_len and min_names_len == 0:
        return np.inf

    return calculate_text_relative_intersection(set(names_a), set(names_b))


def extract_pos_tags(text):
    """

    :param text:
    :return:
    """
    tokens = nltk.word_tokenize(text)
    return nltk.pos_tag(tokens)


def initialize_key_graph():
    """

    :return:
    """
    graph_definition = io.read_json('KeyboardGraphDefinition.json')
    graph = nx.Graph()

    for source_node in graph_definition.keys():
        for target_node in graph_definition[source_node]:
            graph.add_edge(source_node, target_node)

    return graph


def calculate_term_path(term, graph, path = []):
    """

    :param path:
    :param term:
    :param graph:
    :return:
    """
    for ix in range(0, len(term) - 1):

        p = nx.shortest_path(graph, source=term[ix], target=term[ix + 1])
        path.extend(p[:-1])

    path.extend(p[-1])

    return path

def calculate_text_metrics(text, graph):
    """

    :param text:
    :param graph:
    :return:
    """
    text = remove_non_alphabetical_characters_from_text(text)
    term_metrics = []

    for term in text.split():


        term = term.lower().strip()
        if len(term) <= 1 or term in adjacent_names['names'].values:
            continue

        term_path = calculate_term_path(term, graph, [])
        term_path_len = len(term_path)

        term_metrics.append((term, 1.0 * term_path_len / len(term)))

    shitty_terms = list(filter(lambda x: x[1] == 1.0, term_metrics))
    if len(shitty_terms) > 0 and 1.0 * len(shitty_terms) / len(text.split()) > 0.5:
        return 1 - 1.0 * len(shitty_terms) / len(text.split())

    return 1

def analyze_nn_pos_tag_ratio(text):
    """

    :param text:
    :return:
    """
    text = remove_non_alphabetical_characters_from_text(text)
    text = remove_stop_words(text)
    text = text.lower()

    if len(text) == 0:
        return 1

    tags = extract_pos_tags(text)
    tag_frequencies_df = pd.DataFrame(data=tags, columns=['word', 'tag']).groupby('tag').size().reset_index()
    tag_frequencies_df.columns = ['tag', 'frequency']
    tag_frequencies_df = tag_frequencies_df.sort_values('frequency', ascending=False)

    try:
        ratio = 1.0 * tag_frequencies_df.loc[tag_frequencies_df['tag'] == 'NN', 'frequency'].iloc[0] / tag_frequencies_df['frequency'].sum()
    except Exception as e:
        ratio = 1

    return ratio