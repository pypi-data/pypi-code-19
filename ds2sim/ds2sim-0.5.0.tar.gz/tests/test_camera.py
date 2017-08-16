import ds2sim.camera
import numpy as np


class TestUtilityFunctions:
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def test_compileCameraMatrix_valid(self):
        """Serialise a test matrix."""
        # Create random position.
        pos = np.random.normal(0, 1, 3)

        # Create a random orthonormal matrix.
        R = np.linalg.svd(np.random.normal(size=(3, 3)))[0]
        assert np.allclose(np.eye(3), R @ R.T)

        # The rotation matrix must span a right handed coordinate system.
        right, up = R[0, :], R[1, :]
        forward = np.cross(right, up)
        R[2, :] = forward
        assert np.allclose(np.eye(3), R @ R.T)

        # Compile the camera matrix with the position in the last _row_.
        # This is also how compileCameraMatrix must construct and serialise
        # it internally.
        ref_cmat = np.eye(4)
        ref_cmat[:3, :3] = R
        ref_cmat[3, :3] = pos
        ref_cmat = ref_cmat.astype(np.float64)
        ref_cmat = ref_cmat.flatten('C')

        # Camera vectors must be serialised into 4x4 float32 matrix.
        fun = ds2sim.camera.compileCameraMatrix
        ret_cmat = fun(right, up, pos)
        assert isinstance(ret_cmat, bytes)
        assert len(ret_cmat) == 16 * 4

        # The serialisation must have added the missing forward vector
        # and stored the matrix in column major format. Construct this
        # transformation here as well, then compare the arrays.
        assert np.allclose(np.fromstring(ret_cmat, np.float32), ref_cmat)

    def test_compileCameraMatrix_invalid(self):
        """Must return None if the matrix is invalid."""
        fun = ds2sim.camera.compileCameraMatrix

        # Wrong data types.
        assert fun(None, None, [1, 2, 3]) is None

        # Wrong dimensions: must be 3 vectors with 3 elements.
        assert fun([1, 2, 3, 4], [5, 6, 7], [8, 9]) is None

        # Right and Up are not orthogonal
        right, pos = [1, 0, 0], [0, 0, 0]
        assert fun(right, right, pos) is None

        # Rotation matrix is not orthonormal.
        assert fun(right, [0, 2, 0], pos) is None
