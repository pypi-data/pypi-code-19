#!/bin/bash/env python

from hello_civis import helloCivis


if __name__ == "__main__":
    hello = helloCivis()
    print(hello.return_phrase())
