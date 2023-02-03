import csv
from os import path
import datetime
import logging

class CsvWriter():
    def __init__(self):
        """Init CSVWriter class"""
        self.filename_usb = ""
        self.filename_local = ""

    def set_filename_local(self, filename):
        self.filename_local = filename

    def set_filename_usb(self, filename):
        self.filename_usb = filename

    def write_header(self):
        """
        Creates new .csv file with given header values 'Timestamp,*args'
        
        where *args is a list of strings - data columns to append.
        """
        try:
            if not path.isfile(self.filename_usb):
                with open(self.filename_usb, "w", newline="") as file:
                    print(file)
                    print("Writing header")
                    writer = csv.writer(file)
                    writer.writerow(["Timestamp", "Flow", "Rpm", "Temperature"])
        except Exception as e:
            logging.error("An exception occured when trying to write header to csv file")

        try:
            if not path.isfile(self.filename_local):
                with open(self.filename_local, "w", newline="") as file:
                    print(file)
                    print("Writing header")
                    writer = csv.writer(file)
                    writer.writerow(["Timestamp", "Flow", "Rpm", "Temperature"])
        except Exception as e:
            logging.error("An exception occured when trying to write header to csv file")

    def append_row(self, args):
        """
        Append a row of data to an existing .csv file.
        args = Timestamp, int(frequency), int(duty_cycle), bool(pump_on)
        """
        try:
            with open(self.filename_usb, 'a+', newline='') as file:
                writer = csv.writer(file)
                datenow = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')
                writer.writerow([datenow, *args])
        except Exception as e:
            logging.error("An exception occured when trying to append row to csv file")
        try:
            with open(self.filename_local, 'a+', newline='') as file:
                writer = csv.writer(file)
                datenow = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')
                writer.writerow([datenow, *args])
        except Exception as e:
            logging.error("An exception occured when trying to append row to csv file")

    def start_new_log(self, type):
        time_now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        self.set_filename_usb(f"/mnt/storage/measurements/{time_now}_{type}.csv")
        self.set_filename_local(f"/home/pi/new-harvest-storage/measurements/{time_now}_{type}.csv")
        self.write_header()