#! coding:utf-8
"""
commands.py

"""
from __future__ import absolute_import

import os
import sys
import time
import argparse
from pathlib import Path
from . import globalvars as g
from .configs import Station
from .trainer import Trainer
from .manager import BackGroundProcess, Manager


def init():
    """
    :usage:
        $ ats-init

    No argment
    """
    cur_dir = Path(os.getcwd())

    # Create Directories
    cur_dir.joinpath(g.DatasetDir).mkdir(exist_ok=True)
    cur_dir.joinpath(g.ModelsDir).mkdir(exist_ok=True)
    cur_dir.joinpath(g.SettingsDir).mkdir(exist_ok=True)
    cur_dir.joinpath(g.ResultsDir).mkdir(exist_ok=True)

    # Copy Stationfile
    Station.copy_default_file(
        to_path=cur_dir.joinpath(g.Stationfile).as_posix())


def makeDataset():
    """
    No argment
    """
    # CompleteDataset = Dataset.create(param)
    # asser CompleteDataset.success == True
    cur_dir = Path(os.getcwd())
    Stationfile = cur_dir.joinpath(g.Stationfile)
    config = Station(Stationfile.as_posix())


def run():
    """
    --model, -m, model_001.py
    --setting, -s, 001.conf
    --test, -t, test model
    """

    cur_dir = Path(os.getcwd())

    print("OpenATS : ats-run ...")

    # Argument Parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', '-m', default=None)
    parser.add_argument('--setting', '-s', default=None)
    parser.add_argument('--test', '-t', default=False, action='store_true')

    if sys.argv[0] == 'python -m unittest':
        parsed_args = parser.parse_args([])
        parsed_args.test = True
    else:
        parsed_args = parser.parse_args()

    # argument setup
    model_name = Path(parsed_args.model).stem
    setting_name = Path(parsed_args.setting).stem
    istest = parsed_args.test

    print("model : ", model_name)
    print("setting : ", setting_name)
    print("test mode : ", istest, type(istest))

    # create trainer
    trainer = Trainer(cur_dir, model_name, setting_name, isTest=istest)

    # run trainer
    trainer.run()

    pass


def runAll():
    """
    No argment
    """
    print("OpenATS : ats-runAll ...")

    # ==========================================
    # Argument Parsing
    # ==========================================
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', '-t', default=False, action='store_true')

    if sys.argv[0] == 'python -m unittest':
        parsed_args = parser.parse_args([])
        parsed_args.test = True
    else:
        parsed_args = parser.parse_args()

    print("test mode : ", parsed_args.test, type(parsed_args.test))


    # ==========================================
    # Current Dir 
    # ==========================================
    cur_dir = Path(os.getcwd())

    # ==========================================

    backgraoud_proc = BackGroundProcess()
    # ==========================================
    manager = Manager(
        project_rootdir=cur_dir.as_posix(),
        models_dirname=g.ModelsDir, 
        params_dirname=g.SettingsDir, 
        results_dirname=g.ResultsDir)

    # ==========================================

    while(True):
        time.sleep(5)

        # if isrunning
        if backgraoud_proc.isRunning():
            print(".")
        else:

            n = manager.next()

            if(n == False):
                print("Task is Nothing.. ")
                continue

            print(" ---- Proc is Start --- ")

            param_name = Path(manager.get_primary_param()).stem
            model_name = Path(manager.get_primary_model()).stem

            working_dir_path = manager.get_workspace_path(model_name, param_name)
            # runner_filepath = os.path.join(ROOT_DIR, "runner.py")
            if parsed_args.test:
                args = ["ats-run",
                        "-m", model_name,
                        "-s", param_name,
                        '-t'
                        ]
            else:
                args = ["ats-run",
                        "-m", model_name,
                        "-s", param_name,
                        ]
            # Proccess Run
            backgraoud_proc.popen(args, cws=cur_dir.as_posix())

            # SUCCESS
            if backgraoud_proc.proc.stdout != None:
                for line in backgraoud_proc.proc.stdout:
                    print(line.decode("utf-8"))

            # ERROR
            if backgraoud_proc.proc.stderr != None:
                with open(os.path.join(working_dir_path, "error.txt"), "w") as fp:
                    for line in backgraoud_proc.proc.stderr:
                        fp.write(line.decode("utf-8") + "\n")
