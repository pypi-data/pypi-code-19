#!/usr/bin/env python
import os
import click
from cyberglove.prescribed_viewer import PrescribedViewer
from mujoco_py import MjSim, load_model_from_path


@click.command()
@click.option('--hand-xml-path', default=None, help='path to XML hand model')
def main(hand_xml_path):
    if hand_xml_path is None:
        hand_xml_path = 'xmls/robot/dactyl/hand.xml'
    if not os.path.exists(hand_xml_path):
        raise ValueError('Failed to find hand XML.  Tried {}'.format(hand_xml_path))
    try:
        print('Loading hand xml file', hand_xml_path)
        sim = MjSim(load_model_from_path(hand_xml_path))
    except Exception as e:
        raise Exception('Failed to load model, make sure STL files are in cache', e)
    viewer = PrescribedViewer(sim)
    viewer.run()
    print('Gathered recordings, fitting calibration right away')
    print('To re-fit gathered recording, run fit_cyberglove_mapping.py')
    dirname = os.path.dirname(os.path.abspath(__file__))
    fname = os.path.join(dirname, "fit_cyberglove_mapping.py")
    os.system('python ' + fname)
    print("Finished fitting model.")

if __name__ == '__main__':
    main()

