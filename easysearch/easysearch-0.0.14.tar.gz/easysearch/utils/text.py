import ast

import gensim

from nltk.corpus import stopwords
from nltk import RegexpTokenizer


def get_text_for_doc2vec(doc, text_fields):
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
    tokenizer = RegexpTokenizer(r'\w+')
    stopword_set = get_custom_stopwords()
    for text_field in text_fields:
        if text_field in doc:
            text = doc[text_field]
            if text is None or len(text) == 0:
                continue
            else:
                text = text.lower()
                words = tokenizer.tokenize(text)
                return list(set(words).difference(stopword_set))
    return ''


def process_text_for_lda(text, phraser=None, language='portuguese'):
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

    if phraser is not None:
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


def get_custom_stopwords():
    return ['a','agora','ainda','alem','algum','alguma','algumas','alguns','alguém','além','ambas','ambos','ampla',\
            'amplas','amplo','amplos','and','ante','antes','ao','aonde','aos','apos','após','aquela','aquelas',\
            'aquele','aqueles','aquilo','as','assim','através','até','cada','coisa','coisas','com','como','contra',\
            'contudo','cuja','cujas','cujo','cujos','côm','da','daquele','daqueles','das','data','de','dela','delas',\
            'dele','deles','demais','depois','desde','dessa','dessas','desse','desses','desta','destas','deste',\
            'destes','deve','devem','devendo','dever','deveria','deveriam','deverá','deverão','devia','deviam',\
            'dispoe','dispoem','dispõe','dispõem','disse','disso','disto','dito','diversa','diversas','diversos','diz',\
            'dizem','do','dos','durante','dà','dàs','dá','dás','dê','e','ela','elas','ele','eles','em','enquanto',\
            'entao','entre','então','era','eram','essa','essas','esse','esses','esta','estamos','estas','estava',\
            'estavam','este','esteja','estejam','estejamos','estes','esteve','estive','estivemos','estiver','estivera',\
            'estiveram','estiverem','estivermos','estivesse','estivessem','estivéramos','estivéssemos','estou','està',\
            'estàs','está','estás','estávamos','estão','eu','fazendo','fazer','feita','feitas','feito','feitos','foi',\
            'fomos','for','fora','foram','forem','formos','fosse','fossem','fui','fôramos','fôssemos','grande',\
            'grandes','ha','haja','hajam','hajamos','havemos','havia','hei','houve','houvemos','houver','houvera',\
            'houveram','houverei','houverem','houveremos','houveria','houveriam','houvermos','houverá','houverão',\
            'houveríamos','houvesse','houvessem','houvéramos','houvéssemos','há','hão','isso','isto','já','la','lhe',\
            'lhes','lo','logo','lá','mais','mas','me','mediante','menos','mesma','mesmas','mesmo','mesmos','meu','meus',\
            'minha','minhas','muita','muitas','muito','muitos','na','nas','nem','nenhum','nessa','nessas','nesse',\
            'nesta','nestas','neste','ninguém','no','nos','nossa','nossas','nosso','nossos','num','numa','nunca','ná',\
            'nás','não','nós','o','or','os','ou','outra','outras','outro','outros','para','pela','pelas','pelo','pelos',\
            'pequena','pequenas','pequeno','pequenos','per','perante','pode','podendo','poder','poderia','poderiam',\
            'podia','podiam','pois','por','porque','porquê','portanto','porém','posso','pouca','poucas','pouco','poucos',\
            'primeiro','primeiros','proprio','própria','próprias','próprio','próprios','pôde','quais','qual','qualquer',\
            'quando','quanto','quantos','quaís','que','quem','quer','quê','se','seja','sejam','sejamos','sem','sempre',\
            'sendo','ser','serei','seremos','seria','seriam','será','serão','seríamos','seu','seus','si','sido','sob',\
            'sobre','somos','sou','sua','suas','são','só','tal','talvez','tambem','também','tampouco','te','tem','temos',\
            'tendo','tenha','tenham','tenhamos','tenho','ter','terei','teremos','teria','teriam','terá','terão','teríamos',\
            'teu','teus','teve','ti','tido','tinha','tinham','tive','tivemos','tiver','tivera','tiveram','tiverem',\
            'tivermos','tivesse','tivessem','tivéramos','tivéssemos','toda','todas','todavia','todo','todos','tu','tua',\
            'tuas','tudo','tém','têm','tínhamos','um','uma','umas','uns','vendo','ver','vez','vindo','vir','você',\
            'vocês','vos','vós','à','às','á','ás','ão','è','é','éramos','êm','ò','ó','õ','última','últimas','último',\
            'últimos']