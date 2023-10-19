//
// Copyright 2023, Metropolis Technologies, Inc.
//
// Created by ryan on 5/27/22.
//

#include "aws_client_helper.h"

using namespace orion::client;

std::atomic<int> AwsInitHelper::ref_count_ = {0};
Aws::SDKOptions AwsInitHelper::options_;
std::mutex AwsInitHelper::options_mutex_;
std::unique_ptr<Aws::CloudWatch::CloudWatchClient> AwsInitHelper::cw_client_;


AwsInitHelper::AwsInitHelper() {
  if ((++AwsInitHelper::ref_count_) == 1) {
    options_mutex_.lock();
    //    AwsInitHelper::options_.loggingOptions.logLevel = Aws::Utils::Logging::LogLevel::Trace;
    Aws::InitAPI(AwsInitHelper::options_);
    // Learn more about configurations
    // https://sdk.amazonaws.com/cpp/api/LATEST/struct_aws_1_1_client_1_1_client_configuration.html
    Aws::Client::ClientConfiguration cw_client_cfg;
    cw_client_cfg.connectTimeoutMs = 2000; // 2 second
    cw_client_cfg.httpRequestTimeoutMs = 5000; // 5 second
    cw_client_cfg.requestTimeoutMs = 2000; // 2 second
    cw_client_cfg.verifySSL = false;
    cw_client_cfg.maxConnections = 25; // TCP max connect to a single client.
    AwsInitHelper::cw_client_ = std::make_unique<Aws::CloudWatch::CloudWatchClient>(cw_client_cfg);
    std::cout << "CloudWatch client is created" << std::endl;
  }
}

AwsInitHelper::~AwsInitHelper() {
  if ((--AwsInitHelper::ref_count_) == 0) {
    std::cout << "CloudWatch client is shutting down" << std::endl;
    AwsInitHelper::cw_client_ = nullptr;

    Aws::ShutdownAPI(AwsInitHelper::options_);
    Aws::Utils::Memory::ShutdownAWSMemorySystem();
    options_mutex_.unlock();
  }
}

Aws::CloudWatch::CloudWatchClient& AwsInitHelper::GetCloudWatch() {
  return *AwsInitHelper::cw_client_;
}
