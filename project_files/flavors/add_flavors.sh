#!/bin/bash

openstack flavor create elk_basic --ram 4096 --disk 50 --vcpus 4
openstack flavor create elk_norm --ram 8192 --disk 100 --vcpus 4
openstack flavor create nf_basic --ram 2048 --disk 10 --vcpus 2
openstack flavor create nf_heavy --ram 4096 --disk 20 --vcpus 3
openstack flavor create ueransim_basic --ram 4096 --disk 20 --vcpus 3