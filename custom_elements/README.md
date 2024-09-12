# Efficiency Improvements in Prototype Version 4
In Prototype Version 4, we have made significant improvements to efficiency by running Zeek and Filebeat directly in the virtual machine (VM) instead of using containers within the VM. This change brings several benefits:

- Improved Efficiency: Running Zeek and Filebeat directly in the VM eliminates the overhead associated with containerization, leading to better performance.

- Reduced Disk Space Usage: Since we no longer need to copy a tar file containing Docker images onto the disk, the required disk space is significantly reduced.

- Faster Uptime: The most notable improvement is the reduction in uptime. Without the need to pull and extract Docker images for Filebeat and Zeek, the system can start up much more quickly.

- Seperation between elk and prototype: Since filebeat and zeek are not needed at the node running elk, a seperate elk image will be used, this improves efficiency at ELK aswell.

These changes collectively enhance the overall performance and responsiveness of the system, making Prototype Version 4 more efficient and effective.

