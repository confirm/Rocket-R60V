Reverse Engineering
===================

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

If you want to display all implemented byte addresses and the settings, run:

.. code-block:: bash

    ./rocket-r60v addresses

TCP server
----------

The R 60V has a TCP listener which accepts unencrypted connections to configure it:

- IP address: ``192.168.1.1``
- TCP port: ``1774``

.. note:: 

    There's no HTTP/REST interface or alike. It's all plain TCP, therefore this Python API.

Message protocol
----------------

Fortunately, the R 60V uses a relatively simple message protocol format. 

I'm not 100% sure, but I think it's simply an interface to read & write the memory of the Rocket R 60V.
I also suppose that the whole logic is built into the original Rocket mobile app itself, and there's no "rich" backend in the machine itself.

Here's an example message which will set the language of the machine to English:

.. code-block::

    w000100010059

+------------------------+--------------------------------------+----------+-----------------------------------------------------+----------+
|        Position        |              Data Type               |  Usage   |                     Description                     | Example  |
+========================+======================================+==========+=====================================================+==========+
| 1                      | 8-bit unsigned integer,              | command  | The command.                                        | ``w``    |
|                        | encoded as uppercase hex value       |          | Uses ``r`` (``0x72``) for reading,                  |          |
|                        |                                      |          | or ``w`` (``0x77``) for writing.                    |          |
+------------------------+--------------------------------------+----------+-----------------------------------------------------+----------+
| 2 … 5                  | 16-bit unsigned integer,             | address  | The memory address.                                 | ``0001`` |
|                        | encoded as uppercase hex value       |          |                                                     |          |
+------------------------+--------------------------------------+----------+-----------------------------------------------------+----------+
| 6 … 9                  | 16-bit unsigned integer,             | length   | The length of the data.                             | ``0001`` |
|                        | encoded as uppercase hex value       |          |                                                     |          |
+------------------------+--------------------------------------+----------+-----------------------------------------------------+----------+
| 10 … (10 + length * 2) | sequence of 8-bit unsigned integers, | data     | The data itself.                                    | ``00``   |
|                        | encoded as uppercase hex values      |          | The length must be multiplied by 2,                 |          |
|                        |                                      |          | as an 8-bit integer uses 2 hex chars (i.e. ``FF``). |          |
+------------------------+--------------------------------------+----------+-----------------------------------------------------+----------+
| (END - 2) … END        | 8-bit unsigned integer,              | checksum | The checksum.                                       | ``59``   |
|                        | encoded as uppercase hex value       |          | Modulo 256 of the sum of all bytes.                 |          |
+------------------------+--------------------------------------+----------+-----------------------------------------------------+----------+

.. note::

    Please note that these are not "official" terms by Rocket itself.
    I just reverse engineered everything and tried to use matching terms all
    across my code base. Next to these terms, I'll make use of the
    following ones:

        - Raw Message: The complete message with its checksum (i.e. ``w000100010059``)
        - Message: The message without its checksum (i.e. ``w0001000100``)
        - Envelope: The command, address & length (i.e. ``w00010001``)

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
There are several ways to do this, either by installing it on your Android phone and extracting it from there, or by downloading it directly from the Google Play store. Just google for it or use the `APK Downloader by APK.Support <https://apk.support/apk-downloader>`_.

Install the `Apktool <https://github.com/iBotPeaches/Apktool>`_ to decode the APK. There's a `Homebrew Formulae <https://formulae.brew.sh/formula/apktool>`_ available for Mac OS X.

When you've downloaded the Android app and installed ``apktool``, you can decode the app by running:

.. code-block::

    apktool decode -o rocket_app {Rocket apk file}

There should now be a ``rocket/`` directory with the decoded app. 
When browsing through the ``smali`` files, you can find hints how to access different data of the machine.

For example, the ``smali/singleton/SettingsSingleton.smali`` contains lines which look like this:

.. code-block::

    .field private static final INGRESSO_ACQUA:I = 0x46

These are significant static fields which point to a byte address of a specific setting. Fortunately, with a bit knowledge of Italian (or a translator), you found yourself a mapping between the settings and the actual memory addresses. The addresses are 16bit unsigned integers, encoded in uppercase hex characters.

A bit of grepping like ``grep -R 'ADDRESS:I'`` or ``grep -R 'field public static final \w\+:I = 0x[0-9a-f]\{1,2\}$'`` can disclose even more addresses!

