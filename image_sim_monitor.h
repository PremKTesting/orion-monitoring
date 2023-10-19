//
// Copyright 2023, Metropolis Technologies, Inc.
//
// Created by long on 9/22/2023.
//
#ifndef ORION_MONITORING_IMAGE_SIMILARITY_H_
#define ORION_MONITORING_IMAGE_SIMILARITY_H_
#include <opencv2/opencv.hpp>
#include <vector>
#include <map>
#include <yaml-cpp/yaml.h>
#include <experimental/filesystem>
#include "opencv2/xfeatures2d.hpp"
#include "util.h"
#include "cloud_watch_client.h"

typedef std::chrono::time_point<std::chrono::system_clock> Timestamp;

namespace orion::monitor {
    class ImageSimilarityMonitor {
        public:
            ImageSimilarityMonitor(const std::string& config_filename,
                                   const double& sim_threshold=0.50,
                                   const double& dark_theshold=10,
                                   const double& valid_bbox_ratio=0.60,
                                   const int& eval_period_in_min = 15,
                                   const bool& is_enable_surf=false);
            
	        bool Execute();
            void Reset();

            std::map<std::string, double> GetSimMetricData();

            bool IsSimilar(cv::Mat& img_1, cv::Mat& img_2);
            double GetSimilarityScore(cv::Mat& prev_img, cv::Mat& cur_img);
            bool IsPerformSimilarityCheck(const std::string& cam_serial_path,
                                          const std::string& cam_serial);
            
            std::tuple<cv::Mat, cv::Mat> GetInputImages(
                                        const std::string& cam_serial_path);

        private:
            int GetCurrentCanaryImageCount(const std::string& cam_serial_path);
            
            void UpdateCameraSerial();
            std::unordered_set<std::string> GetCurrentCamSerials();
            void CleanUpInvalidCamSerial(
                        const std::unordered_set<std::string>& cur_cam_serials);
            std::string ParseCamSerialFromPath(const std::string& cam_serial_path);

            cv::RotatedRect FindLargestBbox(const cv::Mat& image);
            bool IsBboxValid(const cv::RotatedRect& bbox, const double& max_area);
            void WhiteOut(cv::Mat& img, const cv::RotatedRect& bbox);

            void PreProcessImage(cv::Mat& image);
            cv::Mat GammaCorrection(const cv::Mat& src, 
                                    const float& gamma);
            void DilateImage(cv::Mat& src);

            bool IsDarkImage(const cv::Mat& image);
            double GetPixelMean(const cv::Mat& image);
            
            void PrepareImagesForSIFT(cv::Mat& img1, cv::Mat& img2);
            double ORBSimilarityScore(const cv::Mat& img_1, 
                                      const cv::Mat& img_2);
            double SIFTSimilarityScore(const cv::Mat& img_1, 
                                        const cv::Mat& img_2);
            double SURFSimilarityScore(const cv::Mat& img_1, 
                                        const cv::Mat& img_2);

            double dark_threshold = 10;
            double sim_threshold = 0.50;
            double valid_bbox_ratio = 0.6;
            bool is_enable_surf = false;
            int eval_period_in_min_ = 15;

            std::string canary_dir_;
            std::string config_base_pth_;
            std::map<std::string, Timestamp> cam_2_last_eval_timestamp_;
            std::map<std::string, std::string> path_2_cam_serial_;
            
            std::map<std::string, int> cam_2_canary_img_counter_;
            std::map<std::string, double> cam_2_sim_score_;
    };
}

#endif //ORION_MONITORING_IMAGE_SIMILARITY_H_
