# De-id script
# import modules
from __future__ import print_function
import os
import sys
import pickle
import glob
import string
import re
import time
import argparse

# import multiprocess
import multiprocessing
from multiprocessing import Pool

# import NLP packages
import nltk
from nltk import sent_tokenize
from nltk import word_tokenize
from nltk.tree import Tree
from nltk import pos_tag_sents
from nltk import ne_chunk
import spacy
from pkg_resources import resource_filename

# import self-defined functions
# from Sql import *
# from Autocorrection import *
# autocorrection and whitelist check
# from Searchterms import *

nlp = spacy.load('en')  # load spacy english library



# configure the regex patterns
# we're going to want to remove all special characters
pattern_word = re.compile(r"[^\w+]")


pattern_number = re.compile(r"""\b(
\d{6}\d*
|(\d[\(\)-.\']?\s?){7}\d+   # SSN/PHONE/FAX XXX-XX-XXXX, XXX-XXX-XXXX, XXX-XXXXXXXX, etc.
)\b""", re.X | re.I)

pattern_postal = re.compile(r"""\b(
\d{5}(-\d{4})?             # postal code XXXXX, XXXXX-XXXX
)\b""", re.X | re.I)

# match DOB
pattern_dob = re.compile(r"""\b(
.*?(?=\b(\d{1,2}[-./\s]\d{1,2}[-./\s]\d{2}  # X/X/XX
|\d{1,2}[-./\s]\d{1,2}[-./\s]\d{4}          # XX/XX/XXXX
|\d{2}[-./\s]\d{1,2}[-./\s]\d{1,2}          # xx/xx/xx
|\d{4}[-./\s]\d{1,2}[-./\s]\d{1,2}          # xxxx/xx/xx
)\b)
)\b""", re.X | re.I)

# match emails
pattern_email = re.compile(r"""\b(
[a-zA-Z0-9_.+-@\"]+@[a-zA-Z0-9-\:\]\[]+[a-zA-Z0-9-.]*
)\b""", re.X | re.I)

# match date, similar to DOB but does not include any words
pattern_date = re.compile(r"""\b(
\d{1,2}[-./\s]\d{1,2}[-./\s]\d{2}
|\d{1,2}[-./\s]\d{1,2}[-./\s]\d{4}
|\d{2}[-./\s]\d{1,2}[-./\s]\d{1,2}
|\d{4}[-./\s]\d{1,2}[-./\s]\d{1,2}
)\b""", re.X | re.I)

# match names, A'Bsfs, Absssfs, A-Bsfsfs
pattern_name = re.compile(r"""^[A-Z]\'?[-a-zA-Z]+$""")

# match age
pattern_age = re.compile(r"""\b(
age|year[s-]?\s?old|y.o[.]?
)\b""", re.X | re.I)

# match salutation
pattern_salutation = re.compile(r"""
(Dr\.|Mr\.|Mrs\.|Ms\.|Miss|Sir|Madam)\s
(([A-Z]\'?[A-Z]?[-a-z ]+)*
)""", re.X)

# check if the folder exists
def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The folder %s does not exist. Please input a new folder or create one." % arg)
    else:
        return arg

# check if word is in name_set, if not, check the word by single word level
def namecheck(word_output, name_set, screened_words, safe):
    # check if the word is in the name list
    if word_output.title() in name_set:
        # with open("name.txt", 'a') as fout:
           # fout.write(word_output + '\n')
        # print('Name:', word_output)
        screened_words.append(word_output)
        word_output = "**PHI**"
        safe = False

    else:
    # check spacy, and add the word to the name list if it is a name
    # check the word's title version and its uppercase version
        doc1 = nlp(word_output.title())
        doc2 = nlp(word_output.upper())
        if (doc1.ents != () and doc1.ents[0].label_ == 'PERSON' and
                doc2.ents != () and doc2.ents[0].label_ is not None):
            # with open("name.txt", 'a') as fout:
               # fout.write(word_output + '\n')
            # print('Name:', word_output)
            screened_words.append(word_output)
            name_set.add(word_output.title())
            word_output = "**PHI**"
            safe = False

    return word_output, name_set, screened_words, safe