.. note::

    Please note that the Android app is developed in Java. Fortunately, Java is an interpreted language and thus the shipped bytecode can be decoded back into "readable" source code.

    Unfortunately, most iOS apps are compiled into machine code. The Rocket iOS app is no exception to this. There's only compiled machine code and no bytecode available. Decompiling machine code back into "readable" source code (e.g. Objectiv-C or Swift) is a much harder task. It would even be easier to disassembling it into assembly, but even that is a hard thing to do and hard to reverse engineer.

    Therefor I'd stick with the Java bytecode / APK and decode it for reverse engineering of the app / protocol. 

Memory addresses
----------------

Here's a list of memory addresses I found in the bytecode, with an optional link to the implementation of the setting:

+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
|    State    |  Address   |           Field Name           |                             Implementation / Notes                             |    example data    |
+=============+============+================================+================================================================================+====================+
| implemented | ``0x01``   | ``LINGUA_ADDRESS``             | `Language <rocket_r60v/settings/language.py>`_                                 |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| implemented | ``0x02``   | ``TEMP_SET_CAF_ADDRESS``       | `Brew Boiler Temperature <rocket_r60v/settings/brew_boiler.py>`_               |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| implemented | ``0x03``   | ``TEMPERATURA_VAPORE_ADDRESS`` | `Service Boiler Temperature <rocket_r60v/settings/service_boiler.py>`_         |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x04``   | ``KP_CAFFE_ADDRESS``           | *coffee [P]ID?*                                                                | ``[15, 0]``        |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x06``   | ``KP_GRUPPO_ADDRESS``          | *group [P]ID?*                                                                 | ``[40, 0]``        |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x0A``   | ``KI_CAFFE_ADDRESS``           | *coffee P[I]D?*                                                                | ``[1, 0]``         |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x0C``   | ``KI_GRUPPO_ADDRESS``          | *group P[I]D?*                                                                 | ``[1, 0]``         |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x10``   | ``KD_CAFFE_ADDRESS``           | *coffee PI[D]?*                                                                | ``[65, 0]``        |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x12``   | ``KD_GRUPPO_ADDRESS``          | *group PI[D]?*                                                                 | ``[5, 0]``         |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| implemented | ``0x16``   |                                | `Pressure Profile A <rocket_r60v/settings/profiles.py>`_                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| implemented | ``0x26``   |                                | `Pressure Profile B <rocket_r60v/settings/profiles.py>`_                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| implemented | ``0x36``   |                                | `Pressure Profile C <rocket_r60v/settings/profiles.py>`_                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x2B``   | ``ENAB_PRE_INF_ADDRESS``       | *enable pre-infusion?*                                                         | ``[0]``            |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x2C``   | ``T_OFF_PRE_INF_ADDRESS``      | *time off-preinfusion?*                                                        | ``[0, 0, 0, 0]``   |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x30``   | ``T_ON_PRE_INF_ADDRESS``       | *time on pre-infusion?*                                                        | ``[40, 90, 0, 0]`` |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x45``   | ``TEMP_SET_LANCIA_ADDRESS``    |                                                                                | ``[0]``            |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| implemented | ``0x46``   | ``INGRESSO_ACQUA``             | `Water Feed <rocket_r60v/settings/water_feed.py>`_                             |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| implemented | ``0x47``   | ``TIPO_TASTIERA_ADDRESS``      | `Active Profile <rocket_r60v/settings/profiles.py>`_                           |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x48``   | ``T_LAV_LANCIA_ADDRESS``       |                                                                                | ``[15]``           |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| implemented | ``0x49``   | ``ENAB_CALDVAP_ADDRESS``       | `Service Boiler <rocket_r60v/settings/service_boiler.py>`_                     |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| implemented | ``0x4A``   | ``STATO_MACCHINA_ADDRESS``     | `Standby <rocket_r60v/settings/standby.py>`_                                   |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x4B``   | ``COUNT_PARZ_ADDRESS``         | *partial coffee counter? counts up with* ``0x4d``                              |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x4C``   | ``TEMP_SET_GRUPPO_ADDRESS``    |                                                                                | ``[0]``            |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| implemented | ``0x4D``   | ``COUNT_TOT_ADDRESS``          | `Total Coffee Count <rocket_r60v/settings/count.py>`_                          |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x51``   | ``ORA_AUTO_ON_ADDRESS``        | `Auto On Hour <rocket_r60v/settings/timer.py>`_                                |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x52``   | ``MIN_AUTO_ON_ADDRESS``        | `Auto On Minute <rocket_r60v/settings/timer.py>`_                              |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x53``   | ``ORA_AUTO_OFF_ADDRESS``       | `Auto Off Hour <rocket_r60v/settings/timer.py>`_                               |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x54``   | ``MIN_AUTO_OFF_ADDRESS``       | `Auto Off Minute <rocket_r60v/settings/timer.py>`_                             |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x55``   | ``DAY_OFF_ADDRESS``            | *weekdays when timer isn't active?*                                            | ``[0, 0, 0, 0]``   |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x55``   | ``ENAB_PROG_ADDRESS``          | *enable programming? same address as field above.*                             |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x59``   | ``CICLI_MANUT_ADDRESS``        | *maintenance cycle by Rocket?*                                                 | ``[0, 0, 0, 0]``   |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x5D``   | ``DOSES_COUNT_K1_GR1_ADDRESS`` |                                                                                |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x5F``   | ``DOSES_COUNT_K2_GR1_ADDRESS`` |                                                                                |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x61``   | ``DOSES_COUNT_K3_GR1_ADDRESS`` |                                                                                |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x63``   | ``DOSES_COUNT_K4_GR1_ADDRESS`` |                                                                                |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x65``   | ``DOSES_COUNT_K5_GR1_ADDRESS`` |                                                                                |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x67``   | ``DOSES_COUNT_K1_GR2_ADDRESS`` |                                                                                |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x69``   | ``DOSES_COUNT_K2_GR2_ADDRESS`` |                                                                                |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x6B``   | ``DOSES_COUNT_K3_GR2_ADDRESS`` |                                                                                |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x6D``   | ``DOSES_COUNT_K4_GR2_ADDRESS`` |                                                                                |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x6F``   | ``DOSES_COUNT_K5_GR2_ADDRESS`` |                                                                                |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x71``   | ``DOSES_COUNT_K1_GR3_ADDRESS`` |                                                                                |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x73``   | ``DOSES_COUNT_K2_GR3_ADDRESS`` |                                                                                |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0x75``   | ``DOSES_COUNT_K3_GR3_ADDRESS`` |                                                                                |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0x77``   | ``DOSES_COUNT_K4_GR3_ADDRESS`` | *not working, invalid response envelope (when length 2)*                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0x79``   | ``DOSES_COUNT_K5_GR3_ADDRESS`` | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0x7B``   | ``DOSES_COUNT_TEA1_ADDRESS``   | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0x7C``   | ``DOSES_COUNT_TEA2_ADDRESS``   | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0x7D``   | ``DOSES_COUNT_TEA3_ADDRESS``   | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0x97``   | ``COUNT_K1_GR1_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0x99``   | ``COUNT_K2_GR1_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0x9B``   | ``COUNT_K3_GR1_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0x9D``   | ``COUNT_K4_GR1_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0x9F``   | ``COUNT_K5_GR1_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xA1``   | ``COUNT_K1_GR2_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xA3``   | ``COUNT_K2_GR2_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xA5``   | ``COUNT_K3_GR2_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xA7``   | ``COUNT_K4_GR2_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xA9``   | ``COUNT_K5_GR2_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xAB``   | ``COUNT_K1_GR3_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xAD``   | ``COUNT_K2_GR3_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xAF``   | ``COUNT_K3_GR3_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xB1``   | ``COUNT_K4_GR3_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xB3``   | ``COUNT_K5_GR3_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xB5``   | ``COUNT_TEA1_ADDRESS``         | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xB7``   | ``COUNT_TEA2_ADDRESS``         | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xB9``   | ``COUNT_TEA3_ADDRESS``         | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xC3``   | ``LITRI_FILTRO_ADDRESS``       | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xC7``   | ``COUNT_LAVAGGIO_ADDRESS``     | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xCB``   | ``COUNT_POMPA_ADDRESS``        | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| invalid     | ``0xCF``   | ``COUNT_RIEMPIMENTO_ADDRESS``  | *not working, invalid response envelope*                                       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| implemented | ``0xB000`` |                                | `Current Brew Boiler Temperature <rocket_r60v/settings/brew_boiler.py>`_       |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| implemented | ``0xB001`` |                                | `Current Service Boiler Temperature <rocket_r60v/settings/service_boiler.py>`_ |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0xB002`` |                                | *current pressure*                                                             |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+
| ?           | ``0xB007`` |                                | *display content*                                                              |                    |
+-------------+------------+--------------------------------+--------------------------------------------------------------------------------+--------------------+

jffry's library
---------------

Another GitHub user called `jffry <https://github.com/jffry>`_ already did `another client API written in NodeJS <https://github.com/jffry/rocket-r60v>`_ for the Rocket R 60V.  
Kudos to his excellent `reverse engineering <https://github.com/jffry/rocket-r60v/blob/master/doc/Reverse%20Engineering.md>`_ and for publishing his findings!