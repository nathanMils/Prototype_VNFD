#!/bin/bash
set -e

DIR="$(dirname "$(realpath "$0")")"

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <vnfd_name>"
    exit 1
fi

VNF_NAME="$1"


VNF_DIR="$DIR/${VNF_NAME}_VNFD"

if [ ! -d "$VNF_DIR" ]; then
    echo "VNFD folder '$VNF_DIR' does not exist."
    exit 1
fi

PACKAGE_SCRIPT="$VNF_DIR/package.sh"

if [ ! -f "$PACKAGE_SCRIPT" ]; then
    echo "Package script '$PACKAGE_SCRIPT' does not exist."
    exit 1
fi

echo "Executing package script for $VNF_NAME..."
bash "$PACKAGE_SCRIPT"
