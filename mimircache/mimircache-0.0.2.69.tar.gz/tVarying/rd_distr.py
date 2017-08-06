# coding=utf-8

import os, sys, time
from mimircache import *


def rd_distribution_plots(dataloc, output="1104"):
    c = cachecow()
    # c.csv("/scratch/jason/wiki.part.csv.sort.test", init_params={"label_column": 3, "real_time_column":2})
    # c.heatmap('r', 2, "rd_distribution", num_of_threads=6)

    fns = reversed(sorted(os.listdir(dataloc)))
    fns = ["w100_vscsi1.vscsitrace"]
    for fn in fns:
        fig_name = fn + "_frd_dist.png"
        if os.path.exists(output+"/"+fig_name):
            # continue
            pass
        if not fn.endswith("vscsitrace") and not fn.endswith("vscsi"):
            continue
        c.vscsi("{}/{}".format(dataloc, fn))
        # c.heatmap('r', 10000000, "hit_rate_start_time_end_time", cache_size=2000, num_of_threads=6)
        # c.heatmap('r', 1000000000, "rd_distribution", num_of_threads=6, figname = output+"/"+ fn + "_rd_dist.png")
        # c.heatmap('r', 1000000000, "future_rd_distribution", num_of_threads=6, figname = output+"/"+ fn + "_frd_dist.png")


        c.heatmap('v', 10000, "rd_distribution", num_of_threads=6, figname=output + "/" + fn + "_rd_dist2.png")
        # c.heatmap('v', 10000, "future_rd_distribution", num_of_threads=6, figname=output + "/" + fn + "_frd_dist.png")



if __name__ == "__main__":
    # rd_distribution_plots("../mimircache/data/", output="./")
    rd_distribution_plots("../mimircache/data/traces", output="./")