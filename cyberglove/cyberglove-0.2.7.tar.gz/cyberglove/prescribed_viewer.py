import numpy as np
from mujoco_py import const, MjViewerBasic
import glfw
from cyberglove import CyberGlove
import time
import copy
from cyberglove.const import joint_names, data_dir
import os
import pickle

prescribed_poses = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0.5, 0, 0, 0, -0.5, 0, 0, 0, 0, -1, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0.3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, -1, 0, 0, 0, 0],
    [1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, -1, 0, 0, 0, 0],
    [-1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, -1, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, -1, 0, 0, 0, 0],
    [0, -1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, -1, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, -1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, -1, -1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -0.5, 0, 0, -1, -1],
    [0, 0, 0, 0, 0, 0, 0, 0.33, 0, 0, 0, 0.66, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0.66, 0, 0, 0, 0.33, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 0, 0.35, 0.7, 0.33, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.31, 0.61, 1, -1, -0.1],
    [0, 0, 0, 0, 0, 0, 0, 0.45, 0.7, 0.33, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.42, 0.72, 0.8, -0.76, -0.08],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.63, 0.48, 0.4, 0, 0, 0, 0, 0, 0.47, 1, 0.95, -0.8, -0.08],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.85, -0.25, 0.63, 0.4, 0.16, 0, 1, 1, -0.87, -0.22],
    [0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0.1, 0.7, 1, -1, -0.5],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1, 1, -1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, -1, 0],
    [1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0.1, 0.7, 1, -1, -0.5],
    [-1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0.1, 0.7, 1, -1, -0.5],
    [0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0.1, 0.7, 1, -1, -0.5],
    [0, -1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0.1, 0.7, 1, -1, -0.5]])


class PrescribedViewer(MjViewerBasic):
    ''' Gather data by imitating prescribed poses '''
    def __init__(self, sim):
        super().__init__(sim)
        self.mjb = self.sim.model.get_mjb()
        self.phases = [(self.key_callback_instructions, self._overlay_instructions),
                       (self.key_callback_gathering_poses, self._overlay_poses)]
        self.phase_idx = 0

        self.pose_idx = 0
        self.glove = CyberGlove()
        self.start_random = False
        self.move_camera(const.MOUSE_ZOOM, 0, -0.1)
        self.move_camera(const.MOUSE_ROTATE_V, -0.2, 0.0)
        self.move_camera(const.MOUSE_ROTATE_H, 0.0, -0.1)
        self.glove_recordings = []
        self.glove_recording = []
        self.poses = [None for _ in range(len(prescribed_poses))]

        self.wait_time = 4
        self.recording_time = 3

    # ########## Info about instructions.

    def key_callback_instructions(self, window, key, scancode, action, mods):
        if key == glfw.KEY_A:
            self.phase_idx += 1
            self.start_time = time.time()

    def _overlay_instructions(self):
        self.add_overlay(const.GRID_TOPRIGHT,
                         "Put glove on your hand.\n"
                         "You will have %ds to read instructions\n"
                         "and %d sec. to do what you are asked for.\n"
                         "Press [a] to start.\n" % (self.wait_time, self.recording_time), "")

    # ########## Info about gathering positions.

    def key_callback_gathering_poses(self, window, key, scancode, action, mods):
        if action != glfw.RELEASE:
            return
        if key == glfw.KEY_A and self.remaining < -self.recording_time and self.weird_std():
            self.glove_recordings.append(copy.deepcopy(self.glove_recording))
            self.pose_idx += 1
            self.start_time = time.time()
            self.glove_recording = []
            if self.pose_idx >= len(prescribed_poses):
                self.phase_idx += 1
        if key == glfw.KEY_R:
            self.start_time = time.time()
            self.glove_recording = []

    def _overlay_poses(self):
        self.sim.set_state(self.state)
        pose = copy.deepcopy(prescribed_poses[self.pose_idx])
        for idx, name in enumerate(joint_names):
            jnt_range = self.sim.model.jnt_range[self.sim.model.joint_name2id(name)]
            qpos_idx = self.sim.model.get_joint_qpos_addr(name)
            if pose[idx] > 1e-4:
                pose[idx] = pose[idx] * jnt_range[1]
            else:
                pose[idx] = pose[idx] * np.abs(jnt_range[0])
            self.sim.data.qpos[qpos_idx] = pose[idx]
        self.poses[self.pose_idx] = (pose)
        self.sim.forward()

        self.add_overlay(const.GRID_TOPRIGHT, "", "")

        self.add_overlay(const.GRID_TOPRIGHT,
                         "Currently gathered %d / %d samples." % (self.pose_idx, len(prescribed_poses)), "")

        self.add_overlay(const.GRID_TOPRIGHT, "", "")
        self.remaining = (self.wait_time - (time.time() - self.start_time))
        if self.remaining > 0:
            self.add_overlay(const.GRID_TOPRIGHT, "Starting in %.1f sec." % self.remaining, "")
        elif self.remaining > -self.recording_time:
            self.add_overlay(const.GRID_TOPRIGHT, "Recording %s" % ("." * (int(time.time() * 5) % 7)), "")
            self.glove_recording.append(np.array(copy.deepcopy(self.glove.read())))
        if self.remaining < -self.recording_time:
            if self.weird_std():
                self.add_overlay(const.GRID_TOPRIGHT, "[a]ccept the recording", "")
            else:
                self.add_overlay(const.GRID_TOPRIGHT, "Cannot accept this recording.\nToo high std or glove is not on your hand.", "")
        self.add_overlay(const.GRID_TOPRIGHT, "[r]eject and repeat this recording", "")

    def weird_std(self):
        std = np.max(np.std(np.stack(self.glove_recording), axis=0))
        return std < 80 and std > 0

    ####################################

    def save_results(self):
        data = {"glove_recordings": self.glove_recordings,
                "poses": self.poses,
                "mjb": self.mjb}
        user = os.getenv('OPENAI_USER', 'OPENAI_USER')
        fname = os.path.join(data_dir, "recordings_%s.pkl" % user)
        print("Saving recordings as: %s" % fname)
        os.makedirs(data_dir, exist_ok=True)  # Make data directory if not present
        with open(fname, "wb") as f:
            pickle.dump(data, f)
        print("Saved")

    def key_callback(self, window, key, scancode, action, mods):
        super().key_callback(window, key, scancode, action, mods)
        self.phases[self.phase_idx][0](window, key, scancode, action, mods)

    def render(self):
        self._overlay.clear()
        self.phases[self.phase_idx][1]()
        super().render()

    def run(self):
        self.state = self.sim.get_state()
        while self.phase_idx <= len(self.phases) - 1:
            self.render()
        self.save_results()
