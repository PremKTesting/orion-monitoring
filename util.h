//
// Created by anil on 4/2/23.
//

#ifndef ORION_MONITORING_ORION_MONITORING_UTIL_H_
#define ORION_MONITORING_ORION_MONITORING_UTIL_H_
#include <iostream>
#include <fstream>
#include <mutex>
#include <experimental/filesystem>
#include <boost/algorithm/string.hpp>
#include <yaml-cpp/yaml.h>
#include "date.h"

static std::string kDatetimeFormat = "%04d-%02d-%02d_%02d-%02d-%02d.%03d";
static std::string kDatetimeParseFormat = "%Y-%m-%d_%H-%M-%S";
static const int KNanoToMilliDivisor = 1000000;

namespace fs = std::experimental::filesystem;
typedef std::chrono::high_resolution_clock CLK;
typedef std::chrono::system_clock::time_point CLK_TP;

namespace orion::util{
  /**
   * Read the orion configuration global.yaml file.
   * @param filename
   * @return
   */
  YAML::Node ReadConfiguration(const std::string& filename);
  
  /**
     * Check for existence of a file system.
     * @param filename
     * @return
     */
  bool FileExist(const std::string filename);
  
  /**
   * Execute shell command and return the output in string.
   * @param command
   * @return
   */
  std::string ExecuteCommand(const std::string command);
  
  /**
   * Get hostname of the device
   * @return
   */
  std::string GetHostName();

  std::string CurrentDate();
  
  std::string CurrentDateTime();

  CLK::time_point ParseStringToTimePoint(std::string timestamp,
                                         std::string format = kDatetimeParseFormat);

  std::vector<std::string> SplitString(const std::string& input,
                                       const std::string& separator_chars);

  std::vector<std::string_view> SplitStringView(std::string_view input, 
                     std::string_view separators);
}
#endif //ORION_MONITORING_ORION_MONITORING_UTIL_H_
