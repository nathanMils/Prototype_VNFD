#!/bin/bash

# Exit on error
set -e

echo "Running fix!"
./fix.sh

echo "Starting Openstack!"
$DEVSTACK_ROOT/devstack/stack.sh

echo "Register Local VIM!"
./register.sh

echo "Success!"
