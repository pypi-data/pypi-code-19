# coding=utf-8


from mimircache import *



def cal_cold_miss(dat, type):
    """
    calculate the cold miss for a trace, this is different from using 
    number of uniq lbns / number of lbn, because when size is considered, 
    the cold miss can be smaller as new request hit on part of the large chunk of 
    previous requests 
    :param dat: 
    :param type: 
    :return: 
    """
    print(dat)
    TRACE_DIR_CPHY = "/home/cloudphysics/traces/"
    TRACE_DIR_MSR = "/home/jason/ALL_DATA/MSR/MSR-Cambridge/"
    BLOCK_UNIT_SIZE = 16 * 1024
    d = set()
    uniq = 0
    n_all = 0
    if type == "cphy":
        reader = vscsiReader("{}/{}".format(TRACE_DIR_CPHY, dat),
                             disk_sector_size=512,
                             block_unit_size=BLOCK_UNIT_SIZE)
        n_all = reader.get_num_total_req()
        r = reader.read_one_request_full_info() # time, lbn, size
        while r:
            time = r[0]
            lbn = r[1]
            size = r[2]
            if lbn not in d:
                uniq += 1
            d.add(lbn)
            n = int(math.ceil(size//BLOCK_UNIT_SIZE))
            for i in range(n-1):
                d.add(lbn + 1 + i)
            r = reader.read_one_request_full_info()
        reader.close()
        return n_all, uniq

    elif type == "msr":
        # reader = csvReader("{}/{}".format(TRACE_DIR_MSR, dat), data_type='l',
        #                    disk_sector_size=1, block_unit_size=16 * 1024,
        #                    init_params={"label_column": 5, "real_time_column": 1, "size_column": 6})
        with open("{}/{}".format(TRACE_DIR_MSR, dat)) as ifile:
            for line in ifile:
                line = line.split(",")
                n_all += 1
                time = int(line[0])
                lbn = int(line[4]) // BLOCK_UNIT_SIZE
                size = int(line[5])
                if lbn not in d:
                    uniq += 1
                d.add(lbn)
                n = int(math.ceil(size // BLOCK_UNIT_SIZE))
                for i in range(n - 1):
                    d.add(lbn + 1 + i)
        return n_all, uniq

    else:
        print("unknown type {}".format(type))
        return



def cal_all_cold_miss():
    """
    calculate the cold miss considering size for all cphy and msr traces 
    :return: 
    """
    import pickle
    d = {}

    TRACE_DIR_CPHY = "/home/cloudphysics/traces/"
    TRACE_DIR_MSR = "/home/jason/ALL_DATA/MSR/MSR-Cambridge/"
    # for i in range(106, 0, -1):
    #     if i < 10:
    #         i = "0{}".format(i)
    #     if os.path.exists("{}/w{}_vscsi{}.vscsitrace".format(TRACE_DIR_CPHY, i, 1)):
    #         dat = "w{}_vscsi1.vscsitrace".format(i)
    #     elif os.path.exists("{}/w{}_vscsi{}.vscsitrace".format(TRACE_DIR_CPHY, i, 2)):
    #         dat = "w{}_vscsi2.vscsitrace".format(i)
    #     else:
    #         print("unknown vscsi type: {}".format(i))
    #     try:
    #         n, nu = cal_cold_miss(dat, "cphy")
    #         d[dat] = (n, nu)
    #         print("{}: {} {}".format(dat, n, nu))
    #     except Exception as e:
    #         print(e)

    with open("nUniq.pickle", 'rb') as ifile:
        d = pickle.load(ifile)

    for f in os.listdir(TRACE_DIR_MSR):
        if 'csv' not in f:
            continue
        try:
            n, nu = cal_cold_miss(f, 'msr')
            dat = f[:-4]
            d[dat] = (n, nu)
            print("{}: {} {}".format(f, n, nu))
        except Exception as e:
            print(e)

    with open("nUniq.pickle", 'wb') as ofile:
        pickle.dump(d, ofile)


if __name__ == "__main__":
    # run1()
    cal_all_cold_miss()
    # print(cal_cold_miss("w79_vscsi1.vscsitrace", type='cphy'))
    # run3(128, t1=0.2, t2=0.01)

