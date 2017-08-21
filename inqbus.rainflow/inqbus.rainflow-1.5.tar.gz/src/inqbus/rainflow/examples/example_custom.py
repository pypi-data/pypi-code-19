import numpy as np
import inqbus.rainflow as rfc

data = np.array([2,3,5,6,1,2,3,5,6,5,7,6,4,2,5,3,8,1,2,5,6,-2,-4,-3,-5,-2])
print(data)

# main algorithm
res, res_counted = rfc.Rainflow.on_numpy_array(data)
print(res, res_counted)

# add some classifications afterwards
res_32, res_counted_32 = rfc.Binning.as_table_on_numpy_array(
    res, bin_count=4, minimum=2)
print(res_32, res_counted_32)

matrix_32 = rfc.Binning.as_matrix_on_numpy_array(
    res, bin_count=32, axis=['top', 'left', 'bottom', 'right'])
print(matrix_32)