Rocket R 60V - Python API
=========================

Purpose
-------

This is a Python API for the `Rocket R 60V <https://rocket-espresso.com/r-60v.html>`_.

It provides a proper API and a CLI tool to read & write settings on the machine.

Why this API
------------

Rocket provides its own `iOS <https://apps.apple.com/us/app/rocket-r60v/id1073102815>`_ & `Android <https://play.google.com/store/apps/details?id=com.gicar.Rocket_R60V>`_ apps. However, IMHO the apps are complete rubbish (bad engineering par excellence) and work bad or sometimes not at all. The app reviews tell the same story.

Annoyed and frustrated by the origin apps, I did some research & reverse engineering.

Why Python
----------

I use Python simply because I like it and it allows me to get shit done. 

Installation
============

The Rocket R 60V API can be either installed from source (i.e. downloading or cloning this repository) or via ``pip``:

.. code-block:: bash

    pip install rocket-r60v

CLI command
===========

This package provides a CLI command called ``rocket-r60v`` to communicate with the machine.
To display the available commands, use the ``--help`` flag:

.. code-block:: bash

    rocket-r60v --help
    rocket-r60v {setting} --help

For example, to query the language you can use:

.. code-block:: bash

    rocket-r60v language

If you want to change the language, you can use:

    rocket-r60v language English

Communication
=============

Networking
----------

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

Fortunately, the R 60V uses a relatively simple message protocol format. 

I'm not 100% sure, but I think it's simply an interface to read & write its memory.
I also suppose that the whole logic is built into the original Rocket mobile app itself, and there's no "rich" backend in the machine itself.

Here's an example message which will set the language of the machine to English:

.. code-block::

    w000100010059

+----------+----------+----------+-------------------------------------------------------+
| Position | Example  |  Usage   |                      Description                      |
+==========+==========+==========+=======================================================+
| 1        | ``w``    | Command  | The command, ``r`` for reading, ``w`` for writing     |
+----------+----------+----------+-------------------------------------------------------+
| 2 … 5    | ``0001`` | Offset   | The memory offset (i.e. the language in this example) |
+----------+----------+----------+-------------------------------------------------------+
| 6 … 9    | ``0001`` | Length   | The data length (i.e. 1 byte)                         |
+----------+----------+----------+-------------------------------------------------------+
| 10 … -2  | ``00``   | Data     | The data (i.e. ``00`` = ``English``                   |
+----------+----------+----------+-------------------------------------------------------+
| -2 … END | ``59``   | Checksum | The checksum                                          |
+----------+----------+----------+-------------------------------------------------------+

.. note::

    Please note that these are not "official" terms by Rocket itself.
    I just reverse engineered everything and tried to use matching terms all across my code base.
    Next to these terms, I'll make use of the following:

        - Raw Message: The complete message with its checksum (i.e. ``w000100010059``)
        - Message: The message without its checksum (i.e. ``w0001000100``)
        - Envelope: The command, offset & length (i.e. ``w00010001``)

Reverse Engineering
===================

iOS app communication
---------------------

I've installed the iOS app on my iPhone and analysed the network communication when using the app.
This is achieved by:

- Installing the `iOS app <https://apps.apple.com/us/app/rocket-r60v/id1073102815>`_ on the iPhone
- Installing `Xcode <https://developer.apple.com/xcode/>`_ on the MacBook
- Installing `Wireshark <https://www.wireshark.org/>`_ on the MacBook
- Connecting the iPhone via USB to the MacBook and trusting it
- Opening Xcode and adding the device under ``Window > Devices and Simulators``
- Copy the ``UDID``
- Executing the ``/Library/Apple/usr/bin/rvictl -x {UDID}`` on the shell
- Starting Wireshark and recording on the interface ``rvi0``
- Using the app and doing a single action
- Stopping Wireshark
- Filtering the conversation (e.g. ``ip.addr==192.168.1.1 && ip.addr==192.168.1.11 && tcp.port==1774``)
- Analysing the data packets

There's an excellent tutorial by `pentest_it <https://medium.com/@pentest_it>`_ available which describes `How to capture network traffic from iPhone with tcpdump <https://medium.com/@pentest_it/how-to-capture-network-traffic-from-iphone-with-tcpdump-acd11e030f08>`_.

jffry's library
---------------

Another GitHub user called `jffry <https://github.com/jffry>`_ already did `another client API written in NodeJS <https://github.com/jffry/rocket-r60v>`_ for the Rocket R 60V. Kudos to his reverse engineering & findings!
