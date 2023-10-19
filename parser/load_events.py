import collections
import os
import json
from model import (Data, GroundTruthData, PredictionData)


class LoadEvents:
    def __init__(self, gt_file, orion_data_dir):
        self.gt_file: str = gt_file
        self.gt_filename: str = self.gt_file.split("/")[-1]
        self.event_dir: str = os.path.join(orion_data_dir, "events")
        self.log_dir: str = os.path.join(orion_data_dir, "log")
        self.final_event_dir: str = os.path.join(orion_data_dir, "final_events")
        self.gts: GroundTruthData = GroundTruthData(self.gt_filename)
        self.preds: PredictionData = PredictionData(self.gt_filename)

    def load_gt(self):
        print(f"Loading GroundTruth {self.gt_file}")
        with open(self.gt_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                gt = Data(line)
                self.gts.add(gt)

    def load_date_camera_dirs(self, is_final_event: bool = False):
        event_load_dir = self.final_event_dir if is_final_event else self.event_dir
        print(f"Listing date and camera dirs {event_load_dir}")
        date_dirs = os.listdir(event_load_dir)
        date_dirs = sorted(date_dirs)
        dirs = []
        for date_dir in date_dirs:
            camera_dir_path = os.path.join(event_load_dir, date_dir)
            camera_dirs = os.listdir(camera_dir_path)
            camera_dirs = sorted(camera_dirs)
            for camera_dir in camera_dirs:
                dirs.append(os.path.join(date_dir, camera_dir))
        return dirs, event_load_dir

    def load_events(self, is_final_event: bool = False):
        cam_dirs, event_load_dir = self.load_date_camera_dirs(is_final_event)
        events = collections.defaultdict(list)

        for cam_dir in cam_dirs:
            date, camera = cam_dir.split("/")
            event_dir_path = os.path.join(event_load_dir,
                                          cam_dir)
            event_timestamp_dirs = os.listdir(event_dir_path)
            event_timestamp_dirs = sorted(event_timestamp_dirs)

            for event_timestamp_dir in event_timestamp_dirs:
                event_path = os.path.join(event_dir_path, event_timestamp_dir)
                filenames = os.listdir(event_path)
                for filename in filenames:
                    if filename.endswith(".json") and \
                            filename.startswith("media"):
                        filepath = os.path.join(event_path, filename)
                        with open(filepath, 'r') as file:
                            event = json.load(file)
                            data = Data(event)
                            self.preds.add(data, camera)
    
    def load_log_dirs(self):
        log_files = []
        event_log_dir = self.log_dir
        date_log_dirs = os.listdir(event_log_dir)
        for date_log in date_log_dirs:
            date_log_dir = os.path.join(event_log_dir, date_log)
            log_list = os.listdir(date_log_dir)
            for log_file in log_list:
                if log_file.endswith(".log"):
                    log_files.append(os.path.join(event_log_dir, log_file))
            print(f"Log file: {log_files}")
        
        return log_files, event_log_dir