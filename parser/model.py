import collections
import json
import os
from typing import List, Any
from generate_pdf import Pdf
from datetime import datetime, date


class Table:
    def __init__(self, title: str, cols: List[str], rows: dict):
        self.title: str = title
        self.cols: List[str] = cols
        self.rows: dict = rows

    def write_pdf(self, pdf: Pdf, add_page: bool = False):
        if add_page:
            pdf.add_page(title=self.title)
        pdf.add_table(title=self.title,
                      headers=self.cols,
                      data=self.rows)


class ResultJson:
    def __init__(self):
        self.results: List[Table] = []

    def add(self, table: Table):
        self.results.append(table)

    def add_page(self, title):
        self.results.append(Table(title=title, cols=[], rows={}))

    def write(self, pdf: Pdf, output_dir):
        for result in self.results:
            if not result.cols and not result.rows:
                pdf.add_page(result.title)
            else:
                filename = "_".join(result.title.lower().split(" "))
                path = os.path.join(output_dir, filename + ".json")
                pdf.add_table(title=result.title,
                              headers=result.cols,
                              data=result.rows)
                with open(path, 'w') as file:
                    json.dump(result.rows, file, ensure_ascii=False, indent=4)


class Data:
    def __init__(self, data: Any):
        self.is_gt: bool = False
        self.lic_plate: str = ""
        self.state: str = ""
        self.relative_motion: str = ""
        self.pose: str = ""
        self.type: str = ""
        self.category: str = ""
        self.category: str = ""
        self.is_valid_upload: bool = False
        self.entry_direction: str = ""
        self.exit_direction: str = ""
        self.enter_time: str = ""
        self.exit_time: str = ""
        self.suppress_reason: list = []
        self.linked_lic_numbers: dict = {}

        if data and type(data) == str:
            parts = data.split(",")
            self.lic_plate: str = str(parts[0]).strip()
            self.state: str = str(parts[1]).strip()
            self.relative_motion: str = str(parts[2]).strip()
            self.pose: str = str(parts[3]).strip()
            self.type: str = str(parts[4]).strip()
            self.category: str = str(parts[5]).strip()
            self.category = str(self.category.replace("\n", "")).strip()
            self.is_valid_upload: bool = True
            self.is_gt = True
        elif data and type(data) == dict:
            if "source" not in data:
                self._load_old_json_format(data)
            else:
                self._load_new_json_format(data)

    def _load_new_json_format(self, data: dict):
        license = data.get("license", {})
        event = data.get("event", {})
        vehicle = data.get("vehicle", {})
        motion = data.get("motion", {})
        event_state = data.get("event_state", {})

        self.linked_lic_numbers: dict = license.get("num_count", {})
        self.suppress_reason: list = event.get("suppress_reason", [])
        self.lic_plate: str = license.get("number", "")
        self.state: str = license.get("state", "")
        self.relative_motion: str = motion.get("relative_motion", "")
        self.pose: str = vehicle.get("pose", "")
        self.type: str = vehicle.get("type", "")
        self.is_valid_upload: bool = event.get("valid", False)
        self.entry_direction: str = motion.get("entry_side", "")
        self.exit_direction: str = motion.get("exit_side", "")
        self.enter_time: str = event_state.get("enter_timestamp", "")
        self.exit_time: str = event_state.get("exit_timestamp", "")

    def _load_old_json_format(self, data: dict):
        self.linked_lic_numbers: dict = data.get(
            "LINKED_LICENSE_PLATE_NUMS", {})
        self.suppress_reason: list = data.get("SUPPRESS_REASON", [])
        self.lic_plate: str = data.get("LICENSE_PLATE_NUMBER", "")
        self.state: str = data.get("LICENSE_PLATE_STATE", "")
        self.relative_motion: str = data.get("RELATIVE_MOTION", "")
        self.pose: str = data.get("POSE", "")
        self.type: str = data.get("TYPE", "")
        self.is_valid_upload: bool = data.get("VALID_UPLOAD", False)
        self.entry_direction: str = data.get("ENTER_DIRECTION", "")
        self.exit_direction: str = data.get("EXIT_DIRECTION", "")
        self.enter_time: str = data.get("ENTER_TIME", "")
        self.exit_time: str = data.get("EXIT_TIME", "")

    def __str__(self):
        return f"{self.lic_plate} - {self.pose} - {self.type} - {self.state}"

    def __dict__(self):
        if self.is_gt:
            return {
                "lic_plate": self.lic_plate,
                "state": self.state,
                "relative_motion": self.relative_motion,
                "pose": self.pose,
                "type": self.type,
                "category": self.category,
            }

        return {
            "lic_plate": self.lic_plate,
            "state": self.state,
            "relative_motion": self.relative_motion,
            "pose": self.pose,
            "type": self.type,
            "category": self.category,
            "is_valid_upload": self.is_valid_upload,
            "entry_direction": self.entry_direction,
            "exit_direction": self.exit_direction,
            "enter_time": self.enter_time,
            "exit_time" : self.exit_time
        }


