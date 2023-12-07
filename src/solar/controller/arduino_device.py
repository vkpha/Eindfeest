# This is the controller class. We communicate with the device and return to model class.

try:
    from nsp2visasim import sim_pyvisa as pyvisa
except ModuleNotFoundError:
    import pyvisa


class ArduinoVISADevice:
    """Control class used to send queries to the arduino."""

    def __init__(self, port):
        # Connect with device
        rm = pyvisa.ResourceManager("@py")
        self.device = rm.open_resource(
            port, read_termination="\r\n", write_termination="\n"
        )

    # Different functions to send queries to device
    def get_indentification(self):
        """Get the port identification of the device.

        Returns:
            string: port identification of the device
        """
        return self.device.query("*IDN?")

    def set_output_value(self, value):
        """Set the output value of the device on channel 0.

        Args:
            value (int): value that is set on channel 0
        """
        self.device.query(f"OUT:CH0 {value}")

    def get_output_value(self):
        """Get the current output value on channel 0.

        Returns:
            int: the current output value on channel 0
        """
        return int(self.device.query(f"OUT:CH0?"))

    def get_input_value(self, channel):
        """Get the input value on the given channel.

        Args:
            channel (int): the channel for which the input value is called

        Returns:
            int: the current input value on the given channel
        """
        return int(self.device.query(f"MEAS:CH{channel}?"))

    def get_input_voltage(self, channel):
        """Get the input voltage on the given channel.

        Args:
            channel (int): the channel for which the input voltage is called

        Returns:
            float: the current input voltage on the given channel
        """
        return float(self.get_input_value(channel) * (3.3 / 1023))

    def analog_to_digital(self, voltage):
        """Convert given voltage to digital integer value.

        Args:
            voltage (float): the given analog voltage

        Returns:
            int: the corresponding digital value
        """
        return round(voltage / 3.3 * 1023)

    def digital_to_analog(self, value):
        """Convert given digital integer to analog voltage.

        Args:
            value (int): the given digital value

        Returns:
            float: the corresponding analog voltage
        """
        return value / 1023 * 3.3

    def close_device(self):
        self.device.close()


# List devices out of class to know which port to use
def list_devices():
    rm = pyvisa.ResourceManager("@py")
    return rm.list_resources()
