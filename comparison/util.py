# Copyright 2023, Metropolis Technologies, Inc.

def perc_to_float(input: str, leave_val_alone: bool = True):
    if leave_val_alone:
        return round(float(input.strip('%')), 2)
    return round(float(input.strip('%')) / 100.0, 2)