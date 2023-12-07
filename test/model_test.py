from solar.model.solar_experiment import SolarExperiment
import matplotlib.pyplot as plt

experiment = SolarExperiment()
experiment.scan(port="ASRL::SIMPV::INSTR")

U_data = experiment.pv_voltages
I_data = experiment.currents

plt.plot(U_data, I_data)
