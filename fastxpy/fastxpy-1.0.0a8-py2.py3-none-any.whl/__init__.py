#import sys
#import re
#
#def qa(qora):
#    qora = qora.lower()
#    if qora == "a":
#        return ">"
#    elif qora == "q":
#        return "@"
#    else:
#        sys.exit("must be q or a, you put %s" % qora)
#
#def numseqs(file_name, qora):
#    header = qa(qora)
#    with open(file_name, "r") as f:
#        count = 0
#
#        for line in f:
#            if line.strip()[0] == ">":
#                count += 1
#
#    return count
#
#def headers(file_name, qora):
#    header = qa(qora)
#    with open(file_name, "r") as f:
#        headers = []
#
#        for line in f:
#            line = line.strip()
#
#            if line[0] == header:
#                headers.append(line)
#
#    return headers
#
#def detect(file_name):
#    with open(file_name, "r") as f:
#        first = f.readline().strip()
#
#        if first[0] == ">":
#            return "a"
#        elif first[0] == "@":
#            return "q"
#        else:
#            return None
#
#def getrange(file_name, start, stop, qora, regex=None, hold_style=True):
#    result = {}
#    all_heads = []
#    header = qa(qora)
#    broken = False
#    if stop < start:
#        sys.exit("start must be less than stop")
#
#    with open(file_name, "r") as f:
#        count = 0
#        seq = ""
#        curr_head = None
#        for line in f:
#            if line.strip()[0] == header:
#                if count > stop:
#                    broken = True
#                    break
#
#                if curr_head and count >= start:
#                    result[curr_head] = seq.strip()
#                    all_heads.append(curr_head)
#
#                count += 1
#                curr_head = line.strip()
#                if regex:
#                    curr_head = re.search(regex, curr_head).group(1)
#
#                seq = ""
#            else:
#                seq += line.strip()
#                if hold_style:
#                    seq += "\n"
#
#    if not broken:
#        result[curr_head] = seq.strip()
#        all_heads.append(curr_head)
#
#    return result, all_heads
