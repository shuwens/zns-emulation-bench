#!/usr/bin/env bash
set -xeuo pipefail
# go install github.com/markhpc/hsbench@latest

#
# Zstore
#
# PUT: , GET:
# hsbench -a test -s test -u http://12.12.12.1:2000 -z 4K -d 1 -t 10 -b 1
# PUT: , GET:
# hsbench -a test -s test -u http://12.12.12.1:2000 -z 4K -d 5 -t 10 -b 1

# hsbench -a test -s test -u http://12.12.12.1:2000 -z 4K -d 1 -t 5 -b 1


# microceph

hsbench -a minioadmin -s admin123 \
	-u http://12.12.12.2:9000 -z 4K -d 10 -t 20 -b 1

# hsbench -a 50I9XIIDPA2TC8LKYUKM -s J10qS4Bb4vIWxyJW3gWR4XATae0AbhRovkiiTOkj \
# 	-u http://12.12.12.2:80 -z 4K -d 10 -t 50 -b 1

# TO RUN
# hsbench -a test -s test -u http://12.12.12.1:2000 -z 4K -d 10 -t 80 -b 1



# hsbench -a minioadmin -s redbull64 -u http://localhost:9000 -z 4K -d 1 -t 1 -b 1


# hsbench -a 3JZ0SVK94Z55OZU5J1N0 -s OdzEPyDDZ0ls1haDUu1NVWkJDcnG74Lb7XylfXRM -u http://12.12.12.1:2000 -z 4K -d 10 -t 10 -b 10
# hsbench -a test -s test -u http://12.12.12.1:2000 -z 4K -d 1 -t 1 -b 1
