from solar.model.solar_experiment import SolarExperiment, list_devices
import sys
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Slot, QTimer
import pyqtgraph as pg
import numpy as np
import csv
from PySide6.QtGui import QAction, QIcon


# PyQtGraph global options
pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class UserInterface(QtWidgets.QMainWindow):
    """Creates user interface.

    Args:
        QtWidgets (class): default class to create the UI
    """

    def __init__(self):
        """Initialization of interface, adds all the relevant widgets."""
        super().__init__()

        # add central widget and vertical box
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        vbox = QtWidgets.QVBoxLayout(central_widget)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        graph_box = QtWidgets.QVBoxLayout()
        graph_label = QtWidgets.QLabel("Graph")
        self.graph = QtWidgets.QComboBox(self)
        self.graph.addItems(["UI-characteristic", "PR-characteristic"])
        #graph_box.addWidget(graph_label)
        graph_box.addWidget(self.graph)
        hbox.addLayout(graph_box)


        # add plot widget
        self.plot_widget = pg.PlotWidget()
        vbox.addWidget(self.plot_widget)

        # add horizontal box
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        # add start value box in hbox
        start_box = QtWidgets.QVBoxLayout()
        self.start_voltage = QtWidgets.QDoubleSpinBox()
        self.start_voltage.setValue(0)
        self.start_voltage.setRange(0, 3.3)
        self.start_voltage.setSingleStep(0.01)
        start_label = QtWidgets.QLabel("Start voltage")
        start_box.addWidget(start_label)
        start_box.addWidget(self.start_voltage)
        hbox.addLayout(start_box)

        # add stop value box in hbox
        stop_box = QtWidgets.QVBoxLayout()
        self.stop_voltage = QtWidgets.QDoubleSpinBox()
        self.stop_voltage.setValue(3.3)
        self.stop_voltage.setRange(0, 3.3)
        self.stop_voltage.setSingleStep(0.01)
        stop_label = QtWidgets.QLabel("Stop voltage")
        stop_box.addWidget(stop_label)
        stop_box.addWidget(self.stop_voltage)
        hbox.addLayout(stop_box)

        # add measuements box in hbox
        measurements_box = QtWidgets.QVBoxLayout()
        self.measurements = QtWidgets.QSpinBox()
        self.measurements.setValue(1)
        self.measurements.setRange(1, 20)
        measurements_label = QtWidgets.QLabel("Measurements")
        measurements_box.addWidget(measurements_label)
        measurements_box.addWidget(self.measurements)
        hbox.addLayout(measurements_box)

        # add port choice
        port_box = QtWidgets.QVBoxLayout()
        port_label = QtWidgets.QLabel("Device")
        self.port = QtWidgets.QComboBox(self)
        self.port.addItems(list_devices())
        port_box.addWidget(port_label)
        port_box.addWidget(self.port)
        hbox.addLayout(port_box)

        # add start and save button
        button_box = QtWidgets.QVBoxLayout()
        start_button = QtWidgets.QPushButton("Start")
        save_button = QtWidgets.QPushButton("Save")
        button_box.addWidget(start_button)
        button_box.addWidget(save_button)
        hbox.addLayout(button_box)

        # buttons to functions
        start_button.clicked.connect(self.run)
        save_button.clicked.connect(self.save_data)
        self.graph.currentIndexChanged.connect(self.change_plot)

        self.experiment = SolarExperiment()

        # Plot timer
        self.plot_timer = QtCore.QTimer()
        # Roep iedere 100 ms de plotfunctie aan
        if self.graph.currentIndex() == 0:
            self.plot_timer.timeout.connect(self.plot)
            self.plot_timer.start(100)
        else:
            self.plot_timer.timeout.connect(self.pr_plot)
            self.plot_timer.start(100)

        self.change_plot()

        # create menubar
        self._createActions()
        self._createMenubar()
        self._createStatusBar()

    @Slot()
    def change_plot(self):
        # Plot timer
        self.plot_timer = QtCore.QTimer()
        # Roep iedere 100 ms de plotfunctie aan
        if self.graph.currentIndex() == 0:
            self.plot_timer.timeout.connect(self.plot)
            self.plot_timer.start(100)
        else:
            self.plot_timer.timeout.connect(self.pr_plot)
            self.plot_timer.start(100)

    @Slot()
    def run(self):
        """Starts a scanning process with threading."""
        try:

            self.experiment.start_scan(
                self.port.currentText(),
                self.start_voltage.value(),
                self.stop_voltage.value(),
                self.measurements.value(),
            )
            self.statusbar.showMessage("Done", 3000)
        except Exception as e:
            print(e)
            error = QtWidgets.QMessageBox()
            error.setText("Error")
            error.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            error.exec()

    @Slot()
    def plot(self):
        """Plot the results"""
        self.plot_widget.clear()
        x = np.array(self.experiment.pv_voltages)
        y = np.array(self.experiment.currents)
        x_err = np.array(self.experiment.pv_voltages_err)
        y_err = np.array(self.experiment.currents_err)
        self.plot_widget.plot(x, y, symbol="o", symbolSize=5, pen=None)
        self.plot_widget.setLabel("left", "I (A)")
        self.plot_widget.setLabel("bottom", "U (V)")
        error_bars = pg.ErrorBarItem(x=x, y=y, width=2*x_err, height=2*y_err)
        self.plot_widget.addItem(error_bars)

    @Slot()
    def simple_plot(self):
        self.experiment = SolarExperiment()
        self.experiment.scan(
            self.port.currentText(),
            self.start_voltage.value(),
            self.stop_voltage.value(),
            self.measurements.value(),
        )
        self.plot_widget.clear()
        x = np.array(self.experiment.pv_voltages)
        y = np.array(self.experiment.currents)
        x_err = np.array(self.experiment.pv_voltages_err)
        y_err = np.array(self.experiment.currents_err)
        self.plot_widget.plot(x, y, symbol="o", symbolSize=5, pen=None)
        self.plot_widget.setLabel("left", "I (A)")
        self.plot_widget.setLabel("bottom", "U (V)")
        error_bars = pg.ErrorBarItem(x=x, y=y, width=x_err, height=y_err)
        self.plot_widget.addItem(error_bars)

    @Slot()
    def save_data(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(filter="CSV files (*.csv)")
        # Export to csv file
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ["Voltage (V)", "Current (A)", "Voltage error (V)", "Current error (A)"]
            )
            # remove error if only 1 measurement
            if self.measurements.value() == 1:
                for line in zip(self.experiment.pv_voltages, self.experiment.currents):
                    writer.writerow(list(line))
            else:
                for line in zip(
                    self.experiment.pv_voltages,
                    self.experiment.currents,
                    self.experiment.pv_voltages_err,
                    self.experiment.currents_err,
                ):
                    writer.writerow(list(line))

    @Slot()
    def power(self):
        self.statusbar.showMessage(f"Current max power: {self.experiment.p_max}")

    @Slot()
    def pr_plot(self):
        """Plot the results"""
        self.plot_widget.clear()
        x = np.array(self.experiment.fet_R)
        y = np.array(self.experiment.pv_powers)
        x_err = np.array(self.experiment.fet_R_err)
        y_err = np.array(self.experiment.pv_powers_err)
        self.plot_widget.plot(x, y, symbol="o", symbolSize=5, pen=None)
        self.plot_widget.setLabel("left", "P (W)")
        self.plot_widget.setLabel("bottom", "R (Ohm)")
        error_bars = pg.ErrorBarItem(x=x, y=y, width=2*x_err, height=2*y_err)
        self.plot_widget.addItem(error_bars)

    def _createActions(self):
        """Connect menubar to actions"""
        self.save_action = QAction("&Save", self)
        self.save_action.triggered.connect(self.save_data)
        self.exit_action = QAction("&Exit", self)
        self.exit_action.triggered.connect(self.close)

    def _createMenubar(self):
        """Create menubar"""
        menuBar = self.menuBar()
        fileMenu = QtWidgets.QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.save_action)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exit_action)

    def _createStatusBar(self):
        """Create statusbar"""
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Ready", 3000)


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
