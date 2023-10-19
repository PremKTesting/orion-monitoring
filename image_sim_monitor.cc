//
// Copyright 2023, Metropolis Technologies, Inc.
//
// Created by long on 9/22/2023.
//
#include "image_sim_monitor.h"

using namespace orion::monitor;
using namespace orion::util;
namespace fs = std::experimental::filesystem;

ImageSimilarityMonitor::ImageSimilarityMonitor(
    const std::string& config_filename,
    const double& sim_threshold,
    const double& dark_theshold,
    const double& valid_bbox_ratio,
    const int& eval_period_in_min,
    const bool& is_enable_surf    // Due to license issue
) {
    this->sim_threshold = sim_threshold;
    this->dark_threshold = dark_theshold;
    this->valid_bbox_ratio = valid_bbox_ratio;
    this->is_enable_surf = is_enable_surf;  
    this->eval_period_in_min_ = eval_period_in_min;

    auto config = ReadConfiguration(config_filename);

    int idx = config_filename.rfind("global.yaml");
    this->config_base_pth_ = config_filename.substr(0, idx);

    if (config["canary"].IsDefined() &&
        config["canary"]["dir"].IsDefined()){
        this->canary_dir_ = config["canary"]["dir"].as<std::string>();
    }
    
    // Set canary_img_counter_ for ALL cams
    UpdateCameraSerial();
    for (auto const& [cam_serial, cam_serial_path]: this->path_2_cam_serial_) {
        this->cam_2_canary_img_counter_[cam_serial] = 0;
        this->cam_2_last_eval_timestamp_[cam_serial] = std::chrono::system_clock::from_time_t(0);
    } 
}

std::string ImageSimilarityMonitor::ParseCamSerialFromPath(
    const std::string& cam_serial_path) {
    std::string corrected_cam_serial_path;

    if (cam_serial_path[cam_serial_path.length() - 1] == '/') {
        std::string corrected_cam_serial_path = cam_serial_path.substr(
            0, cam_serial_path.length() - 2
        );
    } else {
        corrected_cam_serial_path = cam_serial_path;
    }

    auto tmp = SplitString(corrected_cam_serial_path, "/");
    std::string cam_serial = tmp[tmp.size() - 1];
    return cam_serial;
}


std::map<std::string, double> ImageSimilarityMonitor::GetSimMetricData() {
    return this->cam_2_sim_score_;
}

void ImageSimilarityMonitor::Reset() {
    cam_2_sim_score_.clear();
}

bool ImageSimilarityMonitor::Execute() {
    UpdateCameraSerial();
    if (this->path_2_cam_serial_.size() == 0) {
        return false;
    }

    for (auto const& [cam_serial, cam_serial_path] : this->path_2_cam_serial_) {
      auto is_perform = this->IsPerformSimilarityCheck(cam_serial_path, cam_serial);
      if (!is_perform){
        continue;
      }
      
      cv::Mat cur_img, prev_img;
      std::tie(prev_img, cur_img) = this->GetInputImages(cam_serial_path);
      double sim_score = this->GetSimilarityScore(prev_img, cur_img);
      
      this->cam_2_sim_score_[cam_serial] = sim_score;
      int img_counter = this->GetCurrentCanaryImageCount(cam_serial_path);
      this->cam_2_canary_img_counter_[cam_serial] = img_counter ;
      this->cam_2_last_eval_timestamp_[cam_serial] = std::chrono::system_clock::now();
    }

    return true;
}


int ImageSimilarityMonitor::GetCurrentCanaryImageCount(const std::string& cam_serial_path) {
    int image_counter = 0;
    for (const auto& file : fs::directory_iterator(cam_serial_path)) {
        if (file.status().type() == fs::file_type::regular && 
            file.path().extension() == ".jpg") {
            image_counter++;
        }
    }
    return image_counter;
}

