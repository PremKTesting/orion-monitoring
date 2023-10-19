import collections
import json
from typing import List
import os
from datetime import datetime
import pandas as pd
import numpy as np

from model import (GroundTruthData,
                   Data,
                   PredictionData,
                   ComparisonResult,
                   ComparisonResultCategory)
date_format = '%Y-%m-%d_%H-%M-%S.%f'


class Compare:
    def __init__(self,
                 filename: str,
                 output_dir: str,
                 gt: GroundTruthData,
                 predictions: PredictionData,
                 criteria_name: str):
        # dict contain lic_num, veh_pose, veh_type, lic_state
        self.filename: str = filename.split("/")[-1]
        self.output_dir: str = output_dir
        self.gt: GroundTruthData = gt
        self.predictions: PredictionData = predictions
        self.criteria_name: str = criteria_name

        self.valid_uploads: dict = collections.defaultdict(list)
        self.invalid_uploads: dict = collections.defaultdict(list)
        self.find_valid_events()

        self.relative_motion: ComparisonResult = \
            ComparisonResult("Relative Motion")
        self.pose: ComparisonResult = \
            ComparisonResult("Vehicle Pose")
        self.type: ComparisonResult = \
            ComparisonResult("Vehicle Type")
        self.state: ComparisonResult = \
            ComparisonResult("License Plate State")
        self.scenario: ComparisonResultCategory = \
            ComparisonResultCategory("Video Scenario")
        self.position_match: ComparisonResult = \
            ComparisonResult("License Plate Number")

        self.extra_prediction = collections.defaultdict(list)
        self.event_times = collections.defaultdict(list)

    def find_valid_events(self):
        for camera, preds in self.predictions.events.items():
            for pred in preds:
                if pred.is_valid_upload:
                    self.valid_uploads[camera].append(pred)
                else:
                    self.invalid_uploads[camera].append(pred)

    def fuzzy_matching_lic_plate(self, gt_lic_plate: str,
                                 pred_lic_plate: str):
        if gt_lic_plate == pred_lic_plate:
            return True

        if len(gt_lic_plate) != len(pred_lic_plate):
            return False

        gt_lic_plate = gt_lic_plate.replace("O", "0")
        pred_lic_plate = pred_lic_plate.replace("O", "0")

        if gt_lic_plate == pred_lic_plate:
            return True

        return False

    def compare_per_camera(self, gt: Data, gt_pos: int,
                           predictions: List[Data],
                           curr_pred_indexes: List[int],
                           last_pred_pos_matched: int = -1):
        matched_data = {
            "is_lic_matched": False,
            "is_type_matched": False,
            "is_state_matched": False,
            "is_pose_matched": False,
            "is_rel_motion_matched": False,
            "pred_pos": -1,
            "pred_event": None,
            "gt_pos": gt_pos,
            "gt": gt
        }

        for i, pred in enumerate(predictions):
            if i in curr_pred_indexes:
                continue

            is_lic_matched = self.fuzzy_matching_lic_plate(gt.lic_plate,
                                                           pred.lic_plate)
            if is_lic_matched:
                matched_data["is_lic_matched"] = is_lic_matched
                matched_data["is_type_matched"] = gt.type == pred.type
                matched_data["is_pose_matched"] = gt.pose == pred.pose
                matched_data["is_state_matched"] = gt.state == pred.state
                is_rel_motion_matched = gt.relative_motion == pred.relative_motion
                matched_data["is_rel_motion_matched"] = is_rel_motion_matched
                matched_data["pred_pos"] = i
                matched_data["pred"] = pred
                curr_pred_indexes.append(i)

                break

        return matched_data

    def accumulate(self, matched_data, delta_pos, is_validate_attr):
        is_lic_matched = matched_data.get("is_lic_matched", False)
        is_type_matched = matched_data.get("is_type_matched", False)
        is_pose_matched = matched_data.get("is_pose_matched", False)
        is_state_matched = matched_data.get("is_state_matched", False)
        is_rel_motion_matched = matched_data.get("is_rel_motion_matched", False)
        event_time = matched_data.get("event_time")
        pred_pos = matched_data.get("pred_pos", -1)
        pred = matched_data.get("pred", Data({}))
        gt_pos = matched_data.get("gt_pos", -1)
        gt = matched_data.get("gt", Data(""))

        is_pos_matched = False
        if is_lic_matched:
            is_pos_matched = (gt_pos + delta_pos) == pred_pos
            if not is_pos_matched:
                delta_pos = (pred_pos - gt_pos)
                is_pos_matched = (gt_pos + delta_pos) == pred_pos
        self.position_match.add({"gt_pos": gt_pos,
                                 "pred_pos": pred_pos,
                                 "gt": gt.__dict__(),
                                 "pred": pred.__dict__(),
                                 "is_pos_matching": is_pos_matched,
                                 "delta_pos": delta_pos,
                                 "event_time": event_time},
                                is_lic_matched)

        data = {
            "gt_pos": gt_pos,
            "pred_pos": pred_pos,
            "gt": gt.__dict__(),
            "pred": pred.__dict__(),
        }

        if is_validate_attr:
            self.type.add(data, is_type_matched)
            self.pose.add(data, is_pose_matched)
            self.state.add(data, is_state_matched)
        if is_rel_motion_matched:
            self.relative_motion.add(data, is_rel_motion_matched)

        self.scenario.add(is_lic_matched, gt)

        return delta_pos

    def compare(self, is_validate_attr: bool = False):
        for camera, events in self.valid_uploads.items():
            matched_indices = []
            delta_pos = 0
            last_pred_pos_matched = -1

            for gt_pos, gt in enumerate(self.gt.events):
                matched_data = self.compare_per_camera(gt,
                                                       gt_pos,
                                                       events,
                                                       matched_indices,
                                                       last_pred_pos_matched)

                if matched_data["is_lic_matched"]:
                    last_pred_pos_matched = matched_data["pred_pos"]

                delta_pos = self.accumulate(matched_data,
                                            delta_pos,
                                            is_validate_attr)

            for i, pred in enumerate(events):
                if i not in matched_indices:
                    self.extra_prediction[camera].append({
                        "at_seq_index": i,
                        "pred": pred.__dict__()
                    })
                else:
                    if(pred.enter_time != '' and pred.exit_time != ''):
                        try:
                            matched_enter_time = datetime.strptime(\
                                                pred.enter_time,
                                                date_format)
                            matched_exit_time = datetime.strptime(\
                                                pred.exit_time,
                                                date_format)
                            self.event_times[camera].append(
                            (matched_exit_time-matched_enter_time).total_seconds()*1000)
                        except:
                            print("WARNING: %s and %s creating error" % 
                                  pred.enter_time,
                                  pred.exit_time)
                    
            self.generate_report(camera)
            self.reset()

    def generate_report(self, camera):
        num_gt = self.gt.get_num_gt()
        num_matched, num_mismatched = self.scenario.get_stat()

        detailed_summary = {
            "Number of Ground Truth": num_gt,
            "License Plate": {
                "Num Matched": len(self.position_match.matched),
                "Matching Rate -> APR": "{0:.2f}%".format(len(
                    self.position_match.matched) / num_gt * 100),
                "Num Mismatched": len(self.position_match.mismatched)
            },
            "Pose": {
                "Num Matched": len(self.pose.matched),
                "Matching Rate": "{0:.2f}%".format(len(
                    self.pose.matched) / num_gt * 100),
                "Num Mismatched": len(self.pose.mismatched)
            },
            "Type": {
                "Num Matched": len(self.type.matched),
                "Matching Rate": "{0:.2f}%".format(len(
                    self.type.matched) / num_gt * 100),
                "Num Mismatched": len(self.type.mismatched)
            },
            "State": {
                "Num Matched": len(self.state.matched),
                "Matching Rate": "{0:.2f}%".format(len(
                    self.state.matched) / num_gt * 100),
                "Num Mismatched": len(self.state.mismatched)
            },
            "Relative Motion": {
                "Num Matched": len(self.relative_motion.matched),
                "Matching Rate": "{0:.2f}%".format(len(
                    self.relative_motion.matched) / num_gt * 100),
                "Num Mismatched": len(self.relative_motion.mismatched)
            },
            "Scenarios": {
                "Num Matched": num_matched,
                "Matching Rate": "{0:.2f}%".format(
                    num_matched / num_gt * 100),
                "Num Mismatched": num_mismatched,
                "Mismatched Scenarios": self.scenario.get_mismatched_scenarios()
            },
            "Extra Prediction": {
                "False Event Rate": "{0:.2f}%".format(
                    len(self.extra_prediction.get(camera, [])) / num_gt * 100),
            },
            "Other Details": {
                "Event Time" : {
                    # "list" : self.event_times.get(camera, [])
                    "Percentiles" : np.percentile(pd.Series(self.event_times.get
                                                            (camera, [])),
                                              q=[0, 25, 50, 75, 100]).tolist()
                }
            }
        }

        data = {
            "License Plate": {
                "Match": self.position_match.matched,
                "Mismatch": self.position_match.mismatched,
                "Summary": {
                    "Num Matched": len(self.position_match.matched),
                    "Matching Rate": "{0:.2f}%".format(len(
                        self.position_match.matched) / num_gt * 100),
                    "Num Mismatched": len(self.position_match.mismatched)
                }
            },
            "Pose": {
                "Match": self.pose.matched,
                "Mismatch": self.pose.mismatched,
                "Summary": {
                    "Num Matched": len(self.pose.matched),
                    "Matching Rate": "{0:.2f}%".format(len(
                        self.pose.matched) / num_gt * 100),
                    "Num Mismatched": len(self.pose.mismatched)
                }
            },
            "Type": {
                "Match": self.type.matched,
                "Mismatch": self.type.mismatched,
                "Summary": {
                    "Num Matched": len(self.type.matched),
                    "Matching Rate": "{0:.2f}%".format(len(
                        self.type.matched) / num_gt * 100),
                    "Num Mismatched": len(self.type.mismatched)
                }
            },
            "State": {
                "Match": self.state.matched,
                "Mismatch": self.state.mismatched,
                "Summary": {
                    "Num Matched": len(self.state.matched),
                    "Matching Rate": "{0:.2f}%".format(len(
                        self.state.matched) / num_gt * 100),
                    "Num Mismatched": len(self.state.mismatched)
                }
            },
            "Relative Motion": {
                "Match": self.relative_motion.matched,
                "Mismatch": self.relative_motion.mismatched,
                "Summary": {
                    "Num Matched": len(self.relative_motion.matched),
                    "Matching Rate": "{0:.2f}%".format(len(
                        self.relative_motion.matched) / num_gt * 100),
                    "Num Mismatched": len(self.relative_motion.mismatched)
                }
            },
            "Scenarios": {
                "Match": self.scenario.matched,
                "Mismatch": self.scenario.mismatched,
                "Summary": {
                    "Num Matched": num_matched,
                    "Matching Rate": "{0:.2f}%".format(num_matched / num_gt * 100),
                    "Num Mismatched": num_mismatched
                }
            },
            "Extra Prediction": {
                "Events": self.extra_prediction.get(camera, []),
                "False Event Rate": "{0:.2f}%".format(
                    len(self.extra_prediction.get(camera, [])) / num_gt * 100),
            }
        }

        # Detailed Summary
        filename = os.path.join(self.output_dir,
                (f"{self.criteria_name}-detailed_prediction_analysis.json"))
        json_data = {}
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                json_data = json.load(file)

        if self.filename not in json_data:
            json_data[self.filename] = {}
        json_data[self.filename][camera] = data

        with open(filename, 'w') as file:
            json_data = dict(sorted(json_data.items()))
            json.dump(json_data, file, ensure_ascii=False, indent=4)

        # Summary
        filename = os.path.join(self.output_dir,
                                (f"{self.criteria_name}-prediction_summary.json"))
        summary_json_data = {}
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                summary_json_data = json.load(file)

        if self.filename not in summary_json_data:
            summary_json_data[self.filename] = {}
        summary_json_data[self.filename][camera].update(detailed_summary)

        with open(filename, 'w') as file:
            summary_json_data = dict(sorted(summary_json_data.items()))
            json.dump(summary_json_data, file, ensure_ascii=False, indent=4)

    def reset(self):
        self.pose.reset()
        self.type.reset()
        self.state.reset()
        self.relative_motion.reset()
        self.scenario.reset()
        self.position_match.reset()
        self.extra_prediction.clear()