"""
Snelle omschrijving,

Channel 0 > controleert de mosfet
Channel 1 > meet de spaning over de zonnecel (mind 3:1 volt splitter)
Channel 2 > used to calculate current 

set channel 0 to controller mosfet and set resistance on PV cell
measure channel 1 and multiply with 3 to get total volt on PV cell
measure channel 2 and 
    > use the 4.7 ohm resistor to get the current
    >> subtract the channel 2 from channel 1 to get MOSFET voltage
    >> Use this to the MOSFET resistance or PV power
"""

from controller.arduino_device import ArduinoVISADevice, list_devices


class SolarExperiment:
    def __init__(self) -> None:
        self.clear()

    def get_resistance(self, port):
        device = ArduinoVISADevice(port)
        U_tot = device.get_input_voltage(channel=1) * 3
        U2 = device.get_input_voltage(channel=2)
        U_r = U_tot - U2

    def scan(self, port, start=0, stop=3.3, sample_size=5) -> dict:
        # connect to controller and convert inputs
        self.device = ArduinoVISADevice(port)
        start = self.device.analog_to_digital(start)
        stop = self.device.analog_to_digital(stop)

        # scan over the requested range
        for value in range(start, stop + 1):
            self.device.set_output_value(value)
            # Remember to multiply with three for the total voltage
            pv_volt = self.device.get_input_voltage(channel=1) * 3
            I_volt = self.device.get_input_voltage(channel=0)
            current = I_volt / 4.7

            pass

        self.device.close_device()

    def get_identification(self, port):
        """Get the identification of the device.

        Returns:
            string: the identification string
        """
        device = ArduinoVISADevice(port)
        return device.get_indentification()

    def close(self, port):
        """Close device"""
        device = ArduinoVISADevice(port)
        device.close_device()

    def clear(self):
        self.pv_voltages = []
        self.currents = []
        self.fet_voltages = []
        self.pv_powers = []
        self.I_voltages = []
