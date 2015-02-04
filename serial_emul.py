class Serial:
    def __init__(self, port_name):
        self.port_name = port_name
        print('Device at ', port_name)

    def write(self, data):
        # print('Recieved: ', data)
        # print('Recived at ', self.port_name)
        return

    def close(self):
        print(self.port_name, ' is closed!')