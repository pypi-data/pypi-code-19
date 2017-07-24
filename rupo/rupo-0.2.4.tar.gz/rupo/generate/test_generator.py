# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Тесты генератора.

import os
import pickle
from rupo.settings import DATA_DIR, GENERATOR_LSTM_MODEL_PATH
from rupo.generate.grammeme_vectorizer import GrammemeVectorizer
from rupo.generate.word_form_vocabulary import WordFormVocabulary
from rupo.generate.lstm import LSTMGenerator


filename = "/media/data/PoetryMorph.txt"

# vectorizer = GrammemeVectorizer()
# vectorizer.collect_grammemes(filename)
# print(vectorizer.get_ordered_grammemes())
# vectorizer.collect_possible_vectors(filename)
# print(vectorizer.vectors)
#
# vocab = WordFormVocabulary()
# vocab.load_from_corpus(filename, grammeme_vectorizer=vectorizer)
# print(vocab.word_forms)

lstm = LSTMGenerator(nn_batch_size=256, external_batch_size=10000, embedding_size=5000, embeddings_dimension=50,
                     lstm_units=128, dense_units=64)
lstm.prepare([filename, ])
lstm.build()
# lstm.load(GENERATOR_LSTM_MODEL_PATH)
# print(lstm.model.summary())
lstm.train([filename, ], validation_size=3, validation_verbosity=50, dump_model_freq=20)