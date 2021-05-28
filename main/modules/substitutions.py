#!/usr/bin/python3

import yaml, json

def yaml_comments(yamlobj):
    """
    Establish a correspondence between
        1) label and its name
        2) label and format
    
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
    yamlobj: string in yaml format
    result: python list with two string in json format

    Example
    -------
    yamlobj = 
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
    result = [{}, {}]
    lines = yamlobj.splitlines();
    was_multiline = 0
    for line in yamlobj.splitlines():
        name_start = line.find("#") + 1
        if name_start != 0:
            # Find the label itself
            # For multi-line name it's in the first line
            if not was_multiline:
                words = line.split()
                # Remove last : in labels
                label = words[1][:-1] if words[0] == '-' else words[0][:-1]
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
                    result[0][label] = name
                if was_multiline:   # Clear flag
                    was_multiline = 0
                name = ''   # Clear name
                # Find the label's format
                format_ = line[name_end+2:-1]
                # Add format if it's specified
                if format_ != '':
                    result[1][label] = format_
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

    return result

def set_comments_back(yamlstr, names_formats): 
    """
    Set comments back to yaml string

    Parameters and result
    ---------------------
    yamlstr: string in yaml format
    names_formats: array with two dictionaries in the next formats:
                          1) {'label': 'name'}
                          2) {'label': 'format')
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
    names, formats = (names_formats[0], names_formats[1])
    # Merge two dicts
    merged = {**names, **formats}
    for label, value in merged.items():
        indent = (len(label) + 7)*' '
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
            label_startind = line.find(label+":")
            if label_startind != -1 and first_time:
                first_time = False
                result = result.replace(line, line + "    " + comment)
                break
    return result


if __name__ == "__main__":
    test = """mgmt:
  accounts:
    radius:
      ip: 10.254.12.211 #[][ipaddr]
      name: Velcom_ACS
    local:
      - username: admin
        password: nTram299
  trusthost:
    '1': 10.0.0.0/8 #[][ipmask]
    '2': 172.16.0.0/12 #[][ipmask]
"""
    comms = yaml_comments(test)
    testnocomms = yaml.dump(yaml.safe_load(test))
    
    print("Comments:", comms,
          "Without comms:", testnocomms,
          "Set comments back:", set_comments_back(testnocomms, list(map(json.loads, comms))),
          sep='\n')