std::tuple<cv::Mat, cv::Mat> ImageSimilarityMonitor::GetInputImages(
    const std::string& cam_serial_path) {

    std::vector<std::pair<std::string, std::time_t>> canary_imgs;

    for (const auto& entry : fs::directory_iterator(cam_serial_path)) {
        if (entry.status().type() == fs::file_type::regular &&
            entry.path().extension() == ".jpg") {
            std::pair<std::string, std::time_t> img_pair;
            img_pair.first = entry.path().string();
	        img_pair.second = std::chrono::system_clock::to_time_t(fs::last_write_time(entry));
                canary_imgs.push_back(img_pair);
        }
    }

    // Sort JPG files by timestamp in descending order
    std::sort(
        canary_imgs.begin(), 
        canary_imgs.end(), 
        [](const auto& a, const auto& b) {
            return a.second > b.second; // compare by second argument (timestamp)
        }
    );
    
    return std::tuple<cv::Mat, cv::Mat>(
		    cv::imread(canary_imgs[1].first), 
		    cv::imread(canary_imgs[0].first)
    );
}

void ImageSimilarityMonitor::UpdateCameraSerial() {
    std::unordered_set<std::string> cam_serials = GetCurrentCamSerials();
    this->CleanUpInvalidCamSerial(cam_serials);
}

std::unordered_set<std::string> ImageSimilarityMonitor::GetCurrentCamSerials() {
    std::string cur_date = CurrentDate();
    std::string cam_base_pth = this->canary_dir_ + "/" + cur_date + "/";
    if (!fs::exists(cam_base_pth)) {
        return std::unordered_set<std::string>{};
    }

    std::unordered_set<std::string> cam_serials;
    for (const auto& entry : fs::directory_iterator(this->config_base_pth_)) {
        if (entry.status().type() == fs::file_type::regular && 
            entry.path().filename().string().find("config_") == 0) {
            
            auto cam_config = ReadConfiguration(entry.path().string());
            if (cam_config["source"].IsDefined() &&
                cam_config["source"]["camera_serial"].IsDefined()) {
                
                std::string cam_serial = 
                        cam_config["source"]["camera_serial"].as<std::string>();
                std::string cam_serial_path = cam_base_pth + cam_serial;
                this->path_2_cam_serial_[cam_serial] = cam_serial_path;
                
                cam_serials.emplace(cam_serial);
            }
        }
    }
    
    return cam_serials;
}

void ImageSimilarityMonitor::CleanUpInvalidCamSerial(
                    const std::unordered_set<std::string>& cur_cam_serials) {
    for (auto const& [cam_serial, cam_serial_path] : this->path_2_cam_serial_) {
        if (cur_cam_serials.find(cam_serial) == cur_cam_serials.end()) {
            this->path_2_cam_serial_.erase(cam_serial);
            this->cam_2_last_eval_timestamp_.erase(cam_serial);
            this->cam_2_canary_img_counter_.erase(cam_serial);
            this->cam_2_sim_score_.erase(cam_serial);
        }
    }
}

bool ImageSimilarityMonitor::IsPerformSimilarityCheck(const std::string& cam_serial_path,
                                                      const std::string& cam_serial) {
    auto cur_timestamp = std::chrono::system_clock::now();
    auto duration =  cur_timestamp - this->cam_2_last_eval_timestamp_[cam_serial];
    auto duration_mins = std::chrono::duration_cast<std::chrono::seconds>(duration).count();
    if (duration_mins < this->eval_period_in_min_) {
        return false;
    }

    int cur_canary_img_count = GetCurrentCanaryImageCount(cam_serial_path);
    int prev_canary_img_count = this->cam_2_canary_img_counter_[cam_serial];

    if (cur_canary_img_count != prev_canary_img_count &&
        cur_canary_img_count > 1) {
        return true;
    } else {
        return false;
    }
}

