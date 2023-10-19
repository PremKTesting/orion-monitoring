//
// Copyright 2023, Metropolis Technologies, Inc.
//
// Created by anil on 6/9/22.
//

#include "cloud_watch_client.h"

using namespace orion::client;

bool CloudWatchClient::initialized_ = false;
std::string CloudWatchClient::namespace_;
std::string CloudWatchClient::site_id_;
std::string CloudWatchClient::hostname_ = orion::util::GetHostName();

std::string CloudWatchClient::GetHostname() {
  return CloudWatchClient::hostname_;
}

std::string CloudWatchClient::GetSiteId() {
  return CloudWatchClient::site_id_;
}

void CloudWatchClient::Init(YAML::Node config){
  if (CloudWatchClient::initialized_){
    return;
  }

  AwsInitHelper::GetCloudWatch();
  
  if (config["monitoring"].IsDefined() &&
      config["monitoring"]["namespace"].IsDefined()){
    CloudWatchClient::namespace_ = config["monitoring"]["namespace"].as<std::string>();
    std::cout << "Monitoring namespace used: "
              << CloudWatchClient::namespace_ << std::endl;
  }
  
  if (config["site_id"].IsDefined()){
    CloudWatchClient::site_id_ = config["site_id"].as<std::string>();
    std::cout << "Monitoring site used: "
              << CloudWatchClient::site_id_ << std::endl;
  }
  
  CloudWatchClient::initialized_ = true;
}

void CloudWatchClient::PushMetrics(
    const std::map<std::string, double>& metrics_data) {
  auto& client = AwsInitHelper::GetCloudWatch();
  auto metrics = CloudWatchClient::PrepareMetrics(metrics_data);
  CWRequest request = CloudWatchClient::GetRequest(metrics);
  CWResponse response = client.PutMetricData(request);
  if (!response.IsSuccess()) {
    std::cout << "Failed to publish AWS CloudWatch metric"
              << response.GetError()
              << std::endl;
  }
}

Aws::Vector<CWMetric> CloudWatchClient::PrepareMetrics(
    const std::map<std::string, double>& metrics_data) {
  
  Aws::Vector<CWMetric> metrics;
  std::string timestamp = orion::util::CurrentDateTime();
  
  for (auto [metric_name, value] : metrics_data){
    CWMetric metric = CloudWatchClient::GetMetric(metric_name, value,
                                                  CWUnit::Count, timestamp);
    metrics.push_back(metric);
  }
  
  return metrics;
}

void CloudWatchClient::PushCamMetrics(
                      const std::map<std::string, double>& cam_metrics_data,
                      const std::string& metric_name) {
  auto& client = AwsInitHelper::GetCloudWatch();
  auto metrics = CloudWatchClient::PrepareCamMetrics(cam_metrics_data, metric_name);
  CWRequest request = CloudWatchClient::GetRequest(metrics);
  CWResponse response = client.PutMetricData(request);
  if (!response.IsSuccess()) {
    std::cout << "Failed to publish AWS CloudWatch cam metric"
              << response.GetError()
              << std::endl;
  }
}

Aws::Vector<CWMetric> CloudWatchClient::PrepareCamMetrics(
                      const std::map<std::string, double>& cam_metrics_data,
                      const std::string& metric_name) {
  Aws::Vector<CWMetric> metrics;
  std::string timestamp = orion::util::CurrentDateTime();
  
  for (auto [cam_serial, sim_score] : cam_metrics_data){
    CWMetric metric = CloudWatchClient::GetCamMetric(metric_name, sim_score,
                                                     CWUnit::Count, cam_serial,
                                                     timestamp);
    metrics.push_back(metric);
  }
  
  return metrics;
}


CWMetric CloudWatchClient::GetCamMetric(const std::string& metric_name,
                                        double value, CWUnit unit,
                                        const std::string& cam_serial,
                                        const std::string& timestamp){
  CWMetric datum;
  datum.SetMetricName(metric_name);
  datum.SetUnit(unit);
  datum.SetValue(value);
  if (!timestamp.empty()){
    CLK::time_point time_point = orion::util::ParseStringToTimePoint(timestamp);
    auto date_time = CWDate(time_point);
    datum.SetTimestamp(date_time);
  }
  CWDimensions dimensions;
  dimensions.push_back(CloudWatchClient::GetDimension("SITE_ID",
                                                      CloudWatchClient::site_id_));
  dimensions.push_back(CloudWatchClient::GetDimension("CAMERA", cam_serial));
  dimensions.push_back(CloudWatchClient::GetDimension("host",
                                                      CloudWatchClient::hostname_));

  datum.WithDimensions(dimensions);
  
  return datum;
}

CWMetric CloudWatchClient::GetMetric(const std::string& metric_name,
                                     double value, CWUnit unit,
                                     const std::string& timestamp){
  CWMetric datum;
  datum.SetMetricName(metric_name);
  datum.SetUnit(unit);
  datum.SetValue(value);
  if (!timestamp.empty()){
    CLK::time_point time_point = orion::util::ParseStringToTimePoint(timestamp);
    auto date_time = CWDate(time_point);
    datum.SetTimestamp(date_time);
  }
  CWDimensions dimensions;
  dimensions.push_back(CloudWatchClient::GetDimension("SITE_ID",
                                                      CloudWatchClient::site_id_));
  dimensions.push_back(CloudWatchClient::GetDimension("host",
                                                      CloudWatchClient::hostname_));
  datum.WithDimensions(dimensions);
  
  return datum;
}

CWRequest CloudWatchClient::GetRequest(const Aws::Vector<CWMetric>& metrics){
  CWRequest request;
  request.SetMetricData(metrics);
  request.SetNamespace(CloudWatchClient::namespace_);
  return request;
}

CWDimension CloudWatchClient::GetDimension(const std::string& name,
                                           const std::string& value){
  CWDimension dimension;
  dimension.SetName(name);
  dimension.SetValue(value);
  return dimension;
}
