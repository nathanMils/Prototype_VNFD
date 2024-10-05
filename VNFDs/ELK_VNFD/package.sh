#!/bin/bash
set -e  # Exit on error
zip -r vnfd_package.zip TOSCA-Metadata/TOSCA.meta Definitions/ BaseHOT/ UserData/