double ImageSimilarityMonitor::GetSimilarityScore(cv::Mat& prev_img, cv::Mat& cur_img) {
    bool is_prev_img_dark = this->IsDarkImage(prev_img);
    bool is_cur_img_dark = this->IsDarkImage(cur_img);

    if ((is_prev_img_dark && !is_cur_img_dark) || 
        (!is_prev_img_dark && is_cur_img_dark)) {
        return 0;
    }

    this->PrepareImagesForSIFT(prev_img, cur_img);

    double sift_sim = this->SIFTSimilarityScore(prev_img, cur_img);
    double orb_sim = this->ORBSimilarityScore(prev_img, cur_img);
    double combined_sim = sift_sim + orb_sim;

    if (this->is_enable_surf) {
        double surf_sim = this->SURFSimilarityScore(prev_img, cur_img);
        combined_sim = (combined_sim + surf_sim) / 3.0;
        return combined_sim;
    }

    return combined_sim / 2.0;
}


bool ImageSimilarityMonitor::IsSimilar(cv::Mat& img_1,cv::Mat& img_2) {
    bool is_img1_dark = this->IsDarkImage(img_1);
    bool is_img2_dark = this->IsDarkImage(img_2);

    if ((is_img1_dark && !is_img2_dark) || (!is_img1_dark && is_img2_dark)) {
        return false;
    }

    this->PrepareImagesForSIFT(img_1, img_2);

    double sift_sim = this->SIFTSimilarityScore(img_1, img_2);
    double combined_sim = sift_sim;

    if (this->is_enable_surf) {
        double surf_sim = this->SURFSimilarityScore(img_1, img_2);
        combined_sim = (combined_sim + surf_sim) / 2.0;
    }

    if (combined_sim >= this->sim_threshold) {
        return true;
    } else {
        return false;
    }
}

void ImageSimilarityMonitor::PrepareImagesForSIFT(cv::Mat& img1, cv::Mat& img2) {
    cv::Size max_size = img1.size();
    double max_area = max_size.height * max_size.width;
    
    cv::Mat img1_modified = img1.clone();
    cv::Mat img2_modified = img2.clone();
    this->PreProcessImage(img1_modified);
    this->PreProcessImage(img2_modified);

    cv::bitwise_not(img1_modified, img1_modified);
    cv::bitwise_not(img2_modified, img2_modified);
    cv::bitwise_and(img1, img1, img1_modified, 255 - img1_modified);
    cv::bitwise_and(img2, img2, img2_modified, 255 - img2_modified);

    cv::cvtColor(img1_modified, img1_modified, cv::COLOR_BGR2GRAY);
    cv::cvtColor(img2_modified, img2_modified, cv::COLOR_BGR2GRAY);

    cv::RotatedRect bbox_1 = this->FindLargestBbox(img1_modified);
    cv::RotatedRect bbox_2 = this->FindLargestBbox(img2_modified);

    bool is_bbox1_valid = this->IsBboxValid(bbox_1, max_area);
    bool is_bbox2_valid = this->IsBboxValid(bbox_2, max_area);

    if (this->IsBboxValid(bbox_1, max_area)) {
        this->WhiteOut(img1, bbox_1);
        this->WhiteOut(img2, bbox_1);   
    }

    if (this->IsBboxValid(bbox_2, max_area)) {
        this->WhiteOut(img1, bbox_2);
        this->WhiteOut(img2, bbox_2);   
    }

    cv::cvtColor(img1, img1, cv::COLOR_BGR2GRAY);
    cv::GaussianBlur(img1, img1, cv::Size(5, 5), 0);

    cv::cvtColor(img2, img2, cv::COLOR_BGR2GRAY);
    cv::GaussianBlur(img2, img2, cv::Size(5, 5), 0);
}

void ImageSimilarityMonitor::WhiteOut(cv::Mat& img, const cv::RotatedRect& bbox) {
    cv::Mat mask = cv::Mat::zeros(img.size(), CV_8U);

    // Get the points of the rotated rectangle
    cv::Point2f points[4];
    bbox.points(points);

    // Convert the points to a vector of cv::Point
    std::vector<cv::Point> contour;
    contour.reserve(4); // Reserve space for 4 points
    for (int i = 0; i < 4; ++i) {
        contour.push_back(points[i]);
    }

    // Create a vector of contours and push the single contour
    std::vector<std::vector<cv::Point>> contours;
    contours.push_back(contour);

    // Draw the filled contour on the mask
    cv::drawContours(mask, contours, 0, cv::Scalar(255), cv::FILLED);

    // Set the region inside the contour to white in the input image
    img.setTo(cv::Scalar(255, 255, 255), mask);
}

