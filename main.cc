//
// Copyright 2023, Metropolis Technologies, Inc.
//
// Created by anil on 4/9/21.
//
#include <thread>
#include <chrono>
#include <map>
#include "temp_monitor.h"
#include "service_monitor.h"
#include "aws_client_helper.h"
#include "cloud_watch_client.h"
#include "image_sim_monitor.h"

using namespace orion::monitor;
using namespace orion::util;

int main(int argc, char** argv){
  const char *config_filename = argv[1];
  const char *reporting_interval_seconds = argv[2];
  const char *canary_report_interval_mins = argv[3];
  int eval_period_in_min = std::atoi(canary_report_interval_mins);
  int seconds = std::atoi(reporting_interval_seconds);
  auto config = ReadConfiguration(config_filename);
  
  orion::client::AwsInitHelper aws_init_helper{};
  CloudWatchClient::Init(config);
  
  TempMonitor temp_monitor = TempMonitor();
  ServiceMonitor service_monitor = ServiceMonitor();
  ImageSimilarityMonitor img_sim_monitor = ImageSimilarityMonitor(
    config_filename, 0.50 /*sim_threshold*/, 10 /*dark_theshold*/,
    0.60 /*valid_bbox_ratio*/, eval_period_in_min, false /*is_enable_surf*/);

  for(;;){
    Temp temp_info = temp_monitor.GetTempInfo();
    Service service_info = service_monitor.GeServiceInfo(kOrionService);
    std::map<std::string, double> metric_definitions = {
        {"cpu_temp", temp_info.cpu},
        {"gpu_temp", temp_info.gpu},
        {"orion_active", service_info.is_active},
    };
    
    try{
      CloudWatchClient::PushMetrics(metric_definitions);
    } catch (std::exception& ex){}
  
    bool status = img_sim_monitor.Execute();
    auto cam_metrics_data = img_sim_monitor.GetSimMetricData();
    
    if (status && cam_metrics_data.size() != 0) {
      try{
        CloudWatchClient::PushCamMetrics(cam_metrics_data);
      } catch (std::exception& ex){}
    }

    img_sim_monitor.Reset();
    std::this_thread::sleep_for(std::chrono::seconds(seconds));
  }
  
  return 0;
}
