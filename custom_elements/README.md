# Version 4: Efficiency Improvements
In Prototype Version 4, we have made significant improvements to efficiency by running Zeek and Filebeat directly in the virtual machine (VM) instead of using containers within the VM. This change brings several benefits:

- Improved Efficiency: Running Zeek and Filebeat directly in the VM eliminates the overhead associated with containerization, leading to better performance.

- Reduced Disk Space Usage: Since we no longer need to copy a tar file containing Docker images onto the disk, the required disk space is significantly reduced.

- Faster Uptime: The most notable improvement is the reduction in uptime. Without the need to pull and extract Docker images for Filebeat and Zeek, the system can start up much more quickly.

- Seperation between elk and prototype: Since filebeat and zeek are not needed at the node running elk, a seperate elk image will be used, this improves efficiency at ELK aswell.

These changes collectively enhance the overall performance and responsiveness of the system, making Prototype Version 4 more efficient and effective.

# Version 5: Configuration update and further efficiency improvements
Updating to VPP in UPF and Included UERANSIM for traffic generation
## Advantages of Vector Packet Processing (VPP)

Vector Packet Processing (VPP) offers several advantages that contribute to the performance and scalability of network functions:

- **High Performance**: VPP is designed to process packets at high speeds, leveraging modern CPU architectures to achieve line-rate performance.

- **Scalability**: VPP can scale efficiently with the number of CPU cores, making it suitable for both small and large-scale deployments.

- **Flexibility**: VPP supports a wide range of network functions and can be easily extended with plugins to add new features or protocols.

- **Low Latency**: By processing packets in batches (vectors), VPP reduces the per-packet processing overhead, resulting in lower latency.

- **Open Source**: VPP is an open-source project under the FD.io (Fast Data Project) umbrella, which means it benefits from community contributions and continuous improvements.

These advantages make VPP a powerful tool for enhancing the performance and efficiency of network functions in Prototype Version 5.
## Uses of UERANSIM

UERANSIM (User Equipment and Radio Access Network Simulator) is a versatile tool used for simulating 5G networks. It provides several key benefits and use cases:

- **Network Testing**: UERANSIM allows for comprehensive testing of 5G network components, including the core network and radio access network, ensuring they function correctly under various conditions.

- **Performance Evaluation**: By simulating different traffic patterns and loads, UERANSIM helps in evaluating the performance and scalability of 5G network deployments.

- **Development and Debugging**: Developers can use UERANSIM to test new features and debug issues in a controlled environment before deploying them in a live network.

- **Interoperability Testing**: UERANSIM can be used to verify the interoperability of different network components from various vendors, ensuring seamless integration and operation.

- **Educational Purposes**: UERANSIM serves as a valuable educational tool for learning about 5G network architecture, protocols, and operations.

These uses make UERANSIM an essential tool for advancing the development, testing, and deployment of 5G networks in Prototype Version 5.

# Version 6: Updated Configuration options
Added ELK enabled and disabled varients for benchmarking, updated UERANSIM update to create various traiffic types. I also added health checks and a more automated deployment variant. Lastly an extensive resource collection script.