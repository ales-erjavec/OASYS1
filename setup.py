#! /usr/bin/env python3

import imp
import os
import subprocess

try:
    from setuptools import find_packages, setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import find_packages, setup
except AttributeError:
    from setuptools import find_packages, setup

NAME = 'OASYS1'

VERSION = '1.0.12'
ISRELEASED = True

DESCRIPTION = 'OrAnge SYnchrotron Suite'
README_FILE = os.path.join(os.path.dirname(__file__), 'README.txt')
LONG_DESCRIPTION = open(README_FILE).read()
AUTHOR = 'Luca Rebuffi, Manuel Sanchez del Rio and Bioinformatics Laboratory, FRI UL'
AUTHOR_EMAIL = 'luca.rebuffi@elettra.eu'
URL = 'https://github.com/lucarebuffi/OASYS1'
DOWNLOAD_URL = 'https://github.com/lucarebuffi/OASYS1'
MAINTAINER = 'Luca Rebuffi, Elettra-Sincrotrone Trieste S.C.p.A.'
MAINTAINER_EMAIL = 'luca.rebuffi@elettra.eu'
LICENSE = 'GPLv3'

KEYWORDS = (
    'ray tracing',
    'simulation',
)

CLASSIFIERS = (
    'Development Status :: 5 - Production/Stable',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Console',
    'Environment :: Plugins',
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: '
    'GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: POSIX',
    'Operating System :: Microsoft :: Windows',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
)

INSTALL_REQUIRES = (
    'setuptools',
    'numpy',
    'scipy',
    'matplotlib',
    'oasys-canvas-core>=0.0.5',
    'oasys-widget-core>=0.0.4',
    'silx>=0.4.0',
    'srxraylib>=1.0.11',
    'syned',
    'wofry',
)

SETUP_REQUIRES = (
    'setuptools',
)


# Return the git revision as a string
def git_version():
    """Return the git revision as a string.

    Copied from numpy setup.py
    """
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        GIT_REVISION = out.strip().decode('ascii')
    except OSError:
        GIT_REVISION = "Unknown"

    return GIT_REVISION


def write_version_py(filename='oasys/version.py'):
    # Copied from numpy setup.py
    cnt = """
# THIS FILE IS GENERATED FROM OASYS SETUP.PY
short_version = '%(version)s'
version = '%(version)s'
full_version = '%(full_version)s'
git_revision = '%(git_revision)s'
release = %(isrelease)s

if not release:
    version = full_version
    short_version += ".dev"
"""
    FULLVERSION = VERSION
    if os.path.exists('.git'):
        GIT_REVISION = git_version()
    elif os.path.exists('oasys/version.py'):
        # must be a source distribution, use existing version file
        version = imp.load_source("oasys.version", "oasys/version.py")
        GIT_REVISION = version.git_revision
    else:
        GIT_REVISION = "Unknown"

    if not ISRELEASED:
        FULLVERSION += '.dev0+' + GIT_REVISION[:7]

    a = open(filename, 'w')
    try:
        a.write(cnt % {'version': VERSION,
                       'full_version': FULLVERSION,
                       'git_revision': GIT_REVISION,
                       'isrelease': str(ISRELEASED)})
    finally:
        a.close()


PACKAGES = [
    "oasys",
    "oasys.canvas",
    "oasys.canvas.styles",
    "oasys.menus",
    "oasys.widgets",
    "oasys.widgets.tools",
]

PACKAGE_DATA = {
    "oasys.canvas": ["icons/*.png", "icons/*.svg"],
    "oasys.canvas.styles": ["*.qss", "orange/*.svg"],
    "oasys.widgets.tools": ["icons/*.png", "icons/*.svg"],
}

ENTRY_POINTS = {
    'oasys.widgets' : (
        "Oasys Tools = oasys.widgets.tools",
    )
}

def setup_package():
    write_version_py()
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        url=URL,
        download_url=DOWNLOAD_URL,
        license=LICENSE,
        keywords=KEYWORDS,
        classifiers=CLASSIFIERS,
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        entry_points = ENTRY_POINTS,
        # extra setuptools args
        zip_safe=False,  # the package can run out of an .egg file
        include_package_data=True,
        install_requires=INSTALL_REQUIRES,
        setup_requires=SETUP_REQUIRES,
    )

if __name__ == '__main__':
    setup_package()
