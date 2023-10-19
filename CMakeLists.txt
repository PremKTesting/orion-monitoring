cmake_minimum_required(VERSION 3.17)
set(PROJECT_NAME orion-monitoring)
project(${PROJECT_NAME})
message(STATUS "Building: ${PROJECT_NAME}")

include(cmake/set_ifndef.cmake)
set(CMAKE_BUILD_TYPE Release)
set(CMAKE_C_COMPILER gcc PARENT_SCOPE)
set(CMAKE_CXX_COMPILER g++ PARENT_SCOPE)
set(CMAKE_CXX_STANDARD 17 PARENT_SCOPE)
set(CMAKE_CXX_FLAGS " -std=c++17 -Wno-dev ")
set(DEFAULT_OPENCV_VERSION 4.4.0)
set(DEFAULT_CUDA_VERSION 10.2)
set(DEFAULT_YAML_VERSION 0.6.3)
link_libraries(stdc++fs)

set_ifndef(CUDA_VERSION ${DEFAULT_CUDA_VERSION})
set(DEFAULT_CUDA_INSTALL_DIR "/usr/local/cuda-${CUDA_VERSION}")
set_ifndef(CUDA_INSTALL_DIR ${DEFAULT_CUDA_INSTALL_DIR})
set_ifndef(OPENCV_VERSION ${DEFAULT_OPENCV_VERSION})
set_ifndef(YAML_VERSION ${DEFAULT_YAML_VERSION})
set(CUDA_TOOLKIT_ROOT_DIR ${CUDA_INSTALL_DIR})

include(cmake/dependencies.cmake)

add_executable(${PROJECT_NAME} main.cc
        date.h util.h util.cc
        aws_client_helper.h aws_client_helper.cc
        cloud_watch_client.h cloud_watch_client.cc
        temp_monitor.h temp_monitor.cc
        service_monitor.h service_monitor.cc
        image_sim_monitor.h image_sim_monitor.cc)

include_directories(BEFORE SYSTEM ${yaml-cpp_SOURCE_DIR}/include)

target_link_libraries(${PROJECT_NAME} ${AWSSDK_LINK_LIBRARIES})
target_link_libraries(${PROJECT_NAME} ${OpenCV_LIBS})
target_link_libraries(${PROJECT_NAME} yaml-cpp)
