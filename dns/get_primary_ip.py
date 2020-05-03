import socket, struct, fcntl


class GetPrimaryIp(object):
    def __init__(self):
        self.mode = 0

    def get_default_gateway_linux(self):
        """Read the default gateway directly from /proc."""
        with open("./test.log") as fh:
            for line in fh:
                fields = line.strip().split()
                print(fields)
                if fields[0] != 'Iface':
                    print(socket.inet_ntoa(struct.pack("<L", int(fields[1], 16))))
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue

                # return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

    def get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        buffer = fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s',
                        bytes(ifname[:15], 'utf-8'))
        )[20:24]

        return socket.inet_ntoa(buffer)

    def main(self):
        ip = self.get_ip_address('enp11s0')
        print(ip)


# you can run this function from command line and this will catch it
if __name__ == "__main__":
    GetPrimaryIp().main()
