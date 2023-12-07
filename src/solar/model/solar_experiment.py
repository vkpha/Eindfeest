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
from solar.controller.arduino_device import ArduinoVISADevice, list_devices
import numpy as np
from rich.progress import track


class SolarExperiment:
    def __init__(self) -> None:
        self.clear()

    def get_resistance(self, port):
        device = ArduinoVISADevice(port)
        U_tot = device.get_input_voltage(channel=1) * 3
        U2 = device.get_input_voltage(channel=2)
        U_r = U_tot - U2

    def scan(self, port, start=0, stop=3.3, sample_size=5) -> None:
        # connect to controller and convert inputs
        self.device = ArduinoVISADevice(port)
        start = self.device.analog_to_digital(start)
        stop = self.device.analog_to_digital(stop)

        # Clear old results
        self.clear()

        # scan over the requested range
        for value in track(range(start, stop + 1)):
            self.device.set_output_value(value)
            pv_volt = []
            I_volt = []
            fet_voltage = []
            current = []
            pv_power = []
            for _ in range(sample_size):
                # Remember to multiply with three for the total voltage
                pv_volt.append(self.device.get_input_voltage(channel=1) * 3)
                I_volt.append(self.device.get_input_voltage(channel=2))

            # Add results
            self.pv_voltages.append(np.mean(pv_volt))
            self.pv_voltages_err.append(np.std(pv_volt) / np.sqrt(sample_size))

            self.I_voltages.append(np.mean(I_volt))
            self.I_voltages_err.append(np.std(I_volt) / np.sqrt(sample_size))

            self.fet_voltages.append(np.mean(pv_volt) - np.mean(I_volt))
            self.fet_voltages_err.append(
                (
                    (np.std(pv_volt) / np.sqrt(sample_size)) ** 2
                    + (np.std(I_volt) / np.sqrt(sample_size)) ** 2
                )
            )

            self.currents.append(np.mean(I_volt) / 4.7)
            self.currents_err((np.std(I_volt) / np.sqrt(sample_size)) / 4.7)

            # self.pv_powers.append(pv_power)

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
        self.pv_voltages_err = []
        self.currents = []
        self.currents_err = []
        self.fet_voltages = []
        self.fet_voltages_err = []
        # self.pv_powers = []
        # self.pv_powers_err = []
        self.I_voltages = []
        self.I_voltages_err = []