bool ImageSimilarityMonitor::IsBboxValid(const cv::RotatedRect& bbox,
                                            const double& max_area) {
    double bbox_area = bbox.size.width * bbox.size.height;
    if (bbox_area == 0) {
        return false;
    }
    if (bbox_area / max_area <= this->valid_bbox_ratio) {
        return true;
    }
    else {
        return false;
    }
}

cv::RotatedRect ImageSimilarityMonitor::FindLargestBbox(const cv::Mat& image) {
    std::vector<std::vector<cv::Point>> contours;
    std::vector<cv::Vec4i> hierarchy;
    cv::findContours(image, contours, hierarchy, 
                        cv::RETR_LIST, cv::CHAIN_APPROX_SIMPLE);

    // Filter to retrieve only the contour with the largest area
    //  ==> assumed to be the target license plate
    double max_area = 0;
    int max_index = 0;
    for (int i=0; i<contours.size(); i++) {
        double area = cv::contourArea(contours[i]);
        if (area > max_area) {
            max_area = area;
            max_index = i;
        }
    }

    if (contours.size() == 0) {
        return cv::RotatedRect();
    }
    else {
        // convert from contour to bounding box
        cv::RotatedRect bbox = cv::minAreaRect(contours[max_index]);
        return bbox;
    }
}

bool ImageSimilarityMonitor::IsDarkImage(const cv::Mat& image) {
    double pixel_mean = this->GetPixelMean(image);

    if (pixel_mean <= this->dark_threshold) {
        return true;
    }
    else {
        return false;
    }
}

double ImageSimilarityMonitor::GetPixelMean(const cv::Mat& image) {
    // Check if the image is loaded successfully
    if (image.empty()) {
        std::cout << "Could not open or find the image." << std::endl;
        return -1;
    }
    
    cv::Mat gray_image;
    if (image.channels() > 1) {
        cv::cvtColor(image, gray_image, cv::COLOR_BGR2GRAY);
    } else {
        gray_image = image.clone();
    }

    // Calculate the mean pixel value
    double pixel_mean = cv::mean(gray_image).val[0];
    return pixel_mean;
}

double ImageSimilarityMonitor::ORBSimilarityScore(const cv::Mat& img_1, 
                                                  const cv::Mat& img_2) {
    cv::Ptr<cv::ORB> orb = cv::ORB::create();

    std::vector<cv::KeyPoint> key_pts_1, key_pts_2;
    cv::Mat descriptor_1, descriptors_2;
    orb->detectAndCompute(img_1, cv::noArray(), key_pts_1, descriptor_1);
    orb->detectAndCompute(img_2, cv::noArray(), key_pts_2, descriptors_2);

    cv::BFMatcher bf_orb(cv::NORM_HAMMING, true);
    std::vector<cv::DMatch> orb_matches;
    bf_orb.match(descriptor_1, descriptors_2, orb_matches);

    double orb_sim = static_cast<double>(orb_matches.size()) / 
                    std::min(key_pts_1.size(), key_pts_2.size());

    return orb_sim;
}

double ImageSimilarityMonitor::SIFTSimilarityScore(const cv::Mat& img_1, 
                                                    const cv::Mat& img_2) {
    cv::Ptr<cv::SIFT> sift = cv::SIFT::create();
    std::vector<cv::KeyPoint> key_pts_1, key_pts_2;

    cv::Mat descriptor_1, descriptors_2;
    sift->detectAndCompute(img_1, cv::noArray(), 
                            key_pts_1, descriptor_1);
    sift->detectAndCompute(img_2, cv::noArray(), 
                            key_pts_2, descriptors_2);

    cv::FlannBasedMatcher flann_sift;
    std::vector<std::vector<cv::DMatch>> sift_matches;
    flann_sift.knnMatch(descriptor_1, descriptors_2, 
                        sift_matches, 2);

    std::vector<cv::DMatch> sift_good_matches;
    for (size_t i = 0; i < sift_matches.size(); ++i) {
        if (sift_matches[i][0].distance < 0.75 * sift_matches[i][1].distance) {
            sift_good_matches.push_back(sift_matches[i][0]);
        }
    }

    double sift_sim = static_cast<double>(sift_good_matches.size()) / 
                        std::min(key_pts_1.size(), key_pts_2.size());
    return sift_sim;
}

