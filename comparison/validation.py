# Copyright 2023, Metropolis Technologies, Inc.
import os


def validate_inputs(run_info: dict):
    """Validate if input directories exist for A & B, else exit program.
    
    Parameters:
    run_info (dict): Dict containing all necessary dirpaths
    
    Returns:
    void
    """
    validOut = True
    if not os.path.isdir(run_info['input_a']):
        print("Input A: %s is not a valid directory." % run_info['input_a'])
        validOut = False
    if not os.path.isdir(run_info['input_b']):
        print("Input B: %s is not a valid directory." % run_info['input_b'])
        validOut = False
    if (validOut == False):
        exit('Program has exited: Invalid Arguments')