# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "C:/Espressif/frameworks/esp-idf-v5.1.1/components/bootloader/subproject"
  "D:/workspace/thermocouple/build/bootloader"
  "D:/workspace/thermocouple/build/bootloader-prefix"
  "D:/workspace/thermocouple/build/bootloader-prefix/tmp"
  "D:/workspace/thermocouple/build/bootloader-prefix/src/bootloader-stamp"
  "D:/workspace/thermocouple/build/bootloader-prefix/src"
  "D:/workspace/thermocouple/build/bootloader-prefix/src/bootloader-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "D:/workspace/thermocouple/build/bootloader-prefix/src/bootloader-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "D:/workspace/thermocouple/build/bootloader-prefix/src/bootloader-stamp${cfgdir}") # cfgdir has leading slash
endif()
