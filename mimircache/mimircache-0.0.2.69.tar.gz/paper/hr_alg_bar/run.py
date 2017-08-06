# coding=utf-8
"""
a runnable for using cGeneralProfiler
"""


import os, sys, time, pickle
sys.path.append("../")
sys.path.append("./")
from mimircache import *
from mimircache.bin.conf import *

################################## Global variable and initialization ###################################

# TRACE_TYPE = "cloudphysics"
TRACE_TYPE = "msr"

TRACE_DIR, NUM_OF_THREADS = initConf(TRACE_TYPE, trace_format='variable')


block_unit_size = 16 * 1024

DEFAULT_PARAM_MIMIR_LRU = {"max_support": 4,
                 "min_support": 1,
                 "confidence": 0,
                 "item_set_size": 20,
                 "prefetch_list_size": 2,
                 "cache_type": "LRU",
                 "sequential_type": 0,
                 "max_metadata_size": 0.1,
                 "block_size": block_unit_size,
                    "block_unit_size": block_unit_size,
                 "sequential_K": 0,
                 "cycle_time": 2,
                 "AMP_pthreshold": 256
                }

DEFAULT_PARAM_MIMIR_FIFO = {"max_support": 4,
                 "min_support": 1,
                 "confidence": 0,
                 "item_set_size": 20,
                 "prefetch_list_size": 2,
                 "cache_type": "FIFO",
                 "sequential_type": 0,
                 "max_metadata_size": 0.1,
                 "block_size": block_unit_size,
                    "block_unit_size": block_unit_size,
                 "sequential_K": 0,
                 "cycle_time": 2,
                 "AMP_pthreshold": 256
                }


DEFAULT_PARAM_MIMIR_LFU = {"max_support": 4,
                 "min_support": 1,
                 "confidence": 0,
                 "item_set_size": 20,
                 "prefetch_list_size": 2,
                 "cache_type": "LFU",
                 "sequential_type": 0,
                 "max_metadata_size": 0.1,
                 "block_size": block_unit_size,
                    "block_unit_size": block_unit_size,
                 "sequential_K": 0,
                 "cycle_time": 2,
                 "AMP_pthreshold": 256
                }



DEFAULT_PARAM_MIMIR_AMP = {"max_support": 4,
                 "min_support": 1,
                 "confidence": 0,
                 "item_set_size": 20,
                 "prefetch_list_size": 2,
                 "cache_type": "AMP",
                 "sequential_type": 2,
                 "max_metadata_size": 0.1,
                 "block_size": block_unit_size,
                    "block_unit_size": block_unit_size,
                 "sequential_K": 0,
                 "cycle_time": 2,
                 "AMP_pthreshold": 256
                }

DEFAULT_PARAM_PG = {"lookahead": 20,
                    "cache_type": "LRU",
                    "max_metadata_size": 0.1,
                    "prefetch_threshold": 0.05,
                    "block_size": block_unit_size,
                    "block_unit_size": block_unit_size,
                    }

DEFAULT_PARAM_AMP = {"pthreshold": 256,
                    "K": 1,
                     "block_unit_size": block_unit_size
                     }

DEFAULT_PARAM_LRU_FIFO = {
                        "block_unit_size": block_unit_size,
                        }

########################################### main functions ##############################################

def run_profiler(dat, alg, cache_size, bin_size, cache_params, num_of_threads=NUM_OF_THREADS):
    print("{}: {}".format(alg, cache_params))

    if TRACE_TYPE == 'cloudphysics':
        reader = vscsiReader("{}/{}".format(TRACE_DIR, dat), disk_sector_size=512)
    elif TRACE_TYPE == "msr":
        reader = csvReader("{}/{}".format(TRACE_DIR, dat), data_type='l', disk_sector_size=1, # MSR
                               init_params={"label_column": 5, "real_time_column": 1, "size_column": 6})
    else:
        print("unknown type {}".format(TRACE_TYPE))
        return


    p = cGeneralProfiler(reader, alg, cache_size, bin_size,
                         cache_params=cache_params,
                         num_of_threads=num_of_threads)
    print(p.get_hit_rate())
    reader.close()



def run():
    # DATA = ["w94_vscsi1.vscsitrace", "w91_vscsi1.vscsitrace", "w89_vscsi2.vscsitrace"]
    DATA = ["proj_3.csv", "prxy_1.csv", "src1_2.csv"]
    cache_size = 64 * 1024 * 1024 // block_unit_size
    for dat in DATA:
        # run_profiler(dat, "FIFO", cache_size=cache_size, bin_size=cache_size,
        #              cache_params=DEFAULT_PARAM_LRU_FIFO, num_of_threads=1)
        run_profiler(dat, "LFUFast", cache_size=cache_size, bin_size=cache_size,
                     cache_params=DEFAULT_PARAM_LRU_FIFO, num_of_threads=1)
        # run_profiler(dat, "LFU", cache_size=cache_size, bin_size=cache_size,
        #              cache_params=DEFAULT_PARAM_LRU_FIFO, num_of_threads=1)
        # run_profiler(dat, "LRU", cache_size=cache_size, bin_size=cache_size,
        #              cache_params=DEFAULT_PARAM_LRU_FIFO, num_of_threads=1)
        # run_profiler(dat, "AMP", cache_size=cache_size, bin_size=cache_size,
        #              cache_params=DEFAULT_PARAM_AMP, num_of_threads=1)
        # run_profiler(dat, "PG", cache_size=cache_size, bin_size=cache_size,
        #              cache_params=DEFAULT_PARAM_PG, num_of_threads=1)
        # run_profiler(dat, "mimir", cache_size=cache_size, bin_size=cache_size,
        #              cache_params=DEFAULT_PARAM_MIMIR_FIFO, num_of_threads=1)
        run_profiler(dat, "mimir", cache_size=cache_size, bin_size=cache_size,
                     cache_params=DEFAULT_PARAM_MIMIR_LFU, num_of_threads=1)
        # run_profiler(dat, "mimir", cache_size=cache_size, bin_size=cache_size,
        #              cache_params=DEFAULT_PARAM_MIMIR_LRU, num_of_threads=1)
        # run_profiler(dat, "mimir", cache_size=cache_size, bin_size=cache_size,
        #              cache_params=DEFAULT_PARAM_MIMIR_AMP, num_of_threads=1)







if __name__ == "__main__":
    run()
