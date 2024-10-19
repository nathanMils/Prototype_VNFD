#!/bin/bash

openstack flavor create elk_basic --ram 4096 --disk 50 --vcpus 4
openstack flavor create elk_norm --ram 8192 --disk 100 --vcpus 4
openstack flavor create nf_basic --ram 2048 --disk 10 --vcpus 2
openstack flavor create nf_heavy --ram 4096 --disk 20 --vcpus 3
openstack flavor create ueransim_basic --ram 4096 --disk 20 --vcpus 3
openstack flavor create vpp_upf --ram 4096 --disk 10 --vcpus 6
openstack flavor create nf_light --ram 1024 --disk 5 --vcpus 1