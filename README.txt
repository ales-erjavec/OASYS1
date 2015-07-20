OASYS
======

OrAnge SYnchrotron Suite

Installing
----------

This version of Orange requires Python 3.3 or newer. To build it, run::

    python setup.py develop

inside a virtual environment.

Installation of Scipy and is sometimes challenging because of their
non-python dependencies that have to be installed manually.

Starting OASYS
--------------

OASYS requires PyQt, which is not pip-installable in Python 3. You
have to download and install it system-wide. Make sure that the virtual
environment for orange is created with --system-site-packages, so it will have
access to the installed PyQt4.

To start OASYS from the command line, run::

     python3 -m oasys.canvas

The OASYS does not itself come with any widget components. Use the
'Options->Add-ons' menu entry to install the desired widget set.
