#!/usr/bin/python
# -*- coding: utf-8 -*-


cbfStr = u"""
{#- Jinja2 template -#}
###CBF: VERSION 1.5, CBFlib v0.7.8 - PILATUS detectors

data_{{ name }}

_array_data.header_convention "PILATUS_1.2"
_array_data.header_contents
;
# Detector: PILATUS 2M, 24-0111
# {{ datetime }}
# Pixel_size {% if pixel_size %}{{ pixel_size }} m x {{ pixel_size }} m{% else %}172e-6 m x 172e-6 m{% endif %}
# Silicon sensor, thickness 0.000450 m
{%- if Exposure_time is defined %}
# Exposure_time {{ Exposure_time }} s
{%- endif %}
{%- if Exposure_period is defined %}
# Exposure_period {{ Exposure_period }} s
{%- endif %}
{%- if Tau is defined %}
# Tau = {{ Tau }} s
{%- endif %}
{%- if Count_cutoff is defined %}
# Count_cutoff {{ Count_cutoff }} counts
{%- endif %}
{%- if Threshold_setting is defined %}
# Threshold_setting: {{ Threshold_setting }} eV
{%- endif %}
# Gain_setting: low gain (vrf = -0.300)
{%- if N_excluded_pixels is defined %}
# N_excluded_pixels = {{ N_excluded_pixels }}
{%- endif %}
# Excluded_pixels: badpix_mask.tif
# Flat_field: FF_p2m0111_E26000_T13000_vrf_m0p30.tif
# Trim_file: p2m0111_E26000_T13000_vrf_m0p30.bin
# Image_path: /ramdisk/
# Wavelength {% if Wavelength is defined %}{{ Wavelength }}{% else %}0.7{% endif %} A
{%- if Start_angle is defined %}
# Start_angle {{ '{:.2f}'.format(Start_angle) }} deg.
{%- endif %}
{%- if Angle_increment is defined %}
# Angle_increment {{ '{:.2f}'.format(Angle_increment) }} deg.
{%- endif %}
{%- if Omega is defined %}
# Omega {{ '{:.2f}'.format(Omega) }} deg.
{%- endif %}
{%- if Omega_increment is defined %}
# Omega_increment {{ '{:.2f}'.format(Omega_increment) }} deg.
{%- endif %}
{%- if Phi is defined %}
# Phi {{ '{:.2f}'.format(Phi) }} deg.
{%- endif %}
{%- if Phi_increment is defined %}
# Phi_increment {{ '{:.2f}'.format(Phi_increment) }} deg.
{%- endif %}
{%- if Kappa is defined %}
# Kappa {{ Kappa }} deg.
{%- endif %}
{%- if Oscillation_axis is defined %}
# Oscillation_axis {{ Oscillation_axis }}
{%- endif %}
{%- if Detector_distance is defined %}
# Detector_distance {{ Detector_distance }} m
{%- endif %}
{%- if Detector_Voffset is defined %}
# Detector_Voffset {{ Detector_Voffset }} m
{%- endif %}
{%- if Beam_x is defined and Beam_y is defined %}
# Beam_xy ({{ Beam_x }}, {{ Beam_y }}) pixels
{%- endif %}
{%- if Flux is defined %}
# Flux {{ Flux }} counts
{%- endif %}
{%- if Temperature is defined %}
# Temperature {{ '{:.2f}'.format(Temperature) }} K
{%- endif %}
{%- if Blower is defined %}
# Blower {{ '{:.1f}'.format(Blower) }} C
{%- endif %}
{%- if Lakeshore is defined %}
# Lakeshore {{ '{:.2f}'.format(Lakeshore) }} K
{%- endif %}
;

_array_data.data
;
--CIF-BINARY-FORMAT-SECTION--
Content-Type: application/octet-stream;
     conversions="x-CBF_BYTE_OFFSET"
Content-Transfer-Encoding: BINARY
X-Binary-Size: {{ X_Binary_Size }}
X-Binary-ID: 1
X-Binary-Element-Type: "signed 32-bit integer"
X-Binary-Element-Byte-Order: LITTLE_ENDIAN
Content-MD5: {{ Content_MD5 }}
X-Binary-Number-of-Elements: {{ X_Binary_Number_of_Elements }}
X-Binary-Size-Fastest-Dimension: {{ X_Binary_Size_Fastest_Dimension }}
X-Binary-Size-Second-Dimension: {{ X_Binary_Size_Second_Dimension }}
X-Binary-Size-Padding: 4095


"""

cbfTail = b"""

--CIF-BINARY-FORMAT-SECTION----
;


"""


cbfHead = b'\x0c\x1a\x04\xd5'
