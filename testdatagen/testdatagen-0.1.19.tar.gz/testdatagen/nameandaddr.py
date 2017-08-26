"""This nameandaddr module generates pipe ('|') delimited test data with the following fields -
firstname, lastname, email, streetAddress, ZipCode, City, State, StateAbrv, County, Latitude, Longitude

Usage :

    from testdatagen import nameandaddr
    nameandaddr.nameaddr(filename, recordcount)

    example : nameandaddr.nameaddr('persons.csv', 300)

    This example will create  a file named 'persons.csv' in the  directory where this program is located.
    The file 'persons.csv' will have 300 lines.
    It is recommended that you provide a fuly qualified file name (i.e. /path/filename)

"""
import random
import timeit
import csv
from os import path

##
## This module includes five text fies that contain pre generated data that will be used
## in creating the test data.
## The file 'us_postal_codes.csv' is from public domain zipcode data.
## All other files are created from faker module. Each of these files have 50000 lines.
##
list_size = 50000

here = path.abspath(path.dirname(__file__))

csvpath = path.join(here, 'data')

with open(path.join(csvpath, 'us_postal_codes.csv'), 'r') as infile:
    reader = csv.reader(infile)
    next(reader)
    zip_codes = list(reader)
    zip_cnt = len(zip_codes)

with open(path.join(csvpath,'testdata_fn.csv'), 'r') as infile:
    reader = csv.reader(infile)
    first_names = list(reader)

with open(path.join(csvpath,'testdata_st.csv'), 'r') as infile:
    reader = csv.reader(infile)
    street_address = list(reader)

with open(path.join(csvpath,'testdata_ln.csv'), 'r') as infile:
    reader = csv.reader(infile)
    last_names = list(reader)

with open(path.join(csvpath,'testdata_dn.csv'), 'r') as infile:
    reader = csv.reader(infile)
    domain_names = list(reader)


def fake_dataset(writer, rec_cnt):
    random.shuffle(zip_codes)
    random.shuffle(first_names)
    random.shuffle(street_address)
    random.shuffle(last_names)
    random.shuffle(domain_names)

    st = 0
    en = rec_cnt
    testdatalist = []
    for i in range(st, en):

        ln = last_names[i][0]
        fn = first_names[i][0]

        x = first_names[i] + \
            last_names[i] + \
            [ln[0] + fn + '@' + domain_names[i][0]] + \
            street_address[i]

        if i >= zip_cnt:
            j = i - zip_cnt
        else:
            j = i

        x = x + zip_codes[j]

        testdatalist.append(x)

    for item in testdatalist:
        writer.writerow(item)


def nameaddr(filename, recreq):
    """ Generates test data containing firstname, lastname, email, streetAddress
    , ZipCode, City, State, StateAbrv, County, Latitude, Longitude
    It takes two arguments.
    1. filename: file name to  write the test data to
    2. recreq : the number of test data records needed
    example : nameandaddr.nameaddr('persons.csv', 300)
    """
    start_time = timeit.default_timer()


    outfile = open(filename, 'w')
    writer = csv.writer(outfile, delimiter="|")

    ##
    ## The folowing while loop is needed to address the scenarios where the number of tests data records
    ## requested is greater than the value of list size variable defined at the top.
    ##
    recgen = 0
    while recgen < recreq:
        if recreq - recgen > list_size:
            reccnt = list_size
        else:
            reccnt = recreq - recgen

        fake_dataset(writer, reccnt)

        recgen = recgen + reccnt

    elapsed = timeit.default_timer() - start_time

    # print ('time :' + str('%12.6f' % elapsed))

    print('Sucessfully created ' + filename + ' with ' + str(recreq) +
          ' records in ' + str('%7.2f' % elapsed).lstrip() + ' seconds')
    outfile.close()

if __name__ == '__main__':
    nameaddr('persons.csv', 5000)
