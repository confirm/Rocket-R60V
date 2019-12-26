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

Usage
=====

Installation
------------

The Rocket R 60V API can either installed from source (i.e. downloading or cloning this repository) or via ``pip``:

.. code-block:: bash

    pip install rocket-r60v

CLI command
-----------

This package provides a CLI command called ``rocket-r60v`` to communicate with the machine.
To display the available commands, use the ``--help`` flag:

.. code-block:: bash

    rocket-r60v --help
    rocket-r60v {setting} --help

For example, to query the language you can use:

.. code-block:: bash

    rocket-r60v language

If you want to change the language, you can use:

.. code-block:: bash

    rocket-r60v language English

Python API
----------

The Python API can be used like this:

.. code-block:: python

    from rocket_r60v.machine import Machine

    machine = Machine()
    machine.connect()

    # Get language unit from machine.
    print(machine.language)

    # Set language unit on machine.
    machine.temperature_unit = 'English'

All available settings can be displayed via CLI command ``rocket-r60v --help`` or by inspecting the `settings module <rocket_r60v/settings/__init__.py>`_.

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

Please have a look at the `Message class in the message module <rocket_r60v/message.py>`_ for more details about the exact message protocol.

Reverse Engineering
===================

jffry's library
---------------

Another GitHub user called `jffry <https://github.com/jffry>`_ already did `another client API written in NodeJS <https://github.com/jffry/rocket-r60v>`_ for the Rocket R 60V.  
Kudos to his excellent `reverse engineering <https://github.com/jffry/rocket-r60v/blob/master/doc/Reverse%20Engineering.md>`_ and for publishing his findings!

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

Android APK decode
------------------

Download the `Rocket Espresso R 60V android app <https://play.google.com/store/apps/details?id=com.gicar.Rocket_R60V>`_ to your PC.  
There are several ways to do this, either by installing it on your Android phone or by downloading it directly from the Google Play store (just google for it).

Then install the `Apktool <https://github.com/iBotPeaches/Apktool>`_ to decode the APK. There's a `Homebrew Formulae <https://formulae.brew.sh/formula/apktool>`_ available for Mac OS X.

When you've downloaded the Android app and installed apktool, you can decode the app by running:

.. code-block::

    apktool decode -o rocket_app {Rocket apk file}

There should now be a ``rocket/`` directory with the decoded app. 
When browsing through the smali files, you can find hints how to access different data of the machine.

For example, the ``smali/singleton/SettingsSingleton.smali`` contains lines which look like this:

.. code-block::

    .field private static final INGRESSO_ACQUA:I = 0x46

These are significant static fields which point to a byte address of a specific setting. Fortunately, with a bit knowledge of Italian (or a translator), you found yourself a mapping between the settings and the actual memory addresses. The addresses are 16bit unsigned integers, encoded in uppercase hex characters.

Debugging with the rocket-r60v CLI tool
---------------------------------------

You can read any memory address by using the ``rocket-r60v`` CLI tool:

.. code-block::

    usage: rocket-r60v read [-h] address length

    positional arguments:
      address     the memory address (unsigned 16-bit integer)
      length      the data length (unsigned 16-bit integer)

    optional arguments:
      -h, --help  show this help message and exit

There's also an option for writing (use with caution):

.. code-block::

    usage: rocket-r60v write [-h] [-r] address length data

    positional arguments:
      address     the memory address (unsigned 16-bit integer)
      length      the data length (unsigned 16-bit integer)
      data        the memory data (8-bit unsigned integers or hex value if raw)

    optional arguments:
      -h, --help  show this help message and exit
      -r, --raw   send raw data, do not encode data to hex
    