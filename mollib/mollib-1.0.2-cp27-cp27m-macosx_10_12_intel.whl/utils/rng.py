"""
Utility functions for generating random numbers.
"""
import random

# def unique_random_numbers(num_steps, total_size, chunk_size=50000, chunk_num, chunk_total, seed=None):
def unique_random_numbers(num_steps, total_size, chunks=5, seed=None):
    """A memory-efficient generator of unique random numbers.
    
    Numbers are sampled in sequential chunks between 0 and total_size.

    Parameters
    ----------
    num_steps: int
        The number of random numbers to return.
    total_size: int
        The total space (range) of numbers to sample.
    chunks: int
        Sample the random numbers in the following number of chunks. A smaller
        chunk number requires more memory. However, this will randomize numbers
        more when total_size is small. Effectively, the range of numbers
        between 0 and total_size is broken up into chunks to ensure that each
        returned number is unique. The numbers are sampled within each 
        sequential chunk.
    seed: int, optional
        If specified, use the following number to seed the random number
        generator.

    Returns
    -------
    random_number_generator
        A generator of random numbers between 0 and total_size.

    Examples
    --------
    >>> g = unique_random_numbers(10, 100, chunks=5, seed=1)
    >>> list(g)
    [4, 18, 34, 28, 57, 47, 76, 73, 91, 97]
    >>> g = unique_random_numbers(11, 100, chunks=5, seed=15)
    >>> list(g)
    [6, 0, 28, 31, 54, 58, 64, 63, 89, 99, 85]
    """
    # Check the arguments
    # The number of steps has to be at least as large as the the number of
    # chunks to generate evenly distributed numbers.
    if num_steps < chunks:
        chunks = num_steps

    # Initialize parameters
    if seed is not None:
        random.seed(seed)
    chunk_size = int(total_size / chunks)
    chunk_steps = int(num_steps / chunks)

    for chunk in range(chunks):
        if chunk == chunks - 1 and chunk_steps < num_steps:
            chunk_steps = num_steps

        numbers = list(range(chunk * chunk_size, (chunk + 1) * chunk_size))
        random.shuffle(numbers)
        for step in range(chunk_steps):
            if num_steps > 0 and numbers:
                yield numbers.pop()
            else:
                return
            num_steps -= 1
