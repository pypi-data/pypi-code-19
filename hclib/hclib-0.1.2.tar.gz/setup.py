from setuptools import setup

desc = """
Example
=======

.. code:: python

    #!/usr/bin/env python3

    import hclib


    # Make a callback function with two parameters.
    def on_message(connector, data):
        # The second parameter (<data>) is the data received.
        print(data)
        print(connector.onlineUsers)
        # Checks if someone joined the channel.
        if data["type"] == "online add":
            # Sends a greeting the person joining the channel.
            connector.send("Hello {}".format(data["nick"]))


    if __name__ == "__main__":
        hclib.HackChat(on_message, "myBot", "botDev")
"""

setup(
    name = "hclib",
    py_modules = ["hclib"],
    version = "0.1.2",
    description = "A library to connect to https://hack.chat/",
    long_description = desc,
    url = "https://github.com/neelkamath/hack.chat-library",
    author = "Neel Kamath",
    author_email = "neelkamath@protonmail.com",
    license = "MIT",
    keywords = "hack.chat library",
    install_requires = ["websocket-client"]
)
