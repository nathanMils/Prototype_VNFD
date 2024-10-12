class UEDevice:
    def __init__(self, name, ip_address, interface):
        self.name = name
        self.ip_address = ip_address
        self.interface = interface

    def __str__(self):
        return f"UE Device(name={self.name}, ip_address={self.ip_address}), interface={self.interface}"