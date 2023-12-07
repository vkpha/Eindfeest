from solar.model.solar_experiment import SolarExperiment, list_devices
import matplotlib.pyplot as plt

print(list_devices())
experiment = SolarExperiment()

experiment.scan("ASRL::SIMPV::INSTR")
plt.plot(experiment.pv_voltages, experiment.currents, ".")
