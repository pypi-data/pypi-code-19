"""Parse xarray datasets and add additional metadata attributes needed by
xgcm."""

def parse_dataset(ds,
                  x_grid_index=None,
                  x_grid_index_at_u_location=None,
                  y_grid_index=None,
                  y_grid_index_at_v_location=None,
                  cell_x_size_at_t_location=None,
                  cell_x_size_at_u_location=None,
                  cell_x_size_at_v_location=None,
                  cell_x_size_at_f_location=None,
                  cell_y_size_at_t_location=None,
                  cell_y_size_at_v_location=None,
                  cell_y_size_at_u_location=None,
                  cell_y_size_at_f_location=None,
                  cell_area_at_t_location=None,
                  cell_area_at_u_location=None,
                  cell_area_at_v_location=None,
                  cell_area_at_f_location=None,
                  cell_mask_at_t_location=None,
                  cell_mask_at_u_location=None,
                  cell_mask_at_v_location=None,
                  cell_mask_at_f_location=None,
                  ):
    pass

# comodo uses the following axis names, independent of coordinate names
# ['X', 'Y', 'Z', 'T']