def filter_task(f, whitelist_dict, foutpath, key_name):

    with open(f, encoding='utf-8', errors='ignore') as fin:
        # basic settings
        head, tail = os.path.split(f)
        f_name = re.findall(r'[\w\d]+', tail)[0]  # get the file number
        print(f_name)
        start_time_single = time.time()
        total_records = 1
        phi_containing_records = 0
        safe = True
        screened_words = []
        name_set = set()
        phi_reduced = ''
        address_indictor = ['street', 'avenue', 'road', 'boulevard',
                            'drive', 'trail', 'way', 'lane', 'ave',
                            'blvd', 'st', 'rd', 'trl', 'wy', 'ln']

        note = fin.read()
        # saluation check
        re_list = pattern_salutation.findall(note)
        for i in re_list:
            name_set = name_set | set(i[1].split(' '))

        # note_length = len(word_tokenize(note))
        note = sent_tokenize(note)

        for sent in note:
            # postal code check
            if pattern_postal.findall(sent) != []:
                safe = False
                for item in pattern_postal.findall(sent):
                    screened_words.append(item[0])
            sent = str(pattern_postal.sub('**PHIPostal**', sent))

            # number check
            if pattern_number.findall(sent) != []:
                safe = False
                for item in pattern_number.findall(sent):
                    # print(item)
                    if pattern_date.match(item[0]) is None:
                        sent = sent.replace(item[0], '**PHI**')
                        screened_words.append(item[0])

            # email check
            if pattern_email.findall(sent) != []:
                safe = False
                for item in pattern_email.findall(sent):
                    screened_words.append(item)
            sent = str(pattern_email.sub('**PHI**', sent))

            # dob check
            re_list = pattern_dob.findall(sent)
            i = 0
            while True:
                if i >= len(re_list):
                    break
                else:
                    text = ' '.join(re_list[i][0].split(' ')[-6:])
                    if re.findall(r'\b(birth|dob)\b', text, re.I) != []:
                        safe = False
                        sent = sent.replace(re_list[i][1], '**PHI**')
                        screened_words.append(re_list[i][1])
                    i += 2

            # NLP process
            sent = re.sub(r'[\/\-\:\~\_]', ' ', sent)
            doc = nlp(sent)
            sent = [word_tokenize(sent)]

            for position in range(0, len(sent[0])):
                word = sent[0][position]
                # age check
                if word.isdigit() and int(word) > 90:
                    if position <= 2:  # check the words before age
                        word_previous = ' '.join(sent[0][:position])
                    else:
                        word_previous = ' '.join(sent[0][position - 2:position])
                    if position >= len(sent[0]) - 2:  # check the words after age
                        word_after = ' '.join(sent[0][position+1:])
                    else:
                        word_after = ' '.join(sent[0][position+1:position +3])

                    age_string = str(word_previous) + str(word_after)
                    if pattern_age.findall(age_string) != []:
                        screened_words.append(sent[0][position])
                        sent[0][position] = '**PHI**'
                        safe = False

                # address check
                elif (position >= 1 and position < len(sent[0])-1 and
                      (word.lower() in address_indictor or
                       (word.lower() == 'dr' and sent[0][position+1] != '.')) and
                      (word.istitle() or word.isupper())):

                    if sent[0][position - 1].istitle() or sent[0][position-1].isupper():
                        screened_words.append(sent[0][position - 1])
                        sent[0][position - 1] = '**PHI**'
                        i = position - 1
                        # find the closet number, should be the number of street
                        while True:
                            if re.findall(r'^[\d-]+$', sent[0][i]) != []:
                                begin_position = i
                                break
                            elif i == 0 or position - i > 5:
                                begin_position = position
                                break
                            else:
                                i -= 1
                        i = position + 1
                        # block the info of city, state, apt number, etc.
                        while True:
                            if '**PHIPostal**' in sent[0][i]:
                                end_position = i
                                break
                            elif i == len(sent[0]) - 1:
                                end_position = position
                                break
                            else:
                                i += 1
                        if end_position <= position:
                            end_position = position

                        for i in range(begin_position, end_position):
                            #if sent[0][i] != '**PHIPostal**':
                            screened_words.append(sent[0][i])
                            sent[0][i] = '**PHI**'
                            safe = False

            sent_tag = nltk.pos_tag_sents(sent)
            # check if the word is a name based on sentence level
            for ent in doc.ents:  # doc is set in line 168
                if ent.label_ == 'PERSON':
                #print(ent.text)
                    doc1 = nlp(ent.text)
                    if doc1.ents != () and doc1.ents[0].label_ == 'PERSON':
                        name_tag = word_tokenize(ent.text)
                        name_tag = pos_tag_sents([name_tag])
                        chunked = ne_chunk(name_tag[0])
                        for i in chunked:
                            if type(i) == Tree:
                                if i.label() == 'PERSON':
                                    for token, pos in i.leaves():
                                        if pos == 'NNP':
                                            name_set.add(token)

                                else:
                                    for token, pos in i.leaves():
                                        doc2 = nlp(token.upper())
                                        if doc2.ents != ():
                                            name_set.add(token)

            # whitelist check
            for i in range(len(sent_tag[0])):
                word = sent_tag[0][i]
                # print(word)
                word_output = word[0]
                if word_output not in string.punctuation:
                    #word_check = word_output
                    word_check = str(pattern_word.sub('', word_output))
                        # remove the speical chars
                    try:

                        if ((word[1] == 'NN' or word[1] == 'NNP') or
                                ((word[1] == 'NNS' or word[1] == 'NNPS') and word_check.istitle())):
                            #autoc = autocorrect(word_check, whitelist_dict)
                            #word_modif, check_flag = autoc.autocheck()
                            if word_check.lower() not in whitelist_dict:
                                screened_words.append(word_output)
                                word_output = "**PHI**"
                                safe = False
                            else:
                                # name check for the word in whitelist
                                if (word_output.istitle() or word_output.isupper()) and pattern_name.findall(word_output) != []:
                                    word_output, name_set, screened_words, safe = namecheck(word_output, name_set, screened_words, safe)

                    except:
                        print(word[0], sys.exc_info())

                    phi_reduced = phi_reduced + ' ' + word_output
                else:
                    if i > 0 and sent_tag[0][i-1][0][-1] in string.punctuation:
                        phi_reduced = phi_reduced + word_output
                    else:
                        phi_reduced = phi_reduced + ' ' + word_output

        if not safe:
            phi_containing_records = 1

        # save phi_reduced file
        filename = "whitelisted_"+key_name+"_"+f_name+".txt"
        filepath = os.path.join(foutpath, filename)
        with open(filepath, "w") as phi_reduced_note:
            phi_reduced_note.write(phi_reduced)

        # save filtered word
        screened_words = list(filter(lambda a: a!= '**PHI**', screened_words))
        filepath = os.path.join(foutpath,'filter_summary.txt')
        #print(filepath)
        screened_words = list(filter(lambda a: a != '**PHIPostal**', screened_words))
        with open(filepath, 'a') as fout:
            fout.write(str(f_name)+' ' + str(len(screened_words)) +
                ' ' + ' '.join(screened_words)+'\n')
            # fout.write(' '.join(screened_words))

        print(total_records, f, "--- %s seconds ---" % (time.time() - start_time_single))

        return total_records, phi_containing_records


