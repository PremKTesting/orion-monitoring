# Copyright 2023, Metropolis Technologies, Inc.
import os
import re
import json
import variables

def create_eval_from_filepath(filepath: str):
    """Create evaluation object from file
    
    Parameters:
    filepath (str): filepath for input directory 
    
    Returns:
    evaluation: Output evaluation object
    """
    parts = filepath.split("/")
    criterias = []
    for part in parts:
        if ('_d' in part and '_o' in part):
            criterias.append(part)
    if len(criterias) > 1:
        exit("Invalid input directory name: {}".format(filepath))

    current_criteria = criterias[0]
    current_split = re.split(r'_|-',current_criteria)
    output = evaluation()
    output.filepath= filepath
    output.critera_name = criterias[0]
    output.recognition_version = current_split[0].replace('r','')
    output.detection_version = current_split[1].replace('d','')
    output.orion_version = current_split[2].replace('o','')
    if (len(current_split) > 3):
        output.suffix = current_split[3]
    jsons = create_evaluation_objects(  output.filepath,
                                recog_version=output.recognition_version,
                                det_version=output.detection_version,
                                orion_version=output.orion_version)
    output.detailed_reports = jsons["detailed"]
    output.summary_reports = jsons["summary"]
    return output

def create_evaluation_objects(  dirpath: str,
                                recog_version: str,
                                det_version: str,
                                orion_version: str):
    """Sub-function to create detailed and summary dicts in evaluation object
    
    Parameters:
    dirpath (str): Directory path for current object to be created\
    recog_version (str): Used to create criteria prefix
    det_version (str): Used to create criteria prefix
    orion_version (str): Used to create criteria prefix
    
    Returns:
    dict: Output with values of matching rate and winner of comparison
    """
    criteria_prefix = "o{}-d{}-r{}".format(orion_version,
                                           det_version,
                                           recog_version)
    detailed = {}
    summary = {}
    for folder in variables.default_tests.values():
        current_suffix = criteria_prefix + '-' + folder
        current_dir = os.path.join(dirpath, current_suffix)
        if not (os.path.exists(current_dir)):
            exit("Directory: {} does not exist.".format(current_dir))
        for output in variables.default_eval_outputs.values():
            jsons_filepath =  \
                os.path.join(current_dir, (current_suffix + '-' + output + '.json'))
            if not (os.path.isfile(jsons_filepath)):
                jsons_filepath = os.path.join(current_dir, \
                    (current_suffix + '-' + output + '.json'))
            if output == "detailed_prediction_analysis":
                with open(jsons_filepath, 'r') as file:
                    detailed[folder] = json.load(file)
                    file.close()
            if output == "prediction_summary":
                with open(jsons_filepath, 'r') as file:
                    summary[folder] = json.load(file)
                    file.close()
    jsons = {}
    jsons["detailed"] = detailed
    if (len(detailed) < len(variables.default_tests)):
        print("WARNING: # of etailed reports for {} \
              doesn't match expected # of tests.".format(criteria_prefix))
    if (len(summary) < len(variables.default_tests)):
        print("WARNING: # of summary reports for {} \
              doesn't match expected # of tests.".format(criteria_prefix))
    jsons["summary"] = summary
    return jsons


class evaluation:
    def __init__(self):
        self.critera_name = ""
        self.filepath = ""
        self.detection_version = ""
        self.detection_precision = "fp16"
        self.recognition_version = ""
        self.recognition_precision = "fp16"
        self.orion_version = ""
        self.suffix = ""
        self.detailed_reports = {}
        self.summary_reports = {}

class report:
    def __init__(self):
        self.criteria = ""
        self.filepath = ""
        self.report = {}