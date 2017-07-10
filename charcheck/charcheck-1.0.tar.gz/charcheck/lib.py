import xmltodict

def get_dict(filename):
    file_data = open(filename, 'rb')
    data_dict = xmltodict.parse(file_data.read().decode('utf-8'))
    data_dict = {i['@name']:i['#text'] for i in data_dict['resources']['string']}
    return data_dict

def compare(src_dict, target_dict):
    output_list = []
    for i in target_dict.keys():
        if i in src_dict.keys():
            if '\n' in src_dict[i] or '\\n' in src_dict[i]:
                if ('\n' in target_dict[i] or '\\n' in target_dict[i]) and target_dict[i].count('\\n')+target_dict[i].count('\n') == src_dict[i].count('\\n')+src_dict[i].count('\n'):
                    output_list.append(i+" Value status = Correct contains '\\n'\n")
                else:
                    output_list.append(i+" Value Status = Incorrect contains '\\n'\n")
            if '%s' in src_dict[i]:
                if '%s' in target_dict[i] and target_dict[i].count('%s') == src_dict[i].count('%s'):
                    output_list.append(i+" Value status = Correct contains '%s'\n")
                else:
                    output_list.append(i+" Value Status = Incorrect contains '%s'\n")
            else:
                output_list.append(i+" Value Status = Doesn't contain '\\n' or '%s'\n")
        else:
            output_list.append(i+" Value Status = Not Found")
    return output_list

def process(source_file, target_file, output_file='out.txt'):
    compare_output = compare(get_dict(source_file), get_dict(target_file))
    o_file = open(output_file, 'w')
    o_file.writelines(compare_output)
    print("Comaprison complete output in '"+output_file+"'")