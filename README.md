# VNFD Prototype for Tacker

This is designed to build a prototype Virtual Network Function Descriptor (VNFD) for Tacker, an OpenStack project for NFV orchestration.

## VNFD Structure

- `BaseHOT/`: Contains base Heat Orchestration Templates (HOT).
- `Definitions/`: Contains TOSCA definitions and downloaded YAML files.
- `Files/`: Contains additional files required for the VNFD.
- `Scripts/`: Contains shell scripts for configuring various components.
- `TOSCA-Metadata/`: Contains the `TOSCA.meta` file with metadata about the VNFD package.
- `UserData/`: Contains user data scripts and configurations.

## Other
- `Requests/`: Contains JSON for tacker operations.
- `PlantUML/`: Contains PlantUML diagrams for the VNFD and flavours.

## Flavours

- `Nginx Option/nginx_opt`: Intended to capture internal HTTP/HTTPS traffic between 5G network functions (Inline).
- `Suricata Option/suricata_opt`: Intended to capture network level information from consumer traffic for UPF function (Inline)(Most generic).
- `Zeek Option/zeek_opt`: Intended for a more reactive approach where inline is not possible or Network Function is unknown (Not Inline).

## Scripts

### `package.sh`

This script performs the following tasks:
1. Calculates the SHA-256 hash of each script file in the `Scripts/` directory.
2. Replaces the placeholder hash values in the `TOSCA-Metadata/TOSCA.meta` file.
3. Downloads the required TOSCA definitions into the `Definitions/` directory.
4. Zips the specified directories into a single VNFD package.

### Usage

```sh
./package.sh