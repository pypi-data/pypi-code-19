from datetime import datetime, timedelta
from rupo.generate.lstm import LSTMModelContainer
from rupo.generate.generator import Generator
from rupo.settings import GENERATOR_VOCAB_PATH, GENERATOR_WORD_FORM_VOCAB_PATH
from rupo.main.vocabulary import Vocabulary
from rupo.generate.word_form_vocabulary import WordFormVocabulary
import vk
session = vk.Session(access_token="30e9c2dee1af80d23e789ea6df52c5b4a56fe83fb618391b0e4e0d086442513c9d8e885e94505078d718d")
vk_api = vk.API(session)
lstm = LSTMModelContainer()
word_form_vocabulary = WordFormVocabulary(GENERATOR_WORD_FORM_VOCAB_PATH)
# word_form_vocabulary.inflate_vocab(50001)
vocabulary = Vocabulary(GENERATOR_VOCAB_PATH)
generator = Generator(lstm, vocabulary, word_form_vocabulary)
current_datetime = datetime.now()

hours = 12
metre_schemas = ["+-", "-+"]
rhyme_schemas = ["aabb", "abab", "aabbcc", "abbacc", "abcabc"]
syllable_numbers = [6, 8, 10, 12]
for i in range(200):
    poem = generator.generate_poem(metre_schema=metre_schemas[i % len(metre_schemas)],
                                   rhyme_pattern=rhyme_schemas[i % len(rhyme_schemas)],
                                   n_syllables=syllable_numbers[i % len(syllable_numbers)])
    print(poem)
    if poem is not None:
        publish_date = (current_datetime + timedelta(hours=hours) - datetime(1970, 1, 1)) / timedelta(seconds=1)
        vk_api.wall.post(message=poem, owner_id=-147938156, publish_date=publish_date, from_group=1)
        hours += 4