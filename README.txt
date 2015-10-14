OASYS
======

OASYS (OrAnge SYnchrotron Suite) is a graphical environment
for optic simulation software used in synchrotron facilities,
based on Orange 3.

OASYS package requires Python 3.3 or newer.


Installing
----------

OASYS is pip installable (https://pip.pypa.io/), simply run::

    pip install oasys

to install it.

OASYS requires PyQt, which is not pip-installable in Python 3. You
have to download and install it system-wide. If you are installing
in to a virtual environment make sure it is created with the
`--system-site-packages` so it will have access to the installed
PyQt4.


Starting OASYS
--------------

To start OASYS from the command line, run::

     python3 -m oasys.canvas

The OASYS does not itself come with any widget components. Use the
'Options->Add-ons' menu entry to install the desired widget set.