class GroundTruthData:
    def __init__(self, filename):
        self.filename: str = filename
        self.events: List[Data] = []
        self.categories: dict = collections.defaultdict(int)
        self.poses: dict = collections.defaultdict(int)
        self.types: dict = collections.defaultdict(int)
        self.states: dict = collections.defaultdict(int)
        self.relative_motions: dict = collections.defaultdict(int)

    def get_num_gt(self):
        return len(self.events) if self.events else 1

    def add(self, event: Data):
        self.events.append(event)
        self.categories[event.category] += 1
        self.poses[event.pose] += 1
        self.types[event.type] += 1
        self.states[event.state] += 1
        self.relative_motions[event.relative_motion] += 1

    def write_json(self, output_dir):
        data = {
            "Number of Ground Truth Events": len(self.events),
            "Video Category": self.categories,
            "Pose": self.poses,
            "Type": self.types,
            "State": self.states,
            "Relative Motion": self.relative_motions
        }

        filename = os.path.join(output_dir, "ground_truth_summary.json")
        json_data = {}
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                json_data = json.load(file)

        json_data[self.filename] = data

        with open(filename, 'w') as file:
            json_data = dict(sorted(json_data.items()))
            json.dump(json_data, file, ensure_ascii=False, indent=4)

    def summarise_to_pdf(self, result: ResultJson):
        result.add_page(f"Ground Truth Summary")
        cols = ["Item", "Count"]
        table = Table(title=f"Ground Truth Video Category Summary",
                      cols=cols,
                      rows=self.categories)
        result.add(table)
        table = Table(title=f"Ground Truth Poses Summary",
                      cols=cols,
                      rows=self.poses)
        result.add(table)
        table = Table(title=f"Ground Truth Types Summary",
                      cols=cols,
                      rows=self.types)
        result.add(table)
        table = Table(title=f"Ground Truth States Summary",
                      cols=cols,
                      rows=self.states)
        result.add(table)
        table = Table(title=f"Ground Truth Relative Motions Summary",
                      cols=cols,
                      rows=self.relative_motions)
        result.add(table)


class PredictionData:
    def __init__(self, filename):
        self.filename: str = filename
        self.events = collections.defaultdict(list)
        self.num_valid_events = collections.defaultdict(int)
        self.num_invalid_events = collections.defaultdict(int)

    def add(self, event: Data, camera: str):
        s = "Duplicate license plate found within 120000.000000 msecs"
        is_valid = event.is_valid_upload
        # if s in event.suppress_reason and not is_valid:
        #     is_valid = True

        # total_count = 0
        # max_count = 0
        # for lic_num, count in event.linked_lic_numbers.items():
        #     total_count += count
        #     if max_count < count:
        #         max_count = count
        #
        # if total_count > 0 and not is_valid and \
        #         (max_count / total_count) > 0.75:
        #     is_valid = True
        #     event.relative_motion = "Moving Away"

        event.is_valid_upload = is_valid
        self.events[camera].append(event)

        if is_valid:
            self.num_valid_events[camera] += 1
        else:
            self.num_invalid_events[camera] += 1

    def write_json(self, output_dir, criteria_name):
        data = collections.defaultdict(dict)

        for camera, preds in self.events.items():
            data[camera] = {
                "Number of event identified": len(preds),
                "Number of valid events (uploaded)":
                    self.num_valid_events.get(camera, 0),
                "Number of invalid events (not uploaded)":
                    self.num_invalid_events.get(camera, 0)
            }
        filename = os.path.join(output_dir, 
                                (f"{criteria_name}-prediction_summary.json"))
        json_data = {}
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                json_data = json.load(file)

        json_data[self.filename] = data

        with open(filename, 'w') as file:
            json_data = dict(sorted(json_data.items()))
            json.dump(json_data, file, ensure_ascii=False, indent=4)

    def summarise_to_pdf(self, result: ResultJson):
        pass
        # result.add_page(f"Ground Truth Summary")
        # cols = ["Item", "Count"]
        # table = Table(title=f"Ground Truth Video Category Summary",
        #               cols=cols,
        #               rows=self.categories)
        # result.add(table)
        # table = Table(title=f"Ground Truth Poses Summary",
        #               cols=cols,
        #               rows=self.poses)
        # result.add(table)
        # table = Table(title=f"Ground Truth Types Summary",
        #               cols=cols,
        #               rows=self.types)
        # result.add(table)
        # table = Table(title=f"Ground Truth States Summary",
        #               cols=cols,
        #               rows=self.states)
        # result.add(table)
        # table = Table(title=f"Ground Truth Relative Motions Summary",
        #               cols=cols,
        #               rows=self.relative_motions)
        # result.add(table)


