//
// Copyright 2023, Metropolis Technologies, Inc.
//
// Created by anil on 4/3/23.
//
#ifndef ORION_MONITORING_ORION_MONITORING_AWS_CLIENT_HELPER_H_
#define ORION_MONITORING_ORION_MONITORING_AWS_CLIENT_HELPER_H_

#include <iostream>
#include <string>
#include <map>
#include <set>
#include <atomic>
#include <mutex>
#include <aws/core/Aws.h>
#include <aws/core/client/ClientConfiguration.h>
#include <aws/monitoring/CloudWatchClient.h>


namespace orion::client {

/**
 * @brief Helper class to ensure AWS SDK remains initialized while any code
 * using AWS is still running.
 * @details Implemented with reference counting. To use, just keep an
 * AwsInitHelper object around for as long as is needed.
 */
  class AwsInitHelper {
   public:
    AwsInitHelper();
    ~AwsInitHelper();
    static Aws::CloudWatch::CloudWatchClient& GetCloudWatch();
   
   private:
    static std::atomic<int> ref_count_;
    static std::mutex options_mutex_;
    static Aws::SDKOptions options_;
    static std::unique_ptr<Aws::CloudWatch::CloudWatchClient> cw_client_;
    
  }; // class AwsInitHelper
  
} // namespace orion::util

#endif //ORION_MONITORING_ORION_MONITORING_AWS_CLIENT_HELPER_H_
