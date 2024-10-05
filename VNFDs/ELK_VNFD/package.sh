#!/bin/bash
set -e  # Exit on error
meta_file_path='TOSCA-Metadata/TOSCA.meta'
cp 'TOSCA-Metadata/TOSCA.template.meta' "$meta_file_path"
zip -r vnfd_package.zip TOSCA-Metadata/TOSCA.meta Definitions/ BaseHOT/ UserData/
