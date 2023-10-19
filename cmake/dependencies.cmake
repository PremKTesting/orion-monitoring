message(STATUS "Linking YAML")
# ============= YAML ========================
set(YAML_CPP_BUILD_TESTS OFF CACHE BOOL "disable tests inside yaml library" FORCE)
include(FetchContent)
FetchContent_Declare(
        yaml-cpp
        GIT_REPOSITORY https://github.com/jbeder/yaml-cpp.git
        GIT_SHALLOW	ON
        GIT_TAG yaml-cpp-${YAML_VERSION}
)
FetchContent_MakeAvailable(yaml-cpp)
FetchContent_GetProperties(yaml-cpp)
if(NOT yaml-cpp_POPULATED)
    message(STATUS "Fetching yaml-cpp from github")
    FetchContent_Populate(yaml-cpp)
    message(STATUS "yaml-cpp is configured")
endif()
message(STATUS "YAML INCLUDE ${yaml-cpp_SOURCE_DIR}")

message(STATUS "AWS CloudWatch")
# ============ Cloud Watch ==============================
find_package(AWSSDK REQUIRED COMPONENTS monitoring events logs s3)
if(AWSSDK_FOUND)
    message(STATUS "AWS SDK cloud watch is available!")
endif()

# ============= OPENCV ========================
message(STATUS "OpenCV")
if(NOT DEFINED CMAKE_TOOLCHAIN_FILE)
    find_package(OpenCV ${OPENCV_VERSION} REQUIRED)
endif()
