from mujoco_py import const, MjViewer
from cyberglove import CyberGlove
from cyberglove import const as cyberglove_const


class MappedViewer(MjViewer):
    def __init__(self, sim, mapping):
        super().__init__(sim)
        self.mapping = mapping
        self.glove = CyberGlove()

    def render(self):
        glove_recording = self.glove.read()
        vals = self.mapping(glove_recording)
        for idx, name in enumerate(cyberglove_const.joint_names):
            self.sim.data.qpos[self.sim.model.get_joint_qpos_addr(name)] = vals[idx]
        super().render()

    def _create_full_overlay(self):
        super()._create_full_overlay()
        self.add_overlay(const.GRID_TOPRIGHT, "Mimic the pose and press the Enter Key", "")
