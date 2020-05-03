import socket, struct


class GetPrimaryIp(object):
    def __init__(self):
        self.mode = 0

    def get_default_gateway_linux(self):
        """Read the default gateway directly from /proc."""
        with open("/proc/net/route") as fh:
            for line in fh:
                fields = line.strip().split()
                print(fields)
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue

                return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

    def get_primary_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except:
            ip = "127.0.0.1"
        finally:
            s.close()

        return ip

    def main(self):
        ip = self.get_primary_ip()
        print(self.get_default_gateway_linux())
        print(ip)


# you can run this function from command line and this will catch it
if __name__ == "__main__":
    GetPrimaryIp().main()
