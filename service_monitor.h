//
// Created by anil on 4/2/23.
//

#ifndef ORION_MONITORING_ORION_MONITORING_SERVICE_MONITOR_H_
#define ORION_MONITORING_ORION_MONITORING_SERVICE_MONITOR_H_
#include <iostream>
#include <string>
#include "util.h"

static const std::string kOrionService = "orion.service";
static const std::string kServiceActiveTag = "active";
static const std::string kServiceEnabledTag = "enabled";

namespace orion::monitor {
  struct Service{
    std::string name;
    int is_active = 0;
    int is_enabled = 0;
    
    std::string GetHumanReadableActive(){
      if (is_active){
        return kServiceActiveTag;
      }
      return "in-"+kServiceActiveTag;
    }
  
    std::string GetHumanReadableEnable(){
      if (is_enabled){
        return kServiceEnabledTag;
      }
      return "not-"+kServiceEnabledTag;
    }
  };

  class ServiceMonitor {
   public:
    Service GeServiceInfo(const std::string& name);
  };
}
#endif //ORION_MONITORING_ORION_MONITORING_SERVICE_MONITOR_H_
