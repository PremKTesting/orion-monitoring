# Copyright 2023, Metropolis Technologies, Inc.
import os
import argparse
from generate_pdf import Pdf
from compare import Compare
from load_events import LoadEvents


def run_analysis(run_info: dict, data_loader: LoadEvents):
    comparator = Compare(filename=run_info["ground_truth_file"],
                         output_dir=run_info["output_dir"],
                         gt=data_loader.gts,
                         predictions=data_loader.preds,
                         criteria_name=run_info["criteria_name"])
    comparator.compare(is_validate_attr=run_info["validate_attribute"])


def load_data(run_info: dict):
    data_loader = LoadEvents(gt_file=run_info["ground_truth_file"],
                             orion_data_dir=run_info["orion_data_dir"])
    data_loader.load_gt()
    data_loader.gts.write_json(output_dir=run_info["output_dir"])
    data_loader.load_events(is_final_event=False)
    data_loader.load_log_dirs()
    data_loader.preds.write_json(output_dir=run_info["output_dir"],
                                 criteria_name=run_info["criteria_name"])
    return data_loader


def find_analysis_configs(search_dir, gt_dir, out_dir):
    filepaths = os.listdir(search_dir)
    criterias = []

    for filepath in filepaths:
        temp_filepath = os.path.join(search_dir, filepath)
        if not os.path.isdir(temp_filepath):
            continue
        if not filepath.endswith("mp4"):
            continue
        parts = filepath.split(".")
        criteria_str = parts[0]
        criteria_parts = criteria_str.split("_")

        ee = criteria_parts[4]
        index = 6
        ee_str = "not_ee"
        if ee == "ee":
            index += 1
            ee_str = "ee"

        gt_filename = f"gt_{criteria_parts[index]}-{criteria_parts[index + 1]}"
        gt_file_path = os.path.join(gt_dir, gt_filename)
        out_key = f"{criteria_parts[2]}-{criteria_parts[1]}-{criteria_parts[0]}-" \
                  f"{ee_str}-{criteria_parts[3]}"

        criteria = {
            "recognition_model_version": criteria_parts[0],
            "detection_model_version": criteria_parts[1],
            "orion_version": criteria_parts[2],
            "batch_2": criteria_parts[3] == "b2",
            "site_id": criteria_parts[index],
            "early_export": index == 7,
            "video_file_suffix": criteria_parts[index+1],
            "ground_truth_file": gt_file_path,
            "orion_data_dir": temp_filepath,
            "output_dir": os.path.join(out_dir, out_key),
            "criteria_name": (out_key)
        }

        criterias.append(criteria)

    return criterias


if __name__ == "__main__":
    default_output_path = os.path.join(os.getcwd(), "new_evaluated")

    parser = argparse.ArgumentParser()
    parser.add_argument('-t',
                        type=str,
                        help='Testing title',
                        required=True)
    parser.add_argument('-i',
                        type=str,
                        help='Orion data directory',
                        required=True)
    parser.add_argument('-g',
                        type=str,
                        help='Ground Truth directory',
                        required=True)
    parser.add_argument('-o',
                        type=str,
                        help='Output directory to store the result',
                        required=False,
                        default=default_output_path)
    parser.add_argument('-a',
                        action="store_true",
                        help='Validate Attributes POSE and TYPE of vehicle')

    args = parser.parse_args()

    run_info = {
        "title": args.t,
        "validate_attribute": args.a,
        "orion_ab_testing_data_dir": args.i,
    }
    if not os.path.exists(args.o):
        os.mkdir(args.o)

    criterias = find_analysis_configs(args.i, args.g, args.o)

    for criteria in criterias:
        run_info.update(criteria)
        output_dir = run_info["output_dir"]
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        data_loader = load_data(run_info)
        run_analysis(run_info, data_loader)