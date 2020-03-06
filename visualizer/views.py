from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from visualizer.models import db_connection

import json
import copy
from random import randrange

global y_over_time, mode_button_text
y_over_time = False
mode_button_text = "Display measured/time"


def line(request):
    """
    Main page
    :param request:
    :return:
    """
    global y_over_time, mode_button_text

    connection = db_connection()

    smiles_list = connection.get_all_smiles()
    dates_list = connection.format_datelist_for_chart(connection.get_all_dates())

    assay_ints = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    all_datasets = ""
    for assay in assay_ints:

        if y_over_time:
            x_axis, y_axis = connection.get_chart_data_measured_vs_time(assay_int=assay)
        else:
            x_axis, y_axis = connection.get_chart_data_measured_vs_predicted(assay_int=assay)

        with open('config.json') as json_file:
            config = json.load(json_file)
            x_axis_limit = config["x_axis_limit"]

        if x_axis_limit > 0:
            x_axis = x_axis[:50]

        dataset_template = "{label:`assay_int`,fill:false,borderColor:`rgb(RR,GG,BB)`,data:Y_AXIS_LIST}"
        datasets = copy.copy(dataset_template)
        datasets = datasets.replace("RR", str(randrange(50, 255)))
        datasets = datasets.replace("GG", str(randrange(50, 255)))
        datasets = datasets.replace("BB", str(randrange(50, 255)))

        datasets = datasets.replace("Y_AXIS_LIST", str(y_axis))
        datasets = datasets.replace("'null_ph'", 'null')
        datasets = datasets.replace("'AssayNotRan'", 'null')
        datasets = datasets.replace("assay_int", "assay_{}".format(assay))

        print(datasets)
        all_datasets += datasets + ","

    all_datasets = all_datasets[:-1]

    return render(request, 'line.html', {"smiles_list": smiles_list, "dates_list": dates_list, "x_axis": x_axis,
                                         "datasets": all_datasets, "mode_button_text": mode_button_text})


def import_button_click(request):
    connection = db_connection()
    connection.import_csv()
    return line(request)


def mode_button_click(request):
    global y_over_time, mode_button_text
    if y_over_time:
        y_over_time = False
        mode_button_text = "Display measured/time"

    else:
        y_over_time = True
        mode_button_text = "Display measured/predicted"

    return line(request)
