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
There are several ways to do this, either by installing it on your Android phone or by downloading it directly from the Google Play store. Just google for it or use the `APK Downloader by APK.Support <https://apk.support/apk-downloader>`_.

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

Of course, a proper grep like ``grep -R 'ADDRESS:I'`` can probably disclose all available addresses:

.. code-block:: 

    smali/singleton/DbCounterSingleton.smali:.field public static final CICLI_MANUT_ADDRESS:I = 0x59
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_K1_GR1_ADDRESS:I = 0x97
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_K1_GR2_ADDRESS:I = 0xa1
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_K1_GR3_ADDRESS:I = 0xab
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_K2_GR1_ADDRESS:I = 0x99
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_K2_GR2_ADDRESS:I = 0xa3
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_K2_GR3_ADDRESS:I = 0xad
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_K3_GR1_ADDRESS:I = 0x9b
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_K3_GR2_ADDRESS:I = 0xa5
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_K3_GR3_ADDRESS:I = 0xaf
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_K4_GR1_ADDRESS:I = 0x9d
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_K4_GR2_ADDRESS:I = 0xa7
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_K4_GR3_ADDRESS:I = 0xb1
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_K5_GR1_ADDRESS:I = 0x9f
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_K5_GR2_ADDRESS:I = 0xa9
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_K5_GR3_ADDRESS:I = 0xb3
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_LAVAGGIO_ADDRESS:I = 0xc7
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_PARZ_ADDRESS:I = 0x4b
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_POMPA_ADDRESS:I = 0xcb
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_RIEMPIMENTO_ADDRESS:I = 0xcf
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_TEA1_ADDRESS:I = 0xb5
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_TEA2_ADDRESS:I = 0xb7
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_TEA3_ADDRESS:I = 0xb9
    smali/singleton/DbCounterSingleton.smali:.field public static final COUNT_TOT_ADDRESS:I = 0x4d
    smali/singleton/DbCounterSingleton.smali:.field public static final LITRI_FILTRO_ADDRESS:I = 0xc3
    smali/singleton/SettingsSingleton.smali:.field private static final ENAB_CALDVAP_ADDRESS:I = 0x49
    smali/singleton/SettingsSingleton.smali:.field private static final ENAB_PROG_ADDRESS:I = 0x55
    smali/singleton/SettingsSingleton.smali:.field private static final KD_CAFFE_ADDRESS:I = 0x10
    smali/singleton/SettingsSingleton.smali:.field private static final KD_GRUPPO_ADDRESS:I = 0x12
    smali/singleton/SettingsSingleton.smali:.field private static final KI_CAFFE_ADDRESS:I = 0xa
    smali/singleton/SettingsSingleton.smali:.field private static final KI_GRUPPO_ADDRESS:I = 0xc
    smali/singleton/SettingsSingleton.smali:.field private static final KP_CAFFE_ADDRESS:I = 0x4
    smali/singleton/SettingsSingleton.smali:.field private static final KP_GRUPPO_ADDRESS:I = 0x6
    smali/singleton/SettingsSingleton.smali:.field private static final LINGUA_ADDRESS:I = 0x1
    smali/singleton/SettingsSingleton.smali:.field private static final STATO_MACCHINA_ADDRESS:I = 0x4a
    smali/singleton/SettingsSingleton.smali:.field private static final TEMPERATURA_VAPORE_ADDRESS:I = 0x3
    smali/singleton/SettingsSingleton.smali:.field private static final TEMP_SET_CAF_ADDRESS:I = 0x2
    smali/singleton/SettingsSingleton.smali:.field private static final TEMP_SET_GRUPPO_ADDRESS:I = 0x4c
    smali/singleton/SettingsSingleton.smali:.field private static final TEMP_SET_LANCIA_ADDRESS:I = 0x45
    smali/singleton/SettingsSingleton.smali:.field private static final TIPO_TASTIERA_ADDRESS:I = 0x47
    smali/singleton/SettingsSingleton.smali:.field private static final T_LAV_LANCIA_ADDRESS:I = 0x48
    smali/singleton/SettingsSingleton.smali:.field private static final UM_TEMP_ADDRESS:I
    smali/singleton/PrebrewingSingleton.smali:.field public static final ENAB_PRE_INF_ADDRESS:I = 0x2b
    smali/singleton/PrebrewingSingleton.smali:.field public static final T_OFF_PRE_INF_ADDRESS:I = 0x2c
    smali/singleton/PrebrewingSingleton.smali:.field public static final T_ON_PRE_INF_ADDRESS:I = 0x30
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_K1_GR1_ADDRESS:I = 0x5d
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_K1_GR2_ADDRESS:I = 0x67
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_K1_GR3_ADDRESS:I = 0x71
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_K2_GR1_ADDRESS:I = 0x5f
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_K2_GR2_ADDRESS:I = 0x69
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_K2_GR3_ADDRESS:I = 0x73
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_K3_GR1_ADDRESS:I = 0x61
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_K3_GR2_ADDRESS:I = 0x6b
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_K3_GR3_ADDRESS:I = 0x75
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_K4_GR1_ADDRESS:I = 0x63
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_K4_GR2_ADDRESS:I = 0x6d
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_K4_GR3_ADDRESS:I = 0x77
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_K5_GR1_ADDRESS:I = 0x65
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_K5_GR2_ADDRESS:I = 0x6f
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_K5_GR3_ADDRESS:I = 0x79
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_TEA1_ADDRESS:I = 0x7b
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_TEA2_ADDRESS:I = 0x7c
    smali/singleton/DosesSingleton.smali:.field public static final DOSES_COUNT_TEA3_ADDRESS:I = 0x7d
    smali/singleton/TimerSingleton.smali:.field public static final DAY_OFF_ADDRESS:I = 0x55
    smali/singleton/TimerSingleton.smali:.field public static final MIN_AUTO_OFF_ADDRESS:I = 0x54
    smali/singleton/TimerSingleton.smali:.field public static final MIN_AUTO_ON_ADDRESS:I = 0x52
    smali/singleton/TimerSingleton.smali:.field public static final ORA_AUTO_OFF_ADDRESS:I = 0x53
    smali/singleton/TimerSingleton.smali:.field public static final ORA_AUTO_ON_ADDRESS:I = 0x51
    smali/singleton/TextSingleton.smali:.field public static final NOME_ADDRESS:I = 0x6
    smali/singleton/TextSingleton.smali:.field public static final NUMERO_ADDRESS:I = 0x17

jffry's library
---------------

Another GitHub user called `jffry <https://github.com/jffry>`_ already did `another client API written in NodeJS <https://github.com/jffry/rocket-r60v>`_ for the Rocket R 60V.  
Kudos to his excellent `reverse engineering <https://github.com/jffry/rocket-r60v/blob/master/doc/Reverse%20Engineering.md>`_ and for publishing his findings!