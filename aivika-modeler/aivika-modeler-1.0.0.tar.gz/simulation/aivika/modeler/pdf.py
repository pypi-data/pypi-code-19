# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

def encode_pdf(pdf):
    """Encode the probability density function."""
    count = len(pdf)
    pdf = map(lambda x: '(' + str(x[0]) + ', ' + str(x[1]) + ')', pdf)
    pdf = '[' + ', '.join(pdf) + ']'
    return pdf
