import os

from collab import collab


# A TOY EXAMPLE: Fibonacci
# This file exists to demonstrate how to use the collab library.

# this program implements the fibonacci sequence.
# It takes up to two files as input, which should contain a number each.
# It creates a new file and writes the next number in the sequence to it.
# Then, this program asks the Execution Environment to call this program again on the newly generated file and the last previous one.

##############################################################################################################
# The manager: wrapping your code around this enables logging of log messages and exceptions/errors
# (the parameters here are shown with their default values)
##############################################################################################################

with collab.manager(suppress_exceptions_after_logging_them=False, redirect_stdout_to_log=True) as col:

    # these log statements are written to a file that is available via the collab website for inspection,
    # but that is not available to other programs running in collab.
    # they are therefore useful for debugging and gathering information about the program's performance.
    col.log("example log message")

    # if the parameter redirect_stdout_to_log in the manager is set to True, print() and other functions that use stdout get redirected to the logger
    print("test log statement from console 123")

    ##############################################################################################################
    # input: reading files and understanding the context
    ##############################################################################################################

    # get an integer indicating what step in the current execution environment this is

    step = collab.get_current_step()

    # get a list of inputs that were given to this program

    inputs = collab.get_inputs()

    if len(inputs) > 2:
        # if something goes wrong and an exception is thrown, the error and its stacktrace are automatically written to an error log file.
        # just like the log file, this file can be inspected on the website, but is not available to other programs running in collab.
        raise IOError("this program takes up to two files as input, which must contain a number each")
    input_numbers = []
    identifier_of_last_input_object = None

    for input_object in inputs:

        # investigate them more closely

        input_file = input_object.file
        input_object_identifier = input_object.identifier # this identifier is what is used by Tags to reference objects

        # use the input file to see what this program has received as its input

        with open(input_file, 'r') as f:
            inpt = f.read()
            num = int(inpt)
            input_numbers.append(num)
        identifier_of_last_input_object = input_object_identifier

    # find out why this program was triggered

    trigger = collab.get_trigger()
    event_type = trigger.event_type
    reason = trigger.reason

    # get a list of tags that have been made at earlier stages of the execution

    tags = collab.get_tags()

    # look at the tags more specifically

    for example_tag in tags:
        sym1 = example_tag.symbol
        for obj_identifier in example_tag.arguments: # this can refer to one of a number of things, but usually it's an object or another tag.
            pass

    ##############################################################################################################

    # at this point, all inputs have been read and the context of this program's execution has been understood.
    # the actual operations of your program should go here.
    # for this simple example program, we implement the logic of the Fibonacci sequence.

    if len(input_numbers) != 2:
        next_number = 1
    else:
        next_number = input_numbers[0] + input_numbers[1]

    ##############################################################################################################

    # create an output, to make the results of this program available to other programs and to the Execution Environment.
    # you can create multiple outputs, and they will be added in the order in which they were created with this function.

    output_object = collab.add_output_file()
    output_file = output_object.file
    output_object_identifier = output_object.identifier # this identifier is what is used by Tags to reference objects

    # write to the output file whatever you want to communicate to the outside
    # in this example, that's just the number we read incremented by one

    with open(output_file, 'w') as f:
        f.write(str(next_number))

    # create a new global tag using a preexisting Collab Symbol

    collab.create_tag("continue-executing-fibonacci-sequence")

    # create a new tag to mark a relation between one of the input files and the new output file.
    # this can be used to tell other programs about the relationship between these files.
    # (you can use either the identifier of an object, or the object itself as an argument)

    if identifier_of_last_input_object is None:
        collab.create_tag("first-in-fibonacci-sequence", output_object)
    else:
        collab.create_tag("next-in-fibonacci-sequence", identifier_of_last_input_object, output_object)

    # request the Execution Environment to call this program again (assuming this program is called 'fibonacci')
    # using the file we just created and the second of the current input arguments as its new inputs.
    # (if we don't do this, the Execution Environment will use all existing Tags in this Execution Environment
    # and all Execution Rules in the database of the server to determine what to do next)
    # Note that this function works differently depending on the type of the request.

    if identifier_of_last_input_object is None:
        collab.add_event_request('execute_program', 'fibonacci', output_object_identifier)
    else:
        collab.add_event_request('execute_program', 'fibonacci', identifier_of_last_input_object, output_object_identifier)


    # This function is called automatically when the manager closes, but it is possible to call it earlier, too,
    # if you are unsure if the program might time out later, so that you can at least output some preliminary results.
    # (calling it here would be unnecessary, so this is only mentioned for later reference)
    
    #collab.finalize_output()







