cmake_minimum_required(VERSION 3.20)
project(httpaceproxycpp VERSION 4.0.4 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(HTTPACEPROXYCPP_BUILD_TESTS "Build tests" ON)

find_package(Threads REQUIRED)
find_package(CURL REQUIRED)
find_package(ZLIB REQUIRED)

add_library(httpaceproxycpp_core
  src/ace_client.cpp
  src/broadcast.cpp
  src/config.cpp
  src/http_client.cpp
  src/http_server.cpp
  src/json.cpp
  src/playlist.cpp
  src/plugins.cpp
  src/proxy.cpp
  src/util.cpp
)

target_include_directories(httpaceproxycpp_core
  PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(httpaceproxycpp_core
  PUBLIC
    CURL::libcurl
    ZLIB::ZLIB
    Threads::Threads
)

if(APPLE)
  target_compile_definitions(httpaceproxycpp_core PUBLIC HTTPACEPROXYCPP_APPLE=1)
endif()

add_executable(httpaceproxycpp src/main.cpp)
target_link_libraries(httpaceproxycpp PRIVATE httpaceproxycpp_core)

if(HTTPACEPROXYCPP_BUILD_TESTS)
  enable_testing()
  add_executable(httpaceproxycpp_tests tests/test_core.cpp)
  target_link_libraries(httpaceproxycpp_tests PRIVATE httpaceproxycpp_core)
  add_test(NAME httpaceproxycpp_tests COMMAND httpaceproxycpp_tests)
endif()
