from solar.model.solar_experiment import SolarExperiment
import matplotlib.pyplot as plt

experiment = SolarExperiment()
experiment.scan(port="ASRL::SIMPV_BRIGHT::INSTR")

U_data = experiment.pv_voltages
I_data = experiment.currents

plt.plot(I_data, U_data, linestyle="None", marker=".")
plt.show()
