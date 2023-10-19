# Copyright 2023, Metropolis Technologies, Inc.
# USAGE: python3 ab_comparison.py 
#                   -a <a_report_directory> 
#                   -b <b_report_directory>
#                   -o <output_file>
#
# EXAMPLE: python3 ab_comparison.py 
#                   -a '/home/user/r201_d130_o540'
#                   -b '/home/user/r201_d130_o550'
#                   -o '/home/user/output.json'

import os 
import argparse

from validation import validate_inputs
from compare import compare_eval_output

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a',
                        type=str,
                        help='"A" Output Report Directory',
                        required=True)
    parser.add_argument('-b',
                        type=str,
                        help='"B" Output Report Directory',
                        required=True)
    parser.add_argument('-o',
                        type=str,
                        help='Comparison report file output',
                        required=True)
    
    args = parser.parse_args()

    run_info = {
        "input_a": args.a,
        "input_b": args.b,
        "output_file": args.o
    }
    validate_inputs(run_info=run_info)
    compare_eval_output(run_info = run_info)