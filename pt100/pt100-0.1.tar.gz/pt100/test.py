import lookuptable

#values = [100.0, 120.0]
values = [100.015, 120.00] # actual values of our references (tested with the Agilent table top multimeter)

results = lookuptable.interp_resist_to_temp_np(values)
for i in range(len(values)):
    print(values[i], "Ohm = ", results[i], " deg C")

for val in values:
    temp = lookuptable.interp_resist_to_temp_naive(val)
    print(val, "Ohm = ", temp, " deg C")



