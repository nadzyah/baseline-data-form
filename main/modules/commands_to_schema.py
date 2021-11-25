#!/usr/bin/python3

import json
import yaml

def convert_dict_array(obj):
    """
    Convert yaml array to json dict (almost).

    Parameters and result
    ---------------------
    obj: python dict
    result: string in json format

    Example
    ------
    obj = {"FG-100F": ["show system interface"]}

    result = {"FG-100F": {"show system interface": ""}} 
    """
    result = {}
    for key, array in obj.items():
        result[key] = dict(zip(array, ["" for x in range(len(array))]))
    return str(result).replace("'", '"')


def commands_to_schema(commdict):
    """
    Convert log_commands to json-editor schema.

    Parameters and result
    ---------------------
    commdict: python dict
    result: string in json format

    Example
    -------
    commdict = {"FG-100F": {"show system interface": ""}}

    result =
      {"title": "Commands",
         "type": "object",
         "properties": {
           "FG-100F":{
             "type": "object",
             "properties": {
               "show system interface": {
                 "type": "string",
                 "format": "textarea"
                 }}}}}
    """
    result = {"title": "Commands", "type": "object", "properties": {}}
    for device_name, commands in commdict.items():
        result["properties"][device_name] = {"type": "object", "properties": {}}
        for command, output in commands.items():
            result["properties"][device_name]["properties"][command] = {"type": "string", 
                                                                        "format": "textarea",
                                                                        "default": output}
    return str(result).replace('"', r'\"').replace("'", '"')

if __name__ == '__main__':
    test = json.loads('{"FG-100F":["show system interface"],"FortiManager":["diag dvm device list","diag dvm adom list"]}')
    #print(commands_to_schema(json.loads(convert_dict_array(test))))
    a = """Device1:
  - command1
  - command1
Device2:
  - command1
  - command1
"""
    print(convert_dict_array(yaml.safe_load(a)))
    #print(commands_to_schema(json.loads(convert_dict_array(yaml.safe_load(a)))))

