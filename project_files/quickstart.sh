#!/bin/bash

set -e  # Exit on error

cd user_files
. admin-openrc
cd -
cd ./vims/local_vim
./register_vim.sh
cd -
