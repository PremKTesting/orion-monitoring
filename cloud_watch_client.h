//
// Copyright 2023, Metropolis Technologies, Inc.
//
// Created by anil on 6/9/22.
// Note: Not Thread Safe - Can only be called by CloudWatchPublisher
//

#ifndef ORION_INCLUDES_MONITORING_CLOUD_WATCH_CLIENT_H_
#define ORION_INCLUDES_MONITORING_CLOUD_WATCH_CLIENT_H_
#include <iostream>
#include <utility>
#include <set>
#include <mutex>
#include <yaml-cpp/yaml.h>
#include <boost/uuid/uuid_io.hpp>
#include <aws/core/Aws.h>
#include <aws/monitoring/CloudWatchClient.h>
#include <aws/monitoring/model/PutMetricDataRequest.h>
#include "aws_client_helper.h"
#include "util.h"

using CWRequest = Aws::CloudWatch::Model::PutMetricDataRequest;
using CWResponse = Aws::CloudWatch::Model::PutMetricDataOutcome;
using CWMetric = Aws::CloudWatch::Model::MetricDatum;
using CWDimension = Aws::CloudWatch::Model::Dimension;
using CWDimensions = Aws::Vector<Aws::CloudWatch::Model::Dimension>;
using CWUnit = Aws::CloudWatch::Model::StandardUnit;
using CWDate = Aws::Utils::DateTime;

class CloudWatchClient{
 public:
  static void Init(YAML::Node config);

  /**
   * Use this to push metrics to AWS CloudWatch
   * @param metric_definitions
   */
  static void PushMetrics(
      const std::map<std::string, double>& metrics_data);
  /**
   * Prepare metrics from the metric definition map. Metric definition map
   * will look like.
   * {
   *    "metric_name_1" : 2.0,
   *    "metric_name_1" : 100.0
   * }
   * @param metric_definitions
   * @return
   */
  static Aws::Vector<CWMetric> PrepareMetrics(
      const std::map<std::string, double>& metrics_data);

  /**
   * Use this to push metrics to AWS CloudWatch
   * @param metric_definitions
   */
  static void PushCamMetrics(
      const std::map<std::string, double>& cam_metrics_data,
      const std::string& metric_name="image_similarity");

  /**
   * Prepare metrics from the metric definition map. Metric definition map
   * will look like.
   * {
   *    "cam_serial_id_1" : similarity_score_1,
   *    "cam_serial_id_2" : similarity_score_2
   * }
   * @param metric_definitions
   * @return
   */
  static Aws::Vector<CWMetric> PrepareCamMetrics(
    const std::map<std::string, double>& cam_metrics_data,
    const std::string& metric_name="image_similarity");

  static std::string GetHostname();
  static std::string GetSiteId();

 private:
  static bool initialized_;
  static std::string hostname_;
  static std::string site_id_;
  static std::string namespace_;
  
  static CWRequest GetRequest(const Aws::Vector<CWMetric>& metrics);
  static CWMetric GetMetric(const std::string& metric_name,
                            double value,
                            CWUnit unit = CWUnit::None,
                            const std::string& timestamp = "");
  static CWMetric GetCamMetric(const std::string& metric_name,
                               double value, CWUnit unit,
                               const std::string& cam_serial,
                               const std::string& timestamp = "");
  static CWDimension GetDimension(const std::string& name, const std::string& value);
  
  CloudWatchClient() = delete; // not instantiable
  ~CloudWatchClient() = delete; // not instantiable
};

#endif //ORION_INCLUDES_MONITORING_CLOUD_WATCH_CLIENT_H_
