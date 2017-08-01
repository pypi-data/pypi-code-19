from nltk import sent_tokenize
from nltk import word_tokenize
import argparse
from string import punctuation
import pickle
import os
import sys
import re


def annotating(note):
    annotation_list = []
    note = sent_tokenize(note)
    allowed_category = ('0', '1', '2', '3', '4', '5', '6', '7')
    allowed_command = ('exit', 'all', 'from', 'pick', 'show', 'done', 'help')
    allowed_input = allowed_category + allowed_command
    for sent in note:
        sent_list = []
        words = word_tokenize(sent)
        word = [word for word in words if word not in punctuation]
        print(sent)
        for j in range(len(word)):
            sent_list.append([word[j], '0', j+1])
        print('\n')
        [print("({}){}[{}]".format(temp[2], temp[0], temp[1]), end=' ') for temp in sent_list]
        print('\n')
        # for idx, val in enumerate(word):
           # print("({}){} ".format(idx + 1, val), end='')
        print('Category to use: 0:Non-phi, 1:Name, 2:Address, 3:Postal code,'
             '4:Phone/FAX, 5:SSN, 6:DOB, 7:others\n')

        i = 0
        while True:
            #if i == len(word):
               # user_input = input('The end of the sentence. Enter done to next sentence or others to edit. #> ')
               # if user_input == 'done':
               #     break
               # else:
               #     i = i - 1


            user_input = input('Please input command (enter \'help\' for more info): ')

            if user_input not in allowed_command:
                print("Command is not right, please re-input.")

            else:
                if user_input == 'exit':
                    return []

                elif user_input == 'all':
                    user_input = input('which kind of info are all words? > ')
                    if user_input in allowed_category:
                        for j in range(0,len(word)):
                            sent_list[j][1] = user_input
                        user_input = input('Press Enter to finish the'
                                     ' editing of this sentence, or others'
                                     ' to go back to the commend type. > ')
                        if user_input == '':
                            break
                    else:
                        print('Wrong category. Will go back to the commend type.')

                elif user_input == 'from':
                    start_word = input('From which word to edit at the same time: ')
                    if start_word.isdigit() and 0 < int(start_word) <= len(word):
                        end_word = input('To which word to edit at the same time: ')
                        if end_word.isdigit() and int(start_word) < int(end_word) <= len(word):
                            category = input('which kind of info are these words? > ')
                            if category in allowed_category:
                                for j in range(int(start_word)-1, int(end_word)):
                                    sent_list[j][1] = category
                                #annotation_list.append([word[j], category])
                            else:
                                print('Wrong category. Will go back to the commend type.')
                        else:
                            print('Wrong word. Will go back to the commend type.')
                    else:
                        print('Wrong word. Will go back to the commend type.')

                elif user_input == 'pick':
                    user_input = input('which words are you going to edit, seperated by space: ')
                    pick_list = user_input.split(' ')
                    user_input = input('which kind of info are these words? > ')
                    if user_input in allowed_category:
                        for j in pick_list:
                            if j.isdigit() and 0 < int(j) <= len(word):
                                sent_list[int(j)-1][1] = user_input
                                print('{} is changed.'.format(sent_list[int(j)-1][0]))
                            else:
                                print('{} is not a right sequence'.format(j))
                    else:
                        print('Wrong category. Will go back to the word you were editing.')

                elif user_input == 'show':
                    print('\n')
                    [print("({}){}[{}]".format(temp[2], temp[0], temp[1]), end=' ') for temp in sent_list]
                    print('\n')

                elif user_input == 'done':
                    break

                elif user_input == 'help':
                    print('(X)WORD[Y]: X is the sequence number of the word, Y is the current type of the word. All words will be set to 0, non-phi, as default.')
                    print('Command:')
                    print('all: enter \'all\' to change all words\' type at the same time.')
                    print('from: enter \'from\' to change successive words\'type at the same time.')
                    print('pick: enter \'pick\' to change single or multiple(not successive)'
                        ' words\' type at the same time.')
                    print('show: enter \'show\' to show the current status of all words')
                    print('done: enter \'done\' to finish the edit fo this sentence and start the next one.')
                    print('exit: enter \'exit\' to exit the script without saving. \n')
                '''
                else:
                    #temp = re.sub(r'[\/\-\:\~\_]', ' ', word[i])
                    #temp = temp.split(' ')
                    #for j in temp:
                    #    annotation_list.append([j, user_input])
                    sent_list[i][1] = user_input
                    i += 1
                    '''
        '''
        for i in word:
            if i not in punctuation:
                category = input("{} > ".format(i))
                # sys.stdout.flush()
                i = re.sub(r'[\/\-\:\~\_]', ' ', i)
                temp = i.split(' ')
                for j in temp:
                    annotation_list.append([j, category])
                    '''
        for result in sent_list:
            temp = re.sub(r'[\/\-\:\~\_]', ' ', result[0])
            temp = temp.split(' ')
            for j in temp:
                annotation_list.append([j, result[1]])
        #[annotation_list.append(result) for result in sent_list]
        print("\n")
            # else:
                # annotation_list.append((i,'0'))
        # annotation_list.append([sent_list])

    return annotation_list


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--inputfile", required=True,
                    help="Path to the file that contains the PHI note.")
    ap.add_argument("-o", "--output", required=True,
                    help="Path to the directory that save the annotated notes.")

    args = ap.parse_args()

    finpath = args.inputfile
    if os.path.isfile(finpath):
        head, tail = os.path.split(finpath)
    foutpath = args.output

    with open(finpath, encoding='utf-8', errors='ignore') as fin:
        note = fin.read()
    annotation_list = annotating(note)
    file_name = foutpath + "/annotated_" + tail.split('.')[0] + ".ano"
    if annotation_list != []:
        print(annotation_list)
        with open(file_name, 'wb') as fout:
            pickle.dump(annotation_list, fout)


if __name__ == "__main__":
    main()
