"""
Mutual Exclusity <=> MUX

Interleaving in hardware design is the process of rearranging sequential data storage into two or
more non-contiguous storage blocks to increase performance.

A line buffer is used to store a single line of video from
an image. The buffer must be able to be read and written every clock cycle. The simplest
solution would be to map the line buffer storage array to a RAM that has both a read port and a
write port. These types of RAM are usually referred to as RAM with separate read/write ports.
The drawback to using these types of RAMs is that they require as much as 50% more area than
a true singleport RAM. The problem with using singleport RAM is that it cannot be read and
written in the same clock cycle, which makes implementing something like a line buffer a little
tricky.


“Windowing” of 1-D Data Streams

2-D Windowing

"""
