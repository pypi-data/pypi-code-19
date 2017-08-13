# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

class Specs:
    """The simulation specs."""

    def __init__(self, start_time, stop_time, dt,
                 method = 'RungeKutta4',
                 generator_type = 'SimpleGenerator'):
        """Initializes a new instance."""
        self.start_time = start_time
        self.stop_time = stop_time
        self.dt = dt
        self.method = method
        self.generator_type = generator_type

    def write(self, file, indent = ''):
        """Write the specs in the file."""
        file.write(indent)
        file.write('Specs { spcStartTime = ')
        file.write(str(self.start_time))
        file.write(',\n')
        file.write(indent)
        file.write('        spcStopTime = ')
        file.write(str(self.stop_time))
        file.write(',\n')
        file.write(indent)
        file.write('        spcDT = ')
        file.write(str(self.dt))
        file.write(',\n')
        file.write(indent)
        file.write('        spcMethod = ')
        file.write(self.method)
        file.write(',\n')
        file.write(indent)
        file.write('        spcGeneratorType = ')
        file.write(self.generator_type)
        file.write(' }\n')
