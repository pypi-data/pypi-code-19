"""
QuantGo services definitions
"""

EQUITIES_TAQ = {
                "name": "EQUITIES_TAQ",
                "bucket": "us-equity-taq",
                "type": "equities",
                "file_structure": 0
               }

EQUITIES_1MIN = {
                 "name": "EQUITIES_1MIN",
                 "bucket": "us-equity-1min",
                 "type": "equities",
                 "file_structure": 0
               }

EQUITIES_TRADES = {
                   "name": "EQUITIES_TRADES",
                   "bucket": "us-equity-trades",
                   "type": "equities",
                   "file_structure": 0
                   }

EQUITIES_1MIN_TRADES = {
                        "name": "EQUITIES_1MIN_TRADES",
                        "bucket": "us-equity-1min",
                        "type": "equities",
                        "file_structure": 0
                        }

FUTURES_OLD_TAQ = {
                   "name": "FUTURES_OLD_TAQ",
                   "bucket": "us-futures-taq",
                   "type": "futures",
                   "file_structure": 1
                   }

FUTURES_OLD_1MIN = {
                    "name": "FUTURES_OLD_1MIN",
                    "bucket": "us-futures-1min",
                    "type": "futures",
                    "file_structure": 1
                    }

FUTURES_OLD_1MIN_TRADES = {
                           "name": "FUTURES_OLD_1MIN_TRADES",
                           "bucket": "us-futures-1min-trades",
                           "type": "futures",
                           "file_structure": 1
                           }

FUTURES_TAQ = {
               "name": "FUTURES_TAQ",
               "bucket": "us-futures-taq-%d",
               "type": "futures",
               "start_year": 2009,
               "file_structure": 2
               }

FUTURES_TRADES = {
                  "name": "FUTURES_TRADES",
                  "bucket": "us-futures-taq-%d",
                  "type": "futures",
                  "start_year": 2009,
                  "file_structure": 2
                  }

FUTURES_1MIN = {
                "name": "FUTURES_1MIN",
                "bucket": "us-futures-1min-taq-%d",
                "type": "futures",
                "start_year": 2009,
                "file_structure": 2
                }

FUTURES_1MIN_TRADES = {
                       "name": "FUTURES_1MIN_TRADES",
                       "bucket": "us-futures-1min-trades-%d",
                       "type": "futures",
                       "start_year": 2009,
                       "file_structure": 2
                       }