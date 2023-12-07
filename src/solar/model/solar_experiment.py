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


class SolarExperiment:
    def __init__(self) -> None:
        self.clear()

    def scan(self, start=0, stop=3.3):
        pass

    def clear(self):
        self.pv_voltages = []
