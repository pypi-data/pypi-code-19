import pandas as pd
import nltk
from collections import Counter
from nltk.tokenize import RegexpTokenizer

nltk.download("stopwords")
nltk.download('punkt')

# Load nltk's English stopwords as variable called 'default_stopwords'
default_stopwords = nltk.corpus.stopwords.words('english')


def top_gram(dataset, cluster_loop, row_loop, stopwords= False, stoplist = default_stopwords):
    '''
    In text clustering, sometimes the output of a k-means analysis may not be intuitive. This
    function is designed to identify the main criteria of a cluster by identifying the top bi-gram
    associated with each cluster.

    This function creates a DataFrame of each cluster and their top bigram. It does this by
    creating a subset of each cluster, and then creates bigrams for each individual row.
    Those bigrams are joined together into a list, and then run through a counter to
    identify the top bigram.

    Parameters
    --------------
    dataset : DataFrame
        the dataframe being used as an input. At a minimum, it should have two fields: the cluster output and the text fed for clustering
    cluster_loop : string
        the title of the field that records the different clusters output
    row_loop : string
        the title of the field that includes the text for identifying the bigram (can be raw or preprocessed)
    stopwords : bool (optional)
        if True, use stoplist to strip text

    Returns
    ---------
    top_gram :
        returns a DataFrame with 2 columns: the cluster title and a tuple including the topbigram and its count

    '''

    # This is a for loop of the cluster or group of rows we want to analyze.
    for i in range(dataset[cluster_loop].nunique()):
        subset = dataset[dataset[cluster_loop] == i]
        gram_list = []

    # This is a for loop for each row within the subset of data we want to return the bigrams.
        for index, row in subset.iterrows():
            filtered_words = []

            string = str(row[row_loop])
            string_lower = str.lower(string)
            tokenizer = RegexpTokenizer(r'\w+')
            tokens = tokenizer.tokenize(string_lower)

            if stopwords:
                filtered_words = [w for w in tokens if w not in stoplist]
            else:
                filtered_words = [w for w in tokens]

            bigrams = list(nltk.bigrams(filtered_words))
            gram_list.extend(bigrams)

    # This counter keeps track of each of the bigrams that are returned from each row.
        counter = Counter(gram_list)

    # Once a 'block' of text has been processed, only the most common bigram is kept in a new dataframe.
        if i == 0:
            top_gram = pd.DataFrame(data=[[i, counter.most_common(1)]], columns=["Cluster", "Bigram Tuple"])
        else:
            add = pd.DataFrame(data=[[i, counter.most_common(1)]], columns=["Cluster", "Bigram Tuple"])
            top_gram = top_gram.append(add)

    return top_gram
