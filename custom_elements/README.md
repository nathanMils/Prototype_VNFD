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


These uses make UERANSIM an essential tool for advancing the development, testing, and deployment of 5G networks in Prototype Version 5.

# Version 6: Updated Configuration options
Added ELK enabled and disabled varients for benchmarking, updated UERANSIM update to create various traiffic types. I also added health checks and a more automated deployment variant. Lastly an extensive resource collection script. 

## Added Ostinato
Ostinato is a powerful network traffic generator and analyzer that consists of two main components: the Ostinato Drone and the Ostinato Controller.

### Ostinato Drone

The Ostinato Drone is a lightweight, high-performance traffic generator that runs on network devices. It is responsible for generating and capturing network traffic based on the instructions received from the Ostinato Controller. Key features of the Ostinato Drone include:

- **High Performance**: Capable of generating traffic at high speeds, making it suitable for performance testing and benchmarking.
- **Flexibility**: Supports a wide range of network protocols and traffic patterns, allowing for comprehensive testing scenarios.
- **Scalability**: Multiple drones can be deployed across different network segments to simulate large-scale network environments.

### Ostinato Controller

The Ostinato Controller is a graphical user interface (GUI) application that allows users to configure and manage the Ostinato Drones. It provides an intuitive interface for creating and managing traffic generation scenarios. Key features of the Ostinato Controller include:

- **User-Friendly Interface**: Easy-to-use GUI for configuring traffic generation parameters and monitoring traffic in real-time.
- **Comprehensive Traffic Configuration**: Supports detailed configuration of packet headers, payloads, and traffic patterns.
- **Real-Time Monitoring**: Provides real-time statistics and analysis of generated traffic, helping users to quickly identify and troubleshoot issues.

These components make Ostinato a versatile and powerful tool for network testing, performance evaluation, and troubleshooting in Prototype Version 6.

## Added mutual HTTPS between Filebeat and Logstash
To enhance security and ensure data integrity, mutual HTTPS has been implemented between Filebeat and Logstash. This setup involves the following key aspects:

- **Mutual Authentication**: Both Filebeat and Logstash authenticate each other using SSL/TLS certificates, ensuring that data is exchanged only between trusted entities.

- **Data Encryption**: All data transmitted between Filebeat and Logstash is encrypted, protecting it from eavesdropping and tampering during transit.

- **Certificate Management**: Proper management of SSL/TLS certificates is crucial. This includes generating, distributing, and renewing certificates to maintain a secure communication channel.

- **Configuration**: Both Filebeat and Logstash need to be configured to use the appropriate certificates and keys for mutual HTTPS. This involves updating their respective configuration files to specify the paths to the certificate and key files.

Implementing mutual HTTPS between Filebeat and Logstash significantly enhances the security of the data pipeline, ensuring that logs are transmitted securely and reliably in Prototype Version 6.

## Added Data at Rest Encryption using DM-Crypt
To further enhance the security of the system, data at rest encryption has been implemented using DM-Crypt. This ensures that all data stored on disk is encrypted, providing an additional layer of protection against unauthorized access. Key aspects of this implementation include:

- **Docker Volume Encryption**: DM-Crypt provides full disk encryption, ensuring that all data on the disk is encrypted, including system files, user data, and swap space.

- **Transparent Encryption**: The encryption and decryption processes are transparent to applications and users, meaning that no changes are required to existing applications to benefit from the encryption.

- **Performance Considerations**: While encryption adds some overhead, DM-Crypt is designed to minimize performance impact, leveraging hardware acceleration where available.

- **Key Management**: Proper key management is crucial for maintaining the security of encrypted data. This includes securely storing encryption keys and implementing key rotation policies.

- **Configuration**: Setting up DM-Crypt involves configuring the system to use encrypted partitions. This typically includes updating the system's boot configuration and ensuring that the necessary encryption modules are loaded.

Implementing data at rest encryption using DM-Crypt significantly enhances the security of the system, ensuring that sensitive data is protected even if the physical storage media is compromised in Prototype Version 6.

## Added HTTP/2 log analysis
I am too tired to add more details