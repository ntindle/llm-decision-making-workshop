import simplepyble
from simplepyble import Peripheral

SERVICE_UUID = '1ae49b08-b750-4ef7-afd8-5395763c0da6'
CHARACTERISTIC_UUID = '19b10011-e8f2-537e-4f6c-d104768a1214'

class command_sender:
    def __init__(self, arduino_name: str = 'Arduino_Robotics'):
        self.adapter = self.get_adapter()
        self.peripheral = self.get_peripheral(self.adapter, arduino_name)


    def send_command(self, command: str):
        """
        Sends a command string to the Arduino :param command: A command, formatted as "instruction-value" (e.g.,
        "forward-short"). The bot looks for "forward", "backward", "left", and "right".
        """
        self.peripheral.write_request(SERVICE_UUID, CHARACTERISTIC_UUID, command.encode('ascii', 'replace'))

    def get_adapter(self):
        adapters = simplepyble.Adapter.get_adapters()

        if len(adapters) == 0:
            print("No adapters found")
            return

        if len(adapters) == 1:
            adptr = adapters[0]
        else:
            # Query the user to pick an adapter
            print("Please select an adapter:")
            for i, adptr in enumerate(adapters):
                print(f"{i}: {adptr.identifier()} [{adptr.address()}]")

            choice = int(input("Enter choice: "))
            adptr = adapters[choice]

        adptr.set_callback_on_scan_start(lambda: print("Scanning for bluetooth devices."))
        adptr.set_callback_on_scan_stop(lambda: print("Scan complete."))
        adptr.set_callback_on_scan_found(
            lambda peripheral: print(f"Found {peripheral.identifier()} [{peripheral.address()}]"))
        return adptr

    def get_peripheral(self, adptr, identifier) -> Peripheral:
        peripher = None
        while True:
            # Scan for 5 seconds
            print("Scanning for bluetooth devices for 5 seconds...")
            adptr.scan_for(5000)
            peripherals = adptr.scan_get_results()
            print(f"Found {len(peripherals)} bluetooth devices")
            # # Query the user to pick a peripheral
            # print("Please select a peripheral:")
            # for i, peripheral in enumerate(peripherals):
            #     print(f"{i}: {peripheral.identifier()} [{peripheral.address()}]")
            #
            # choice = int(input("Enter choice or -1 to scan again: "))
            # if choice == -1:
            #     continue
            # peripheral = peripherals[choice]
            for p in peripherals:
                if p.identifier() == identifier:
                    peripher = p
                    break
            if peripher is not None:
                break

        print(f"Connecting to: {peripher.identifier()} [{peripher.address()}]")
        peripher.connect()
        print("Connected to Arduino")
        return peripher

