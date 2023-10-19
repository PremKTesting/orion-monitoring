//
// Created by anil on 4/2/23.
//

#ifndef ORION_MONITORING_ORION_MONITORING_THERMAL_MONITOR_TEMP_MONITOR_H_
#define ORION_MONITORING_ORION_MONITORING_THERMAL_MONITOR_TEMP_MONITOR_H_
#include <iostream>
#include <string>
#include "util.h"

static const std::string kCpuTempFile = "/sys/devices/virtual/thermal/thermal_zone0/temp";
static const std::string kGpuTempFile = "/sys/devices/virtual/thermal/thermal_zone1/temp";

namespace orion::monitor {
  struct Temp {
    double cpu;
    double gpu;
  };

  class TempMonitor {
   public:
    Temp GetTempInfo();
  };
}
#endif //ORION_MONITORING_ORION_MONITORING_THERMAL_MONITOR_TEMP_MONITOR_H_
