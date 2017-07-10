#!/usr/bin/env python
import os
from cyberglove.mapped_viewer import MappedViewer
from cyberglove.const import data_dir
import cloudpickle as pickle
from mujoco_py import MjSim, load_model_from_mjb


def main():
    OPENAI_USER = os.getenv('OPENAI_USER', 'OPENAI_USER')

    mapping_file = os.path.join(data_dir, "mapping_%s.pkl" % OPENAI_USER)
    try:
        with open(mapping_file, "rb") as f:
            mapping = pickle.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("Missing calibration file, run calibrate_cyberglove.py")
    model = load_model_from_mjb(mapping.mjb)
    sim = MjSim(model)
    viewer = MappedViewer(sim, mapping.map)
    while True:
        sim.step()
        viewer.render()


if __name__ == '__main__':
    main()
