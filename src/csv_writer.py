import csv
from os import path
import datetime
import logging

class CsvWriter():
    def __init__(self):
        """Init CSVWriter class"""
        self.filename = ""

    def set_filename(self, filename):
        self.filename = filename

    def write_header(self):
        """
        Creates new .csv file with given header values 'Timestamp,*args'
        
        where *args is a list of strings - data columns to append.
        """
        try:
            if not path.isfile(self.filename):
                with open(self.filename, "w", newline="") as file:
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
            with open(self.filename, 'a+', newline='') as file:
                writer = csv.writer(file)
                datenow = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')
                writer.writerow([datenow, *args])
        except Exception as e:
            logging.error("An exception occured when trying to append row to csv file")

    def start_new_log(self, type):
        self.set_filename(f"/mnt/storage/measurements/measure_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}_{type}.csv")
        self.write_header()