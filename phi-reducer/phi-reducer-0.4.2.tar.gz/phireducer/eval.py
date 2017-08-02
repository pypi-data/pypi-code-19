from nltk import sent_tokenize
from nltk import word_tokenize
import argparse
from string import punctuation
import pickle
from difflib import ndiff
import os
import re
import glob


def comparison(note_id, file1path, file2path):

    summary_dict = {}
    output = ''

    with open(file1path, 'r') as fin:
        phi_reduced_note = fin.read()
    with open(file2path, 'rb') as fin:
        annotation = pickle.load(fin)

    note = sent_tokenize(phi_reduced_note)
    note = [word_tokenize(sent) for sent in note]
    note = [word for sent in note for word in sent]
    note = [word for word in note if word not in punctuation]

    temp_annotation = [word[0] for word in annotation if word[1] == '0' and word[0] != '']
    note_temp = [word for word in note if (word != '**PHI**' and word != '**PHIPostal**')]
    note_phi = [word for word in note if (word == '**PHI**' or word == '**PHIPostal**')]

    script_filtered = len(note_phi)
    summary_dict['false_positive'] = []
    summary_dict['false_negative'] = []

    for i, s in enumerate(ndiff(note_temp, temp_annotation)):
        if s[0] == '+':
            summary_dict['false_positive'].append(s[2:])
        elif s[0] == '-':
            summary_dict['false_negative'].append(s[2:])

    true_positive = script_filtered-len(summary_dict['false_positive'])+len(summary_dict['false_negative'])
    summary_dict['true_positive'] = true_positive

    output = 'Note: ' + note_id + '\n'
    output += "Script filtered: " + str(script_filtered) + '\n'
    output += "True positive: " + str(true_positive) + '\n'
    output += "False Positive: " + ' '.join(summary_dict['false_positive']) + '\n'
    output += "FP number: " + str(len(summary_dict['false_positive'])) + '\n'
    output += "False Negative: " + ' '.join(summary_dict['false_negative']) + '\n'
    output += "FN number: " + str(len(summary_dict['false_negative'])) + '\n'
    output += "Recall: {:.2%}".format(true_positive/(true_positive+len(summary_dict['false_negative']))) + '\n'
    output += "Precision: {:.2%}".format(true_positive/(true_positive+len(summary_dict['false_positive']))) + '\n'
    output += '\n'
    #print(output)
    return summary_dict, output


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--phinote", required=True,
                    help="Path to the phi reduced note, *.txt.")
    ap.add_argument("-a", "--annotation", required=True,
                    help="Path to the annotated file, *.ano.")
    ap.add_argument("-o", "--output", required=True,
                    help="Path to save the summary pkl and statistics text.")
    ap.add_argument("-r", "--recursive", action = 'store_true', default = False,
                    help="whether read files in the input folder recursively.")
    args = ap.parse_args()

    file1path = args.phinote
    file2path = args.annotation
    foutpath = args.output
    if_recursive = args.recursive
    summary_dict_all = {}
    summary_text = ''
    phi_reduced_dict = {}
    annotation_dict = {}
    miss_file = []
    TP_all = 0
    FP_all = 0
    FN_all = 0
    phi_length = 0
    output = ''
    if_update = False

    if os.path.isfile(file1path) != os.path.isfile(file2path):
        print("phi note input and annotation input should be both files or folders.")
    else:
        if os.path.isfile(file1path):
            head1, tail1 = os.path.split(file1path)
            head2, tail2 = os.path.split(file2path)
            if re.findall(r'\d+', tail1)[0] != re.findall(r'\d+', tail2)[0]:
                print('Please make sure the note_ids are the same in both file.')
            else:
                note_id = re.findall(r'\d+', tail1)[0]
                summary_dict, output = comparison(note_id, file1path, file2path)
                summary_dict_all[note_id] = summary_dict
                summary_text += output
                if_update = True
        else:
            reply = input('Please make sure no repeated note id in each folders.'
                        'Press Enter to process or others to quit.> ')
            if reply == '':
                if if_recursive:
                    for f in glob.glob(file1path + "/**/*.txt", recursive=True):
                        head, tail = os.path.split(f)
                        if re.findall(r'\d+', tail) != []:
                            note_id = re.findall(r'\d+', tail)[0]
                            phi_reduced_dict[note_id] = f
                            phi_length += 1
                    for f in glob.glob(file2path + "/**/*.ano", recursive=True):
                        head, tail = os.path.split(f)
                        if re.findall(r'\d+', tail) != []:
                            note_id = re.findall(r'\d+', tail)[0]
                            annotation_dict[note_id] = f
                else:
                    for f in glob.glob(file1path + "/*.txt"):
                        head, tail = os.path.split(f)
                        if re.findall(r'\d+', tail) != []:
                            note_id = re.findall(r'\d+', tail)[0]
                            phi_reduced_dict[note_id] = f
                            phi_length += 1
                    for f in glob.glob(file2path + "/*.ano"):
                        head, tail = os.path.split(f)
                        if re.findall(r'\d+', tail) != []:
                            note_id = re.findall(r'\d+', tail)[0]
                            annotation_dict[note_id] = f

                for i in phi_reduced_dict.keys():
                    if i in annotation_dict.keys():
                        summary_dict, output = comparison(i, phi_reduced_dict[i], annotation_dict[i])
                        summary_dict_all[i] = summary_dict
                        summary_text += output
                        if_update = True
                    else:
                        miss_file.append(phi_reduced_dict[i])

                print('{:d} out of {:d} phi reduced notes have been compared.'.format(phi_length-len(miss_file), phi_length))
                print('{} files have not found corresponding annotation as below.'.format(len(miss_file)))
                print('\n'.join(miss_file)+'\n')

                for k,v in summary_dict_all.items():
                    TP_all += v['true_positive']
                    FP_all += len(v['false_positive'])
                    FN_all += len(v['false_negative'])

                output = "True positive in all notes: " + str(TP_all) + '\n'
                output += "False Positive in all notes: " + str(FP_all) + '\n'
                output += "False Negative in all notes: " + str(FN_all) + '\n'
                output += "Recall: {:.2%}".format(TP_all/(TP_all+FN_all)) + '\n'
                output += "Precision: {:.2%}".format(TP_all/(TP_all+FP_all)) + '\n'
                summary_text += output
            else:
                print("Please re-run the script after all the files are ok.")

        print(output)
        if if_update:
            with open(foutpath + "/summary_dict.pkl", 'wb') as fout:
                pickle.dump(summary_dict_all, fout)
            with open(foutpath + '/summary_text.txt', 'w') as fout:
                fout.write(summary_text)


if __name__ == "__main__":
    main()
