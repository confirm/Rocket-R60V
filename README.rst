Rocket R 60V - Python API
=========================

Purpose
-------

This is a Python API for the `Rocket R 60V <https://rocket-espresso.com/r-60v.html>`_.

It provides a proper API and a CLI tool to read & write settings on the machine.

Why this API
------------

Rocket provides its own `iOS <https://apps.apple.com/us/app/rocket-r60v/id1073102815>`_ & `Android <https://play.google.com/store/apps/details?id=com.gicar.Rocket_R60V>`_ apps. However, IMHO the apps are complete rubbish (bad engineering par excellence) and don't work properly. The app reviews tell the same story.

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

.. code-block::

    rocket-r60v --help
    usage: rocket-r60v [-h] [-v] [-f LOGFILE]
                       {active_profile,auto_off,auto_on,brew_boiler_temperature,language,profile_a,profile_b,profile_c,service_boiler,service_boiler_temperature,standby,temperature_unit,total_coffee_count,water_feed,addresses,read,write}
                       ...

    Remote control the Rocket R 60V.

    positional arguments:
      {active_profile,auto_off,auto_on,brew_boiler_temperature,language,profile_a,profile_b,profile_c,service_boiler,service_boiler_temperature,standby,temperature_unit,total_coffee_count,water_feed,addresses,read,write}
        active_profile                the active pressure profile
        auto_off                      the auto off (standby) time
        auto_on                       the auto on time
        brew_boiler_temperature       the desired temperature of the brew boiler
        language                      the language of the machine
        profile_a                     the pressure profile A
        profile_b                     the pressure profile B
        profile_c                     the pressure profile C
        service_boiler                the state of the service boiler
        service_boiler_temperature    the desired temperature of the service boiler
        standby                       the standby state of the machine
        temperature_unit              the temperature unit
        total_coffee_count            the coffee cycles
        water_feed                    the source of the water feed
        addresses                     display all implemented memory addresses / settings (debugging)
        read                          manually read memory data (debugging)
        write                         manually write memory data (debugging)

    optional arguments:
      -h, --help                      show this help message and exit
      -v, --verbose                   verbose mode (-v for error, -vv for warning, -vvv for info, -vvvv for debug)
      -f LOGFILE, --logfile LOGFILE   the filename of the logfile


You can also display the help for a single action:

.. code-block::

    rocket-r60v language --help
    usage: rocket-r60v language [-h] [{English,German,French,Italian}]

    positional arguments:
      {English,German,French,Italian}

    optional arguments:
      -h, --help            show this help message and exit


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

Networking
----------

The Rocket R 60V machine will open a wireless network:

- SSID: ``RocketEspresso``
- Passphrase: ``RocketR60V``

A wireless client can then connect to the wireless network and should get a DHCP lease in the ``192.168.1.0/24`` subnet. 
From there on, you should be able to use the API.

Reverse Engineering
===================

If you're interested how I developed the API and how I reverse engineered the protocol, have a look at the `Reverse Engineering Guide <REVERSE_ENGINEERING.rst>`_.

