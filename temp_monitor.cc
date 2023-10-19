//
// Created by anil on 4/2/23.
//

#include "temp_monitor.h"

using namespace orion::monitor;
using namespace orion::util;

Temp TempMonitor::GetTempInfo() {
  Temp temp{};
  try {
    std::string cpu_temp_str = "0";
    std::string gpu_temp_str = "0";

    if (FileExist(kCpuTempFile)){
      cpu_temp_str = ExecuteCommand("cat "+kCpuTempFile);
    }
    
    if (FileExist(kGpuTempFile)){
      gpu_temp_str = ExecuteCommand("cat "+kGpuTempFile);
    }

    if (!cpu_temp_str.empty()){
      auto cpu_temp = std::atof(cpu_temp_str.c_str());
      temp.cpu = cpu_temp / 1000;
      temp.cpu = round(temp.cpu * 100.0) / 100.0;
    }

    if (!gpu_temp_str.empty()){
      auto gpu_temp = std::atof(gpu_temp_str.c_str());
      temp.gpu = gpu_temp / 1000;
      temp.gpu = round(temp.gpu * 100.0) / 100.0;
    }
  } catch (std::runtime_error& ex){
    std::cout << "Error - Temp monitoring" << std::endl;
  }

  return temp;
}
