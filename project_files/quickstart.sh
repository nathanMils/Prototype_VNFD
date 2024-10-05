#!/bin/bash

set -e  # Exit on error

# Source admin-openrc in user_files directory
(
    cd user_files
    . admin-openrc
)

# Register VIM in vims/local_vim directory
(
    cd vims/local_vim
    ./register_vim.sh
)

# Add flavors in flavors directory
(
    cd flavors
    ./add_flavors.sh
)
