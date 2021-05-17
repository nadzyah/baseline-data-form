#!/usr/bin/python3

import json
import yaml

def convert_dict_array(obj: dict):
    """
    Convert yaml array to json dict (almost). Example:
    Original:
      {
        "FG-100F": [
          "show system interface"
        ]
      }
    Result:
      {
        "FG-100F": {
          "show system interface": ""
        }
      }
    """
    result = {}
    for key, array in obj.items():
        result[key] = {}
        for x in array:
            result[key][x] = ""
    return result


def commands_to_schema(logdict: dict):
    """
    Convert log_commands to json-editor schema. Example:
    Original:
      {
        "FG-100F": {
          "show system interface": ""
        }
      }
    Result:
      {
        "title": "Logs",
        "type": "object",
        "properties": {
          "FG-100F":{
            "type": "object",
            "properties": {
              "show system interface": {
                "type": "string",
                "format": "textarea"
              }
            }
          }
        }
      }
    """
    result = {"title": "Logs", "type": "object", "properties": {}}
    for device_name, commands in logdict.items():
        result["properties"][device_name] = {"type": "object", "properties": {}}
        for command, output in commands.items():
            result["properties"][device_name]["properties"][command] = {"type": "string", 
                                                                        "format": "textarea",
                                                                        "default": output}
    result_str = str(result).replace('"', r'\"')
    return result_str.replace("'", '"')

if __name__ == '__main__':
    test = json.loads('{"FG-100F":["show system interface"],"FortiManager":["diag dvm device list","diag dvm adom list"]}')
    print(commands_to_schema(convert_dict_array(test)))
