#!/usr/bin/python3

import yaml, json
from random import randint

def yaml_comments(yamldata):
    """
    Establish a correspondence between
        1) label and its name (one-to-one relationship)
        2) label and format (one-to-one relationship)
    
    The information about name and format must be specified as comment
    the next way (without first space):
        #[name][format]
    or in case you don't want to specify label's name
        #[][format]
    or in case you a label doesn't have explicit format
        #[name]
    
    If you want to use multi-line comment, end each line with ## symbol,
    excluding the last one:
        label: value  #[Lorem ipsum dolor ##
                 #sit amet consectetur##
                 # adipiscing][format]
    
    Do NOT break format field as it is shown in the next examples:
        #[comment]##
        #[format]
    or
        #[comment][for##
        # mat]

    Parameters and result
    ---------------------
    yamldata: string in yaml format
    result: python list with two string in json format, python dict
        and new yamldata that contain
        - { label: substituion }
        - { label: format }
        - { unique_label: original label}
        - changed_yamldata -- original yamldata string where non-uniwue labels are replaces
              with the original one (using random integers)

    Example
    -------
    yamldata = 
        UTM:  #[Local FortiGate][]
          interfaces:  #[Интерфейсы #
                       # other text][]
            - ip_mask: 172.16.25.10/24  #[IP адрес/Маска][ipmask]
              gw: 172.16.25.1  #[Шлюз][ip]
            - ip_mask: 0.0.0.0/0
              gw: 0.0.0.0

    result =
        [
            '{
                 "UTM": "Local FortiGate",
                 "interfaces": "Интерфейсы # other text",
                 "ip_mask": "IP адрес/Маска",
                 "gw": "Шлюз"
             }',
            '{
                 "ip_mask": "ipmask",
                 "gw": "ip"
             }'
        ]
    """
    changed_yamldata = yamldata
    result = [{}, {}, {}]
    lines = yamldata.splitlines();
    was_multiline = 0
    for line in yamldata.splitlines():
        name_start = line.find("#") + 1
        if name_start != 0:
            # Find the label itself
            # For multi-line name it's in the first line
            if not was_multiline:
                words = line.split()
                # Remove last : in labels
                orig_label = words[1][:-1] if words[0] == '-' else words[0][:-1]
                unique_label = orig_label + str(randint(0, 10000))
                result[2][unique_label] = orig_label

                # Replace original label with the unique one
                lineindex = yamldata.find(line)
                newline = line.replace(orig_label + ":", unique_label + ":")
                changed_yamldata = changed_yamldata.replace(line, newline)
            # Find the next # if name is multiline
            multiline_ind = line[name_start:].find('##')
            # If name is in one line
            if multiline_ind == -1:
                name_end = line.find(']')
                # Get the name text
                if not was_multiline:
                    name = line[name_start+1:name_end]
                else:
                    name += line[name_start:name_end]
                # Add name if it's not empty
                if name != '':
                    result[0][unique_label] = name
                if was_multiline:   # Clear flag
                    was_multiline = 0
                name = ''   # Clear name
                # Find the label's format
                format_ = line[name_end+2:-1]
                # Add format if it's specified
                if format_ != '':
                    result[1][unique_label] = format_
            else:
                # Count number of lines in multi-line name
                if not was_multiline:
                    name = line[name_start+1:]
                else:
                    name += line[name_start:]
                was_multiline = 1
    # Convert dicts to strings
    result[0] = json.dumps(result[0], sort_keys=False)
    result[1] = json.dumps(result[1], sort_keys=False)
    result.append(changed_yamldata)

    return result

def set_comments_back(yamlstr, names_formats_orig): 
    """
    Set comments back to yaml string

    Parameters and result
    ---------------------
    yamlstr: string in yaml format
    names_formats: array with three dictionaries in the next formats:
                          1) {'label': 'name'}
                          2) {'label': 'format')
                          3) {'unique_label' : 'orig_label'}
    result: string in yaml format

    Example
    -------
    yamlstr = 
        UTM1:
          mgmt_iface:
            ip_mask: 172.16.25.10/24
            gw: 172.16.25.1

    comments_formats = 
        [{"UTM": "Local #FortiGate","mgmt_iface": "MGMT Интерфейс","gw": "Шлюз"},
         {"ip_mask": "ipmask","gw": "ip"}]

    result = 
        UTM1:  #[Local ##
               #FortiGate][]
          mgmt_iface:   #[MGMT Интерфейс][]
            ip_mask: 172.16.25.10/24  #[][ipmask]
            gw: 172.16.25.1  #[Шлюз][ip]
    """
    result = yamlstr
    names, formats, unique_orig = (names_formats_orig[0], names_formats_orig[1], names_formats_orig[2])
    # Merge two dicts
    merged = {**names, **formats}
    for label in list(merged.keys()):
        indent = (len(label) + 7)*' '
        # If label is a positive number in quotes, replace quotes with single quotes
        # as yaml loader does
        if label[1:-1].isdigit() or label[1:-1].replace(".", "", 1).isdigit():
            merged["'" + label[1:-1] + "'"] = merged.pop(label)
            names["'" + label[1:-1] + "'"] = names.pop(label)
            formats["'" + label[1:-1] + "'"] = formats.pop(label)
            label = "'" + label[1:-1] + "'"

        if label in names and label in formats:
            # Create comment for label that contains name and format
            # of the label in specified format
            merged[label] = ("#[" + names[label].replace('##', '##\n' 
                                                        + indent + "#")
                            + "]" + "[" + formats[label] + "]")
        elif label in names:
            merged[label] = ("#[" + names[label].replace('##', '##\n'
                                                        + indent + '#') 
                            + "][]")
        else:  # label is in formats
            merged[label] = "#[][" + formats[label] + "]"

    # Add comment to yaml-data string
    for label, comment in merged.items():
        first_time = True
        for line in yamlstr.splitlines():
            # find the index of label in the line
            label_startind = line.find(label+":")
            # if label exists in this line
            if label_startind != -1 and first_time:
                first_time = False
                newline = line.replace(label, unique_orig[label])
                result = result.replace(line, newline + "    " + comment)
                break
    return result


if __name__ == "__main__":
    testnocomms = """trusthost:
  - ip: 10.0.0.0/8    #[one][ipmask]
  - ip: 172.16.0.0/12    #[one dot one][ipmask]
something else:
  ip: another one
"""
    result_after_yamlcomms = yaml_comments(testnocomms)
    for x in result_after_yamlcomms:
        print(x)
    
    result_after_setcomms = set_comments_back(yaml.dump(yaml.safe_load(result_after_yamlcomms[3]), 
                                                        sort_keys=False),
                                [json.loads(result_after_yamlcomms[0]),
                                 json.loads(result_after_yamlcomms[1]),
                                 result_after_yamlcomms[2]])
    print(result_after_setcomms)




