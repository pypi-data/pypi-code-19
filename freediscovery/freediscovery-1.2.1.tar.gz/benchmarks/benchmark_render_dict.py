import pandas as pd
import numpy as np
from time import time

from freediscovery.ingestion import DocumentIndex


def test_performance():

    md = []
    t0 = time()

    for idx in range(10000):
        md.append({'file_path': '/test{}'.format(idx),
                   'internal_id': idx,
                   'document_id': idx**2})
    query = []
    for idx in range(10000):
        query.append({'internal_id': idx, 
                   'a': np.random.randint(100)
                   })
    query = pd.DataFrame(query)

    dbi = DocumentIndex.from_list(md)
    print(time() - t0)

    t0 = time()
    rd = dbi.render_dict(query)
    print(time() - t0)
    print(len(rd))


test_performance()