def main():
    # get input/output/filename
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", default="input_test/",
                    help="Path to the directory or the file that contains the PHI note, the default is ./input_test/.",
                    type=lambda x: is_valid_file(ap, x))
    ap.add_argument("-r", "--recursive", action = 'store_true', default = False,
                    help="whether read files in the input folder recursively.")
    ap.add_argument("-o", "--output", default="output_test/",
                    help="Path to the directory that save the PHI-reduced note, the default is ./output_test/.",
                    type=lambda x: is_valid_file(ap, x))
    ap.add_argument("-w", "--whitelist",
                    #default=os.path.join(os.path.dirname(__file__), 'whitelist.pkl'),
                    default=resource_filename(__name__, 'whitelist.pkl'),
                    help="Path to the whitelist, the default is phireducer/whitelist.pkl")
    ap.add_argument("-n", "--name", default="phi_reduced",
                    help="The key word of the output file name, the default is whitelisted_phi_reduced_*.txt.")
    ap.add_argument("-p", "--process", default=1, type=int,
                    help="The number of multiple process, the default is 1.")
    args = ap.parse_args()

    finpath = args.input
    foutpath = args.output
    key_name = args.name
    whitelist_file = args.whitelist
    process_number = args.process
    if_dir = os.path.isdir(finpath)

    start_time_all = time.time()
    if if_dir:
        print('input folder:', finpath)
        print('recursive?:', args.recursive)
    else:
        print('input file:', finpath)
        head, tail = os.path.split(finpath)
        f_name = re.findall(r'[\w\d]+', tail)[0]
    print('output folder:', foutpath)
    print('Using whitelist:', whitelist_file)
    try:
        with open(whitelist_file, "rb") as fin:
            whitelist = pickle.load(fin)
        print('length of whitelist: {}'.format(len(whitelist)))
        if if_dir:
            print('phi_reduced file\'s name would be:', foutpath+"/whitelisted_"+key_name+"_*.txt")
        else:
            print('phi_reduced file\'s name would be:', foutpath+"/whitelisted_"+key_name+"_"+f_name+".txt")
        print('run in {} process(es)'.format(process_number))
    except FileNotFoundError:
        print("No whitelist is found. The script will stop.")
        whitelist = set()


    # start multiprocess
    pool = Pool(processes=process_number)

    results_list = []
    filter_time = time.time()

    if len(whitelist) != 0:
        if os.path.isdir(finpath):
            if args.recursive:
                results = [pool.apply_async(filter_task, (f,)+(whitelist, foutpath, key_name)) for f in glob.glob   (finpath+"/**/*.txt", recursive=True)]
            else:
                results = [pool.apply_async(filter_task, (f,)+(whitelist, foutpath, key_name)) for f in glob.glob   (finpath+"/*.txt")]
        else:
            results = [pool.apply_async(filter_task, (f,)+(whitelist, foutpath, key_name)) for f in glob.glob(  finpath)]
        try:
            results_list = [r.get() for r in results]
            total_records, phi_containing_records = zip(*results_list)
            total_records = sum(total_records)
            phi_containing_records = sum(phi_containing_records)

            print("total records:", total_records, "--- %s seconds ---" % (time.time() - start_time_all))
            print('filter_time', "--- %s seconds ---" % (time.time() - filter_time))
            print('total records processed: {}'.format(total_records))
            print('num records with phi: {}'.format(phi_containing_records))
        except ValueError:
            print("No txt file in the input folder.")
            pass

        pool.close()
        pool.join()
    # close multiprocess


if __name__ == "__main__":
    multiprocessing.freeze_support()  # must run for windows
    main()
