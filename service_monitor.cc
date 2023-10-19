//
// Created by anil on 4/2/23.
//

#include "service_monitor.h"


using namespace orion::monitor;
using namespace orion::util;

Service ServiceMonitor::GeServiceInfo(const std::string& name) {
  Service service{};
  service.name = name;
  try{
    std::string is_active = ExecuteCommand("systemctl is-active "+name);
    if (is_active == kServiceActiveTag){
      service.is_active = 1;
    }
    std::string is_enabled = ExecuteCommand("systemctl is-enabled "+name);
    if (is_enabled == kServiceEnabledTag){
      service.is_enabled = 1;
    }
  } catch (std::runtime_error& ex){}
 
  return service;
}
