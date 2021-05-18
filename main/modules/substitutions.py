#!/usr/bin/python3

import yaml, json

def yaml_comments(yamlobj):
    """
    Establish a correspondence between yaml comment and label
    
    Parameters and result
    ---------------------
    yamlobj: string in yaml syntax
    result: string in json format

    Example
    -------
    yamlobj = 
        UTM:  #Local FortiGate
          interfaces:  #Интерфейсы
            - ip_mask: 172.16.25.10/24  #IP адрес/Маска
              gw: 172.16.25.1  #Шлюз
            - ip_mask: 0.0.0.0/0
              gw: 0.0.0.0

    result =
        {
          "UTM": "Local FortiGate",
          "interfaces": "Интерфейсы",
          "ip_mask": "ip_mask",
          "gw": "Шлюз",
        }
    """
    result = {}

    for line in yamlobj.splitlines():
        comment_startind = line.find("#")
        if comment_startind != -1:
            comment = line[comment_startind+1:]
            words = line.split()
            # Remove last : in labels
            label = words[1][:-1] if words[0] == '-' else words[0][:-1]
            result[label] = comment

    return str(result).replace('"', r'\"').replace("'", '"')

def set_comments_back(yamlstr, labels_comments): 
    """
    Set comments back to yaml string

    Parameters and result
    ---------------------
    yamlstr: string in yaml format
    labels_comments: one-dimention dictionary 
    result: string in yaml format

    Example
    -------
    yamlstr = 
        UTM1:
          mgmt_iface:
            ip_mask: 172.16.25.10/24
            gw: 172.16.25.1

    labels_comments = {"UTM": "Local FortiGate", "ip_mask": "IP адрес/Маска", "gw": "Шлюз"}

    result = 
        UTM1:  #Local FortiGate
          mgmt_iface:
            ip_mask: 172.16.25.10/24  #IP адрес/Маска
            gw: 172.16.25.1  #Шлюз
    """
    result = yamlstr
    
    for label, comment in labels_comments.items():
        first_time = True
        for line in yamlstr.splitlines():
            label_startind = line.find(label)
            if label_startind != -1 and first_time:
                first_time = False
                result = result.replace(line, line + "    #" + comment)
                break
    return result


if __name__ == "__main__":
    test = """UTM:  #Local FortiGate
 - ip_mask: 172.16.25.10/24  #IP адрес/Маска
   gw: 172.16.25.1  #Шлюз
 - ip_mask: 0.0.0.0/0
   gw: 0.0.0.0
"""
    #print(yaml_comments(test))
    test2 = """UTM1:
  mgmt_iface:
    address_mask: 172.16.25.10/24
    gw: 172.16.25.1
FMG-VM64:
  interfaces:
  - ip: 172.16.25.22
    network: 172.16.25.1
  - ip: 172.16.25.22
    network: 172.16.25.1
global:
  syslog: 0.0.0.0
  ntp: ""
  dns1: 0.0.0.0
"""
    print(set_comments_back(test2, {"UTM1": " FortiGate-100F", "mgmt_iface": " MGMT интерфейс", "address_mask": " IP адрес/маска", "global": "Общесетевые сервисы"}))
