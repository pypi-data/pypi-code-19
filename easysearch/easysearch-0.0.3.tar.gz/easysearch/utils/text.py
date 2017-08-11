import ast

import gensim

from nltk.corpus import stopwords


def get_text(doc, text_fields, deacc=False, min_len=2, max_len=40):
    """
    Verifica se o documento informado possui os campos de texto informados. Efetua um simple_preprocess do gensim
    no primeiro encontrado e retorna o resultado.

    Parameters:
    ----------
    doc: documento com atributos chave-valor, dictionary
    text_fields: array de strings com nomes de campos do solr, list
    deacc: booleano que determina se os acentos serão removidos das palavras ou não
    min_len: tamanho mínimo das palavras a serem mantidas

    Returns:
    -------
    texts: Texto pre-processado para o primeiro campo encontrado, ou uma string vazia caso nenhum seja encontrado.
    """
    for text_field in text_fields:
        if text_field in doc:
            text = doc[text_field]
            if text is None or len(text) == 0:
                continue
            else:
                return gensim.utils.simple_preprocess(text, deacc=deacc, min_len=min_len, max_len=max_len)
    return ''


def process_text_for_lda(text, phraser, language='portuguese'):
    """
    Realiza o processamento do texto para LDA:
    1. aplicando o simple_preprocess do gensim,
    2. mantém acentos nas palavras
    3. mantém as palavras com no mínimo 3 caracteres
    4. Remove os stopwords
    5. Apenda bigrams de acordo com o phraser informado

    Parameters:
    ----------
    text: texto a ser processado
    phraser: fraseador com n-grams configurado com o corpus ao qual o texto pertence
    language: idioma dos stopwords a serem aplicados

    Returns:
    -------
    texts: lista de palavras processadas a partir do processamento para modelo LDA
    """
    text = gensim.utils.simple_preprocess(text, deacc=False, min_len=3)
    stops = set(stopwords.words(language))
    words = [word for word in text if word not in stops]

    for token in phraser[words]:
        if '_' in token:
            # Token is a bigram, add to document.
            words.append(token)

    return words


def process_texts_for_lda(docs, text_fields, language='portuguese'):
    """
    Realiza o processamento dos textos para treinamento de modelo LDA:
    1. aplicando o simple_preprocess do gensim,
    2. mantém acentos nas palavras
    3. mantém as palavras com no mínimo 3 caracteres
    4. Remove os stopwords
    5. Cria bigrams, apendando os bigrams no texto de cada documento

    Parameters:
    ----------
    doc: documento com atributos chave-valor, dictionary
    text_fields: array de strings com nomes de campos do solr, list
    language: idioma dos stopwords a serem aplicados

    Returns:
    -------
    texts: Lista dos textos dos documentos informados, processados para modelo LDA
    """
    texts = []
    for doc in docs:
        text = get_text(doc=doc, text_fields=text_fields, deacc=False, min_len=3)
        texts.append(text)
    stops = set(stopwords.words(language))
    texts = [[word for word in text if word not in stops] for text in texts]

    phrases = gensim.models.Phrases(texts)
    bigram = gensim.models.phrases.Phraser(phrases)

    for idx in range(len(texts)):
        for token in bigram[texts[idx]]:
            if '_' in token:
                # Token is a bigram, add to document.
                texts[idx].append(token)

    return texts, bigram


def parse_text_args(texts):
    texts = ast.literal_eval(texts)
    return [text.strip() for text in texts]
