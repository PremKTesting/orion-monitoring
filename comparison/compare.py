# Copyright 2023, Metropolis Technologies, Inc.
import os
import json
import collections

import variables
from util import perc_to_float
from event_loader import create_eval_from_filepath, evaluation

def compare_eval_output(run_info: dict):
    """Wrapper to create evaluation object from specified files and perform comparison
    
    Parameters:
    run_info (dict): Dict containing all necessary filepaths
    
    Returns:
    void
    """
    eval_a = create_eval_from_filepath(run_info['input_a'])
    eval_b = create_eval_from_filepath(run_info['input_b'])

    compare(a=eval_a, b=eval_b, output_file=run_info["output_file"])

def compare(a: evaluation, b: evaluation, output_file: str):
    print("Comparison Criteria:")                    
    print("A: Orion v{} | Detection v{} {} | Recognition v{} {} | Suffix {}".format(
        a.orion_version, 
        a.detection_version, a.detection_precision,
        a.recognition_version,a.recognition_precision,
        a.suffix
    ))
    print("B: Orion v{} | Detection v{} {} | Recognition v{} {} | Suffix {}".format(
        b.orion_version, 
        b.detection_version, b.detection_precision,
        b.recognition_version,b.recognition_precision,
        b.suffix
    ))
        
    a_variety = list(a.summary_reports.keys())
    b_variety = list(b.summary_reports.keys())
    if not (a_variety == b_variety):
        exit("Test criteria mismatch:\nA:{}\nB:{}".format(a_variety, b_variety))
    
    a_evals = {}
    b_evals = {}
    output_dict = NestedDefaultDict()
    for variety in variables.default_tests:    # ee-b1, not_ee-b1, etc.
        variety_value = variables.default_tests[variety]
        for gt in variables.ground_truth_videos:
            for camera in a.summary_reports[variety_value][gt]:
                for comparison in variables.general_evaluation:
                    output_dict[variety_value][gt][camera]\
                        [variables.dashboard_ids.get(comparison, 'ERROR')] = \
                    compare_value(\
                    a = a.summary_reports[variety_value][gt][camera][comparison], \
                    b = b.summary_reports[variety_value][gt][camera][comparison])
                for comparison in variables.numerical_evaluation:
                    output_dict[variety_value][gt][camera]\
                        [variables.dashboard_ids.get(comparison, 'ERROR')] = \
                    compare_numerical(\
                    a = a.summary_reports[variety_value][gt][camera][comparison], \
                    b = b.summary_reports[variety_value][gt][camera][comparison])
    dashboard_output = convert_to_dashboard_format(output_dict)
    if (os.path.isfile(output_file)):
        print(f"WARNING: Output file {output_file} already exists.\
                \nWill be overwritten.")
        os.remove(output_file)
    with open(output_file, "w") as output: 
        json.dump(dashboard_output, output, ensure_ascii=False, indent=4)

def compare_value(a: int, b: int) -> dict:
    """Comparison for ints
    
    Parameters:
    a (dict): Input int for comparison criteria A
    b (dict): Input int for comparison criteria B
    
    Returns:
    dict: Output with values of values and winner of comparison
    """
    temp = {}
    if (a > b):
        winner = "A"
    elif (b > a):
        winner = "B"
    else: 
        winner = "Both"
    temp = {
        "A": {
            "Matching Rate": float(a)
        },
        "B": {
            "Matching Rate": float(b)
        },
        "Winner": winner
    }
    return temp

def compare_numerical(a: dict, b: dict) -> dict:
    """Comparison for numerical dict (ex. License plate, relative motion, etc.)
    
    Parameters:
    a (dict): Input dict for comparison criteria A
    b (dict): Input dict for comparison criteria B
    
    Returns:
    dict: Output with values of matching rate and winner of comparison
    """
    temp = {}
    if a["Num Matched"] > b["Num Matched"]:
        winner = "A"
    elif b["Num Matched"] > a["Num Matched"]:
        winner = "B"
    else:
        winner = "Both"
    temp = {
        "A" : {
            "Num Matched": a["Num Matched"],
            "Num Mismatched" : a["Num Mismatched"]
        },
        "B" : {
            "Num Matched": b["Num Matched"],
            "Num Mismatched" : b["Num Mismatched"]
        },
        "Winner": winner
    }
    if "Matching Rate -> APR" in a.keys():
        temp["A"]["Matching Rate"] = perc_to_float(a["Matching Rate -> APR"])
        temp["B"]["Matching Rate"] = perc_to_float(b["Matching Rate -> APR"])
    else:
        temp["A"]["Matching Rate"] = perc_to_float(a["Matching Rate"])
        temp["B"]["Matching Rate"] = perc_to_float(b["Matching Rate"])
    return temp

def convert_to_dashboard_format(input):
    new_dict = NestedDefaultDict()
    json_input =  json.loads(json.dumps(input))
    for gt in variables.ground_truth_videos:
        for criteria, criteria_value in json_input.items():
            for camera, camera_value in json_input[criteria][gt].items():
                for comparison, comparison_value in \
                    json_input[criteria][gt][camera].items():
                    new_dict[gt][comparison][criteria][camera] = \
                        json_input[criteria][gt][camera][comparison]
    return new_dict


class NestedDefaultDict(collections.defaultdict):
    def __init__(self, *args, **kwargs):
        super(NestedDefaultDict, self).__init__(NestedDefaultDict, *args, **kwargs)

    def __repr__(self):
        return repr(dict(self))