#!/usr/bin/env python
import os
import click
from cyberglove.prescribed_viewer import PrescribedViewer
from mujoco_py import MjSim, load_model_from_path


@click.command()
@click.argument('hand_xml_path')
def main(hand_xml_path):
    try:
        sim = MjSim(load_model_from_path(hand_xml_path))
    except Exception as e:
        raise Exception('Falied to load model, make sure STL files are in cache', e)
    viewer = PrescribedViewer(sim)
    viewer.run()


if __name__ == '__main__':
    main()
    print('Gathered recordings, fitting calibration right away')
    print('To re-fit gathered recording, run fit_mapping.py')
    os.system('fit_mapping.py')
