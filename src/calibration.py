import json

class Calibration():
    def __init__(self):
        """Initialize calibration from filename, filename required"""
        self.filename = None
        self.calib = None
        self.slope = 1.0
        
        print(f"Calculated slope: {self.slope}")

    def get_filename(self):
        """Return filename"""
        return self.filename

    def set_calibration(self, json_obj, filename):
        """Set calibration with filename"""
        if json_obj.get("low_rpm", None) is None:
            self.filename = "Wrong File Format"
            return

        print(f"Setting calibration with {json_obj} with filename {filename}")
        self.filename = filename
        self.calib = json_obj
        self.calc_slope()

    def load_calibration(self, filename):
        calib = {}
        with open(filename, "r") as calib:
            calib = json.load(calib)
        self.calib = calib
        self.calc_slope()

    def calc_slope(self):
        """Get function that describes relation between rpm and flow"""
        # equation in form of y = ax + b, b is 0 as there is no flow at 0 rpm
        duration_m = self.calib.get("duration", 1) / 60.0
        self.slope = (self.calib.get("high_rpm_vol", 1) / duration_m - self.calib.get("low_rpm_vol", 1) / duration_m) / (self.calib.get("high_rpm", 1) - self.calib.get("low_rpm", 1))   # slope in mL/s/rpm
        print(f"Calculated slope: {self.slope}")

    def get_slope(self):
        """Return calculated slope"""
        return self.slope

    def get_rpm(self, flow):
        """Return required rpm to get desired flow"""
        print(f"Calculating rpm from selected flow: {flow} and slope: {self.slope}")
        return flow / self.slope