//
// Created by anil on 4/2/23.
//
#include "util.h"

YAML::Node orion::util::ReadConfiguration(const std::string& filename) {
  std::cout << "Reading Orion config " << filename << std::endl;
  YAML::Node config = YAML::LoadFile(filename);
  return config;
}

std::string orion::util::ExecuteCommand(const std::string command) {
  char buffer[128];
  std::string result;
  
  FILE* pipe = popen(command.c_str(), "r");
  if (!pipe) {
    return "popen failed!";
  }
  
  while (!feof(pipe)) {
    if (fgets(buffer, 128, pipe) != NULL)
      result += buffer;
  }
  
  pclose(pipe);
  boost::trim(result);
  return result;
}

bool orion::util::FileExist(const std::string filename) {
  return fs::exists(fs::path(filename));;
}

std::string orion::util::GetHostName() {
  static std::once_flag stc_flag;
  static char stc_hostname[1024];
  std::call_once(stc_flag, [](){
    if (::gethostname(stc_hostname, sizeof(stc_hostname))) {
      // non-zero means failure.
      std::strncpy(stc_hostname, "hostname_not_available", sizeof(stc_hostname));
    }
  });
  return stc_hostname;
}

CLK::time_point orion::util::ParseStringToTimePoint(std::string timestamp,
                                                    std::string format){
  std::istringstream date_time(timestamp);
  CLK::time_point time_point;
  date_time >> date::parse(format, time_point);
  return time_point;
}

std::string orion::util::CurrentDateTime() {
  struct tm ymdhms;
  struct timespec tspec;
  clock_gettime(CLOCK_REALTIME, &tspec);
  localtime_r(&tspec.tv_sec, &ymdhms);
  auto msecs = (int)(tspec.tv_nsec / KNanoToMilliDivisor);
  static const int buflen = 29; // enough for msecs
  char buf[buflen] = {};
  int nc = snprintf(
      buf, (size_t)buflen, kDatetimeFormat.c_str(),
      ymdhms.tm_year + 1900, ymdhms.tm_mon + 1, ymdhms.tm_mday,
      ymdhms.tm_hour, ymdhms.tm_min, ymdhms.tm_sec, msecs);
  return std::string(buf);
}

std::vector<std::string_view> orion::util::SplitStringView(std::string_view input, 
                     std::string_view separators) {
  std::vector<std::string_view> results;
  size_t start = 0;
  size_t end = 0;

  while (end != std::string_view::npos)
  {
    end = input.find_first_of(separators, start);
    results.emplace_back(input.substr(start, end - start));

    if (end != std::string_view::npos)
    {
      start = end + 1;
    }
  }

  return results;
}

std::vector<std::string> orion::util::SplitString(
  const std::string& input,
  const std::string& separator_chars
) {
  std::vector<std::string> results;
  if (input.empty()) {
    return results;
  }
  if (separator_chars.empty()) {
    throw std::runtime_error("separator_chars can not be empty.");
  }
  std::string_view input_view = input;
  std::string_view separator_chars_view = separator_chars;
  const auto result_views = SplitStringView(input_view,
                                            separator_chars_view);
  results.reserve(result_views.size());
  for (std::string_view result_item_view : result_views) {
    results.emplace_back(result_item_view);
  }
  return results;
}

std::string orion::util::CurrentDate() {
  static const int buflen = 11;
  struct timespec tspec;
  struct tm ymdhms;
  char buf[buflen] = {};
  clock_gettime(CLOCK_REALTIME, &tspec);
  localtime_r(&tspec.tv_sec, &ymdhms);
  int nc = snprintf(
      buf, (size_t)buflen, "%04d-%02d-%02d",
      ymdhms.tm_year + 1900, ymdhms.tm_mon + 1, ymdhms.tm_mday);
  return std::string(buf);
}
