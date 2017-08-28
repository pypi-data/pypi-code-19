# See https://github.com/facebookresearch/fastText/blob/master/get-wikimedia.sh
#
# From https://github.com/facebookresearch/fastText/issues/161:
#
# We now have a script called 'get-wikimedia.sh', that you can use to download and
# process a recent wikipedia dump of any language. This script applies the preprocessing
# we used to create the published word vectors.
#
# The parameters we used to build the word vectors are the default skip-gram settings,
# except with a dimensionality of 300 as indicated on the top of the list of word
# vectors (we now understand that this could be more visible).

'''
        sed -e "s/’/'/g" -e "s/′/'/g" -e "s/''/ /g" -e "s/'/ ' /g" -e "s/“/\"/g" -e "s/”/\"/g" \
            -e 's/"/ " /g' -e 's/\./ \. /g' -e 's/<br \/>/ /g' -e 's/, / , /g' -e 's/(/ ( /g' -e 's/)/ ) /g' -e 's/\!/ \! /g' \
            -e 's/\?/ \? /g' -e 's/\;/ /g' -e 's/\:/ /g' -e 's/-/ - /g' -e 's/=/ /g' -e 's/=/ /g' -e 's/*/ /g' -e 's/|/ /g' \
            -e 's/«/ /g' | tr 0-9 " "
'''
SUBEXES = ["s/’/'/g", "s/′/'/g", "s/''/ /g", "s/'/ ' /g", 's/“/"/g', 's/”/"/g', 's/"/ /g', "s/\\./ \\. /g", "s/<br \\/>/ /g", "s/, / , /g", "s/(/ ( /g", "s/)/ ) /g", "s/\\!/ \\! /g", "s/\\?/ \\? /g", "s/\\;/ /g", "s/\\:/ /g", "s/-/ - /g", "s/=/ /g", "s/=/ /g", "s/*/ /g", "s/|/ /g", "s/«/ /g"]

# Program to filter Wikipedia XML dumps to "clean" text consisting only of lowercase
# letters (a-z, converted from A-Z), and spaces (never consecutive)...
# All other characters are converted to spaces.  Only text which normally appears.
# in the web browser is displayed.  Tables are removed.  Image captions are.
# preserved.  Links are converted to normal text.  Digits are spelled out.
# *** Modified to not spell digits or throw away non-ASCII characters ***
# Written by Matt Mahoney, June 10, 2006.  This program is released to the public domain.

import subprocess

def preproc(s):
    s = s.lower()
    for subex in SUBEXES:
        #print("Applying", subex)
        s = subprocess.check_output(['sed', subex], input=s.encode()).decode("utf-8")
        # print(s)
    # Whitespace
    s = ' '.join(s.split())
    return s
