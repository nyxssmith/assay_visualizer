from django.db import models
import mysql.connector
import os
import json
import csv
import copy
import uuid


# Create your models here.

class db_connection(models.Model):

    def get_all_smiles(self):

        sql_cmd = "select smiles from assays;"
        result = self.run_sql(sql_cmd)
        smiles = []
        for tup in result:
            smiles.append(tup[0][:-6])

        return smiles

    def get_all_dates(self):

        sql_cmd = "select date from assays;"
        result = self.run_sql(sql_cmd)
        result.sort()

        return result

    def get_measured_vs_predicted_lists_for_assay(self, assay_int):
        sql_cmd = "select assay_{} from assays;".format(assay_int)

        measured_list = self.run_sql(sql_cmd)

        sql_cmd = "select model_for_assay_{} from assays;".format(assay_int)

        predicted_list = self.run_sql(sql_cmd)

        return measured_list, predicted_list

    def get_measured_vs_date_lists_for_assay(self, assay_int):
        sql_cmd = "select assay_{} from assays;".format(assay_int)

        measured_list = self.run_sql(sql_cmd)

        date_list = self.get_all_dates()
        return measured_list, date_list

    def make_x_and_y_axis_for_chart(self, measured_list, predicted_list):

        x_axis = []
        for result in measured_list:
            if result[0]:
                x_axis.append(float(result[0]))
            else:
                x_axis.append("AssayNotRan")

        y_axis = []
        for result in predicted_list:
            if result[0]:
                y_axis.append(result[0])
            else:
                y_axis.append('null_ph')

        return x_axis, y_axis

    def get_chart_data_measured_vs_predicted(self, assay_int):
        measured_list, predicted_list = self.get_measured_vs_predicted_lists_for_assay(assay_int=assay_int)
        x_axis, y_axis = self.make_x_and_y_axis_for_chart(measured_list, predicted_list)

        return x_axis, y_axis

    def format_datelist_for_chart(self, datelist):
        x_axis = []
        for date in datelist:
            x_axis.append(str(date[0]))
        return x_axis

    def get_chart_data_measured_vs_time(self, assay_int):
        measured_list, date_list = self.get_measured_vs_date_lists_for_assay(assay_int=assay_int)

        y_axis, not_used = self.make_x_and_y_axis_for_chart(measured_list, measured_list)
        x_axis = self.format_datelist_for_chart(date_list)

        return x_axis, y_axis

    def generate_insert_sql_cmd(self, csv_row):
        """

        :param csv_row: given row of csv file
        :return: a mysql command to add that row to the assays table
        """
        all_cols = ["smiles", "identifier", "date", "assay_0", " assay_1", " assay_2", " assay_3", " assay_4",
                    " assay_5", " assay_6", " assay_7", " assay_8", " assay_9", " model_for_assay_0",
                    " model_for_assay_1", " model_for_assay_2", "model_for_assay_3", "model_for_assay_4",
                    "model_for_assay_5", "model_for_assay_6", "model_for_assay_7", "model_for_assay_8",
                    "model_for_assay_9"]
        cols_to_use = copy.copy(all_cols)
        i = 0
        values = []
        for col in csv_row:
            if i > 2:
                try:
                    float(csv_row[i])
                    values.append(csv_row[i].replace(' ', ''))
                except:
                    cols_to_use.pop(i)
            elif i == 2:
                # convert date to mysql friendly format
                date_list = csv_row[i].split('/')  # m d y
                date_list.insert(0, date_list[2])
                date_list.pop()  # y m d
                values.append('"' + '-'.join(date_list) + '"')
            elif i == 0:
                smiles_uuid = str(uuid.uuid4())[:6]
                values.append('"' + csv_row[i].replace(' ', '') + smiles_uuid + '"')
            else:
                values.append('"' + csv_row[i].replace(' ', '') + '"')

            i += 1
        cmd = "INSERT INTO assays(" + ",".join(cols_to_use) + ") VALUES(" + ",".join(values) + ");"
        return cmd

    def import_csv(self):
        print("importing all csv files to db")
        files = os.listdir(os.getcwd())
        for file in files:
            if ".csv" in file:
                with open(file, mode='r') as infile:
                    reader = csv.reader(infile)
                    row_num = 0
                    for row in reader:
                        if row_num > 2:
                            print("new row")
                            cmd = self.generate_insert_sql_cmd(row)
                            print(cmd)
                            try:
                                result = self.run_sql(cmd)
                            except:
                                print("sql fialed")
                            print(result)
                        row_num += 1
        return

    def run_sql(self, sql_cmd):
        """

        :param sql_cmd: takes a mysql command as a string
        :return: list of tuples where each tuple corresponds to a returned row of the command
        """

        cursor = self.connection.cursor()
        cursor.execute(sql_cmd)
        self.connection.commit()
        list_of_rows_returned = []
        for (sql_cmd) in cursor:
            list_of_rows_returned.append(sql_cmd)
        return list_of_rows_returned

    # TODO make better
    def create_table_if_not_exists(self):
        cursor = self.connection.cursor()
        sql_cmd = """CREATE TABLE assays (
              smiles VARCHAR(255) NOT NULL,
              identifier VARCHAR(255) NOT NULL,
              date DATE NOT NULL,
              assay_0 FLOAT(18,15),
              assay_1 FLOAT(18,15),
              assay_2 FLOAT(18,15),
              assay_3 FLOAT(18,15),
              assay_4 FLOAT(18,15),
              assay_5 FLOAT(18,15),
              assay_6 FLOAT(18,15),
              assay_7 FLOAT(18,15),
              assay_8 FLOAT(18,15),
              assay_9 FLOAT(18,15),
              model_for_assay_0 FLOAT(18,15),
              model_for_assay_1 FLOAT(18,15),
              model_for_assay_2 FLOAT(18,15),
              model_for_assay_3 FLOAT(18,15),
              model_for_assay_4 FLOAT(18,15),
              model_for_assay_5 FLOAT(18,15),
              model_for_assay_6 FLOAT(18,15),
              model_for_assay_7 FLOAT(18,15),
              model_for_assay_8 FLOAT(18,15),
              model_for_assay_9 FLOAT(18,15),
              PRIMARY KEY (smiles)
            );"""
        result = cursor.execute(sql_cmd)

    def get_db(self):
        with open('config.json') as json_file:
            config = json.load(json_file)
            return config["db"]

    def get_db_addr(self):
        with open('config.json') as json_file:
            config = json.load(json_file)
            return config["db_addr"]

    def get_db_user(self):
        with open('config.json') as json_file:
            config = json.load(json_file)
            return config["db_user"]

    def get_db_password(self):
        with open('config.json') as json_file:
            config = json.load(json_file)
            return config["db_password"]

    def get_db_root_user(self):
        with open('config.json') as json_file:
            config = json.load(json_file)
            return config["db_root_user"]

    def get_db_root_password(self):
        with open('config.json') as json_file:
            config = json.load(json_file)
            return config["db_root_password"]

    def get_connection(self):
        conn = mysql.connector.connect(user=self.db_user, password=self.db_password,
                                       host=self.db_addr, buffered=True, database=self.db)
        return conn

    def __init__(self):
        self.db = self.get_db()
        self.db_addr = self.get_db_addr()
        self.db_user = self.get_db_user()
        self.db_password = self.get_db_password()
        self.db_root_user = self.get_db_root_user()
        self.db_root_password = self.get_db_root_password()
        self.connection = self.get_connection()
        # TODO make actually check and not just try/fail
        try:
            self.create_table_if_not_exists()
            print("table didnt exist, creating it")
        except:
            pass
