from pyconrad import *

jvm = PyConrad()
jvm.setup()

jvm.add_import('edu.stanford.rsl.conrad.data.numeric')
jvm.add_import('edu.stanford.rsl.tutorial.phantoms')
jvm.add_import('edu.stanford.rsl.conrad.phantom')
jvm.add_import('edu.stanford.rsl.conrad.utils')
jvm.add_import('edu.stanford.rsl.tutorial.iterative')
jvm.add_import('edu.stanford.rsl.conrad.geometry.shapes.simple')
jvm.add_import('edu.stanford.rsl.conrad.geometry.trajectories')
jvm.add_import('edu.stanford.rsl.conrad.numerics')
jvm.add_import('edu.stanford.rsl.conrad.geometry')
jvm.add_import('edu.stanford.rsl.tutorial.cone')
jvm.add_import('edu.stanford.rsl.conrad.data.numeric.opencl')


# Common error: "no matching overload"
# There is no method overloading in python!
# Use JPype boxed types: http://jpype.readthedocs.io/en/latest/userguide.html#boxed-types

# Creating a PointND
jvm['PointND'](3,3)  # does not work
jvm['PointND']([3,3])  # neither does this
jvm['PointND'](JArray(JDouble)([3,2]))  # works
makePointND([3, 3])  # works

# the same applies for SimpleVector
jvm['SimpleVector'](JArray(JDouble)([3,2]))  # works
makeSimpleVector([3, 3])  # works

# Grid.setOrigin(...), setSpacing
jvm['Grid2D'](3,2).setOrigin(JArray(JDouble)([2,3]))
PyGrid.from_grid(jvm['Grid2D'](3,2)).set_origin([2,3])
PyGrid.from_grid(jvm['Grid2D'](3,2)).set_spacing([2,3])

# Creating nested enums
traj = jvm['HelicalTrajectory']()
print(traj.getDetectorOffsetU())  # returns a float
enumval = jvm['Projection$CameraAxisDirection'].values()[int(traj.getDetectorOffsetU())] # Convert back to enum
enumval =jvm.enumval_from_int('Projection$CameraAxisDirection', traj.getDetectorOffsetU())  # or like that
