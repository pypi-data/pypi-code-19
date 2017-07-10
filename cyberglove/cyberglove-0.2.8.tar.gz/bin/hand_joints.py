from mujoco_py import const, MjViewerBasic
from cyberglove.const import joint_names
import click
from mujoco_py import MjSim, load_model_from_path
import glfw
import numpy as np


class HandViewer(MjViewerBasic):
    def __init__(self, sim):
        super().__init__(sim)
        self.move_camera(const.MOUSE_ZOOM, 0, -0.1)
        self.move_camera(const.MOUSE_ROTATE_V, -0.2, 0.0)
        self.move_camera(const.MOUSE_ROTATE_H, 0.0, -0.1)
        self.joint_idx = 0

    def _create_full_overlay(self):
        self.add_overlay(const.GRID_TOPRIGHT, "Current joint", joint_names[self.joint_idx])
        self.add_overlay(const.GRID_TOPRIGHT, "Move [n]ext joint", "")
        self.add_overlay(const.GRID_TOPRIGHT, "Move [p]revious joint", "")

    def key_callback(self, window, key, scancode, action, mods):
        super().key_callback(window, key, scancode, action, mods)
        # Trigger on keyup only:
        if action != glfw.RELEASE:
            return
        if key == glfw.KEY_N:
            self.joint_idx = (self.joint_idx + 1) % len(joint_names)
        if key == glfw.KEY_P:
            self.joint_idx = (self.joint_idx - 1) % len(joint_names)

    def render(self):
        self._overlay.clear()
        self._create_full_overlay()
        super().render()

    def run(self):
        state = self.sim.get_state()
        while True:
            self.sim.set_state(state)
            name = joint_names[self.joint_idx]
            qpos_idx = self.sim.model.get_joint_qpos_addr(name)
            jnt_range = self.sim.model.jnt_range[self.sim.model.joint_name2id(name)]
            self.sim.data.qpos[qpos_idx] = np.random.uniform(jnt_range[0], jnt_range[1])
            self.sim.forward()
            self.render()

@click.command()
@click.argument('hand_xml_path')
def main(hand_xml_path):
    try:
        sim = MjSim(load_model_from_path(hand_xml_path))
    except Exception as e:
        raise Exception('Falied to load model, make sure STL files are in cache', e)
    viewer = HandViewer(sim)
    viewer.run()

if __name__ == '__main__':
    main()