class ComparisonResult:
    def __init__(self, comp_title: str):
        self.comp_title: str = comp_title
        self.matched: List[dict] = []
        self.mismatched: List[dict] = []

    def add(self, data, is_matched):
        if is_matched:
            self.matched.append(data)
        else:
            self.mismatched.append(data)

    def reset(self):
        self.matched.clear()
        self.mismatched.clear()


class ComparisonResultCategory:
    def __init__(self, comp_title: str, gt=None):
        self.comp_title: str = comp_title
        self.matched: dict = collections.defaultdict(list)
        self.mismatched: dict = collections.defaultdict(list)
        self.gt = gt

    def add(self, is_matched, gt):
        if is_matched:
            self.matched[gt.category].append(gt.__dict__())
        else:
            self.mismatched[gt.category].append(gt.__dict__())

    def get_mismatched_scenarios(self):
        scenarios = {}
        for scenario, _ in self.mismatched.items():
            if (scenario in scenarios):
                scenarios[scenario] += 1
            else:
                scenarios[scenario] = 1

        return scenarios

    def get_stat(self):
        num_matched, num_mismatched = 0, 0
        for _, l in self.matched.items():
            num_matched += len(l)

        for _, l in self.mismatched.items():
            num_mismatched += len(l)

        return num_matched, num_mismatched

    def summarise_to_pdf(self, result: ResultJson, gt, camera):
        pdf_table_data = collections.defaultdict(dict)
        cols: list = ["Category", "Prediction / GroundTruth numbers"]

        for scenario, lic_plates in self.matched.items():
            pdf_table_data[f"{scenario}"] = {
                "operation": "equal",
                "gt": gt[scenario],
                "pred": len(lic_plates)
            }

        table = Table(title=f"Scenarios Matched for camera {camera}",
                      cols=cols,
                      rows=pdf_table_data)
        result.add(table)

        pdf_table_data = {}
        for scenario, lic_plates in self.mismatched.items():
            pdf_table_data[f"{scenario}"] = {
                "operation": "equal",
                "gt": gt[scenario],
                "pred": len(lic_plates)
            }

        table = Table(title=f"Scenarios Mismatched for camera {camera}",
                      cols=cols,
                      rows=pdf_table_data)
        result.add(table)

    def reset(self):
        self.matched.clear()
        self.mismatched.clear()


class ComparisonResults:
    def __init__(self):
        self.comparisons: List[ComparisonResult] = []

    def add(self, comparison: ComparisonResult):
        self.comparisons.append(comparison)

    def summarise_to_pdf(self, result: ResultJson, camera: str):
        pdf_table_data = {}
        for comparison in self.comparisons:
            title = comparison.comp_title
            num_matched = len(comparison.matched)
            num_mismatched = len(comparison.mismatched)
            pdf_table_data[f"{title} Matched"] = num_matched
            pdf_table_data[f"{title} Mismatched"] = num_mismatched

        table = Table(title=f"Match and Mismatch details for camera {camera}",
                      cols=["Item", "Count"],
                      rows=pdf_table_data)
        result.add(table)

        self.summarise_all_mismatch(result, camera)

    def summarise_all_mismatch(self, result: ResultJson, camera: str):
        for comparison in self.comparisons:
            pdf_table_data = collections.defaultdict(list)
            title = comparison.comp_title
            if len(comparison.mismatched) > 0:
                for mismatch in comparison.mismatched:
                    gt = mismatch.get("gt", Data(""))
                    pred = mismatch.get("pred", Data({}))
                    if "type" in title.lower():
                        g = f"{gt.lic_plate}-{gt.type}"
                        p = f"{pred.lic_plate}-{pred.type}"
                        pdf_table_data[g].append(p)
                    elif "pose" in title.lower():
                        g = f"{gt.lic_plate}-{gt.pose}"
                        p = f"{pred.lic_plate}-{pred.pose}"
                        pdf_table_data[g].append(p)
                    elif "motion" in title.lower():
                        g = f"{gt.lic_plate}-{gt.relative_motion}"
                        p = f"{pred.lic_plate}-{pred.relative_motion}"
                        pdf_table_data[g].append(p)
                    elif "license" in title.lower():
                        g = f"{gt.lic_plate}-{gt.pose}-{gt.type}"
                        p = f"{pred.lic_plate}-{pred.pose}-{pred.type}"
                        pdf_table_data[g].append(p)

            table = Table(title=f"{title} Mismatch Summary for camera {camera}",
                          cols=["Ground Truth", "Prediction"],
                          rows=pdf_table_data)
            result.add(table)

class LogData:             