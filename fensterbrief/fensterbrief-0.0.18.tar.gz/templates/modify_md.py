import markdown
import yaml
import re

def copy_and_adjust_md(src_file,  dst_file, replace_data={}):

    META_RE = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')
    META_MORE_RE = re.compile(r'^[ ]{4,}(?P<value>.*)')
    END_RE = re.compile(r'^(-{3}|\.{3})(\s.*)?')

    meta = {}
    just_copy_line = False
    key = None
    
    with open(src_file) as fin:
        with open(dst_file, 'w') as fout:
            
            for line in fin.readlines():

                if just_copy_line:
                    fout.write(line)
                else:
                    
                    m1 = META_RE.match(line)
                    if m1:

                        key = m1.group('key').lower().strip()
                        value = m1.group('value').strip()

                        if key in meta:
                            meta[key].append(value)
                        else:
                            meta[key] = [value]

                            
                    elif END_RE.match(line) and key != None:
                        
                        just_copy_line = True
                        #print(replace_data)
                        #print(meta)
                        
                        # replace data
                        for k in replace_data:
                            if k in meta:
                                meta[k] = replace_data[k]
                             
                        # dump yaml data
                        for k in meta:
                            if isinstance(meta[k], list):
                                if len(meta[k]) == 1:
                                    fout.write("%s: %s\n" % (k, meta[k][0]))
                                else:
                                    fout.write("%s:\n" % k)                             
                                    for l in meta[k]:
                                        fout.write("    %s\n" % l)
                            else:
                                fout.write("%s: %s\n" % (k, meta[k]))

                        fout.write(line)

                    elif META_MORE_RE.match(line):
                        m2 = META_MORE_RE.match(line)
                        if m2 and key:
                         
                            # Add another line to existing key
                            meta[key].append(m2.group('value').strip())
                         
                    else:
                        fout.write(line)



                 
copy_and_adjust_md('template-pandoc.md', 'x.txt', {'subject' : 'fooooo',
                                                   'to' : ['tante erna', 'gartenstr. 23', 'berlin'] } )
