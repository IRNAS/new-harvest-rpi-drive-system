import json

class Calibration():
    def __init__(self, filename):
        """Initialize calibration from filename, filename required"""
        self.calib = self.load_calibration(filename)

        self.calc_slope()
        print(f"Calculated slope: {self.slope}")

    def load_calibration(self, filename):
        calib = {}
        with open(filename, "r") as calib:
            calib = json.load(calib)
        return calib

    def calc_slope(self):
        """Get function that describes relation between rpm and flow"""
        # equation in form of y = ax + b, b is 0 as there is no flow at 0 rpm
        duration_m = self.calib.get("duration", 1) / 60.0
        self.slope = (self.calib.get("high_rpm_vol", 1) / duration_m - self.calib.get("low_rpm_vol", 1) / duration_m) / (self.calib.get("high_rpm", 1) - self.calib.get("low_rpm", 1))   # slope in mL/s/rpm

    def get_slope(self):
        """Return calculated slope"""
        return self.slope

    def get_rpm(self, flow):
        """Return required rpm to get desired flow"""
        return flow / self.slope