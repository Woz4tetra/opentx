#!/bin/bash
BASE_DIR=$(realpath "$(dirname "${0}")")
docker run --rm -it -e "BOARD_NAME=tx16s"  -e "CMAKE_FLAGS=USB_SERIAL=YES CLI=YES DEBUG=YES" -v "${BASE_DIR}:/opentx" vitass/opentx-fw-build
