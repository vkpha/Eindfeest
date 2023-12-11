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
import threading


class SolarExperiment:
    def __init__(self) -> None:
        self.clear()

        # create a threading event to keep track of trackin status
        self.is_scanning = threading.Event()

    def get_connected_devices(self):
        return list_devices()

    def get_resistance(self, port):
        device = ArduinoVISADevice(port)
        U_tot = device.get_input_voltage(channel=1) * 3
        U2 = device.get_input_voltage(channel=2)
        U_r = U_tot - U2

    def scan(self, port, start, stop, sample_size) -> None:
        # connect to controller and convert inputs
        self.device = ArduinoVISADevice(port)
        start = self.device.analog_to_digital(start)
        stop = self.device.analog_to_digital(stop)

        # Update scanning Event
        self.is_scanning.set()

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
                )**0.5
            )

            self.currents.append(np.mean(I_volt) / 4.7)
            self.currents_err.append((np.std(I_volt) / np.sqrt(sample_size)) / 4.7)

            self.pv_powers.append(self.pv_voltages[-1] * self.currents[-1])
            self.pv_powers_err.append(((self.currents[-1]*self.pv_voltages_err[-1])**2+(self.pv_voltages[-1]*self.currents_err[-1])**2)**0.5)
            if self.pv_powers[-1] > self.p_max:
                self.p_max = self.pv_powers[-1]
            self.fet_R.append(self.fet_voltages[-1] / (self.currents[-1]))
            self.fet_R_err.append(((self.fet_voltages_err[-1]/(self.currents[-1]))**2+(self.fet_voltages[-1] * np.log(self.currents[-1]+0.000001) * self.currents_err[-1])**2)**0.5)

            # self.pv_powers.append(pv_power)

        self.device.close_device()
        self.is_scanning.clear()

    def start_scan(self, port, start, stop, N):
        """Function that runs the scan method as a seperate thread

        Args:
            port (string): port of the device controlling the experiment
            start (float, optional): analog voltage at which the experiment starts.
            stop (float, optional): analog voltage at which the experiment stops.
            N (int, optional): number of samples to take at each volatage level.
        """
        self._scan_thread = threading.Thread(
            target=self.scan, args=(port, start, stop, N)
        )
        self._scan_thread.start()

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
        self.pv_powers = []
        self.pv_powers_err = []
        self.I_voltages = []
        self.I_voltages_err = []
        self.fet_R = []
        self.fet_R_err = []
        self.p_max = 0