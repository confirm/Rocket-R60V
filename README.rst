Rocket R 60V Python API
=======================

This is a Python API for the Rocket R 60V.

The Rocket R 60V protocol
=========================

Network Communication
---------------------

The Rocket R 60V machine will open a wireless network:

- SSID: ``RocketEspresso``
- Passphrase: ``RocketR60V``

A wireless client can then connect to the wireless network and should get a DHCP lease in the `192.168.1.0/24` subnet. 

The R 60V has a TCP listener which can be used to configure it:

- IP address: ``192.168.1.1``
- TCP port: ``1774``

.. note:: 

    There's no HTTP/REST interface or alike. It's all plain TCP.

Message Protocol
----------------

Fortunately, the R 60V uses a relatively simple message format. 

I'm not 100% sure, but I think it's simply an interface to read & write its memory.
I also suppose that the whole logic is built into the original Rocket mobile app itself, and there's no "rich" backend in the machine itself.

Here's an example of how to set the language to English.

.. code-block::

    w000100010059

+----------+----------+----------+-------------------------------------------------------+
| Position | Example  |  Usage   |                      Description                      |
+==========+==========+==========+=======================================================+
| 1        | ``w``    | Command  | The command, ``r`` for reading, ``w`` for writing     |
+----------+----------+----------+-------------------------------------------------------+
| 2-5      | ``0001`` | Offset   | The memory offset (i.e. the language in this example) |
+----------+----------+----------+-------------------------------------------------------+
| 6-9      | ``0001`` | Length   | The data length (i.e. 1 byte)                         |
+----------+----------+----------+-------------------------------------------------------+
| …        | ``00``   | Data     | The data (i.e. ``00`` = ``English``                   |
+----------+----------+----------+-------------------------------------------------------+
| -2       | ``59``   | Checksum | The checksum                                          |
+----------+----------+----------+-------------------------------------------------------+

.. note::

    Please note that these are not "official" terms by Rocket itself.
    I just reverse engineered everything and tried to find matching terms all across my code base.
    Next to these terms, I'll make use of the following:

        - Raw Message: The complete message with its checksum (i.e. ``w000100010059``)
        - Message: The message without its checksum (i.e. ``w0001000100``)
        - Envelope: The command, offset & length (i.e. ``w00010001``)