double ImageSimilarityMonitor::SURFSimilarityScore(const cv::Mat& img_1, 
                                                    const cv::Mat& img_2) {
    cv::Ptr<cv::xfeatures2d::SURF> surf = cv::xfeatures2d::SURF::create(400);

    std::vector<cv::KeyPoint> key_pts_1, key_pts_2;
    cv::Mat descriptor_1, descriptors_2;
    surf->detectAndCompute(img_1, cv::noArray(), 
                            key_pts_1, descriptor_1);
    surf->detectAndCompute(img_2, cv::noArray(), 
                            key_pts_2, descriptors_2);

    // Create a FLANN-based matcher for SURF
    cv::FlannBasedMatcher flann_surf;
    std::vector<std::vector<cv::DMatch>> surf_matches;
    flann_surf.knnMatch(descriptor_1, descriptors_2, 
                        surf_matches, 2);

    // Apply Lowe's ratio test to filter good matches for SURF
    std::vector<cv::DMatch> surf_good_matches;
    for (size_t i = 0; i < surf_matches.size(); ++i) {
        if (surf_matches[i][0].distance < 0.7 * surf_matches[i][1].distance) {
            surf_good_matches.push_back(surf_matches[i][0]);
        }
    }

    double surf_sim = static_cast<double>(surf_good_matches.size()) / 
                            std::min(key_pts_1.size(), key_pts_2.size());
    return surf_sim;
}

cv::Mat ImageSimilarityMonitor::GammaCorrection(const cv::Mat& src, 
                                                const float& gamma) {
    cv::Mat dst;
    if (src.empty()) {
        std::string msg = "Source Image has to be not empty";
        throw std::domain_error(msg);
    }

    if (gamma <= 0) {
        std::string msg = "Gamma value has to be positive (current gamma <= 0)";
        throw std::domain_error(msg);
    }

    if (gamma == 1) {
        return src;
    }

    float inv_gamma = 1 / gamma;
    cv::Mat table(1, 256, CV_8U);
    uchar *p = table.ptr();
    for (int i = 0; i < 256; ++i) {
        p[i] = (uchar) (pow(i / 255.0, inv_gamma) * 255);
    }

    cv::LUT(src, table, dst);
    return dst;
}

void ImageSimilarityMonitor::DilateImage(cv::Mat& src) {
    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, 
                                                cv::Size(5,5), 
                                                cv::Point(1,1));
    cv::dilate(src, src, kernel);
}

void ImageSimilarityMonitor::PreProcessImage(cv::Mat& image) {
    if (image.empty()) {
        return;
    }

    std::vector<std::vector<cv::Point>> contours;
    std::vector<cv::Vec4i> hierarchy;
    cv::Mat gray_image, gamma_corrected_image, bw_image, 
                    dilated_image, erode_image;

    cv::cvtColor(image, gray_image, cv::COLOR_BGR2GRAY);                  

    float pixel_mean = cv::mean(gray_image).val[0];

    if (pixel_mean <= 1) {
        return;
    }

    float gamma_val = std::log(128) / std::log(pixel_mean);
    gamma_corrected_image = this->GammaCorrection(gray_image, gamma_val);

    cv::threshold(gamma_corrected_image, bw_image, 0, 255, cv::THRESH_OTSU);

    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, 
                                                cv::Size(5,5), 
                                                cv::Point(1,1));
    cv::dilate(bw_image, image, kernel);
}
