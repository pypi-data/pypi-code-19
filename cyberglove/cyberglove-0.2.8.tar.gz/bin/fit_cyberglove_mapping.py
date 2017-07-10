#!/usr/bin/env python
import os
import click
import cloudpickle as pickle
from mujoco_py import MjSim, load_model_from_mjb
from cyberglove import Mapping
from cyberglove.const import data_dir


@click.command()
@click.option('--user', default=None, help='Username')
def main(user):
    if user is None:
        user = os.getenv('OPENAI_USER', 'OPENAI_USER')
    recordings_file = os.path.join(data_dir, "recordings_%s.pkl" % user)
    with open(recordings_file, "rb") as f:
        data = pickle.load(f)
    model = load_model_from_mjb(data["mjb"])
    sim = MjSim(model)
    mapping = Mapping()
    mapping.train(sim,
                  data["glove_recordings"],
                  data["poses"])

    fname = os.path.join(data_dir, "mapping_%s.pkl" % user)
    print("Saving mapping as: %s" % fname)
    with open(fname, "wb") as f:
        pickle.dump(mapping, f)


if __name__ == '__main__':
    main()
    print('Run show_calibrated.py to test the glove calibration mapping.')
