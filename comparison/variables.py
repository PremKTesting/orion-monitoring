# Copyright 2023, Metropolis Technologies, Inc.

default_tests = {
    "Early Export B1": "ee-b1",
    "Non-Early Export B1": "not_ee-b1",
    "Early Export B2": "ee-b2",
    "Non-Early Export B2": "not_ee-b2"
}

default_eval_outputs = {
    "Detailed Report": "detailed_prediction_analysis",
    "Summary Report": "prediction_summary"
}

general_evaluation = [
    'Number of event identified',
    'Number of valid events (uploaded)'
]
numerical_evaluation = [
    'License Plate',
    'Pose',
    'Type',
    'State',
    'Relative Motion'
]
eval_elements = {
    'Number of event identified': 0,
    'Number of valid events (uploaded)': 0,
    'License Plate': {},
    'Pose': {},
    'Type': {},
    'State': {},
    'Relative Motion': {}
}

dashboard_ids = {
    'Number of event identified': 'Number-of-identified-events',
    'Number of valid events (uploaded)': 'Number-of-uploaded-valid-events',
    'License Plate': 'License-Plate',
    'Pose': 'Pose',
    'Type': 'Type',
    'State': 'State',
    'Relative Motion': 'Relative-Motion'
}

ground_truth_videos = [
    'gt_1-approaching',
    'gt_1-cross-traffic',
    'gt_1-high-light',
    'gt_1-low-light',
    'gt_771-entry-2022-02-02',
    'gt_771-exit-2022-02-02',
    'gt_846-entry-2022-02-25',
    'gt_846-exit-2022-02-24'
]