#!/usr/bin/env bash
echo
set -e

usage() {
    echo 'usage: build-macos-app.sh [--python-version VER] [--pip-arg ARG] APPPATH
Create (build) an macOS application bundle

Options:
    --python-version VERSION
        Python version to install in the application bundle (default: 3.7.5)

    --pip-arg  ARG
        Pip install arguments to populate the python environemnt in the
        application bundle. Can be used multiple times.
        If not supplied then by default the latest PyPi published Orange3 is
        used.

    -h|--help
        Print this help

Examples
    build-macos-app.sh ~/Applications/Oasys1.2.app
        Build the application using the latest published version on pypi

    build-macos-app.sh --pip-arg={Oasys1.2==3.3.12,PyQt5} ~/Applications/Oasys1.2.app
        Build the application using the specified Orange version

    build-macos-app.sh --pip-arg=path-tolocal-checkout ~/Applications/Oasys1.2-Dev.app
        Build the application using a local source checkout

    build-macos-app.sh --pip-arg={-e,path-tolocal-checkout}  ~/Applications/Oasys1.2-Dev.app
        Build the application and install orange in editable mode

    buils-macos-app.sh --pip-arg={-r,requirements.txt} /Applications/Oasys1.2.app
        Build the application using a fixed set of locked requirements.
'
}

DIR=$(dirname "$0")

# Python version in the bundled framework
PYTHON_VERSION=3.8.10

# Pip arguments used to populate the python environment in the application
# bundle
PIP_REQ_ARGS=( )

while [[ "${1:0:1}" == "-" ]]; do
    case "${1}" in
        --python-version=*)
            PYTHON_VERSION=${1#*=}
            shift 1;;
        --python-version)
            PYTHON_VERSION=${2:?"--python-version requires an argument"}
            shift 2;;
        --pip-arg=*)
            PIP_REQ_ARGS+=( "${1#*=}" )
            shift 1;;
        --pip-arg)
            PIP_REQ_ARGS+=( "${2:?"--pip-arg requires an argument"}" )
            shift 2;;
        --help|-h)
            usage; exit 0;;
        -*)
            echo "Invalid argument ${1}" >&2; usage >&2; exit 1;;
    esac
done

APPDIR=${1:?"Target APPDIR argument is missing"}

PYVER=${PYTHON_VERSION%.*}  # Major.Minor

if [[ ${#PIP_REQ_ARGS[@]} -eq 0 ]]; then
    PIP_REQ_ARGS+=('numpy~=1.23.2' 'fabio==0.14.0' 'PyQt5==5.15.2' 'PyQtWebEngine~=5.15' 'xraylib~=4.1.2' 'oasys1')
fi

mkdir -p "${APPDIR}"/Contents/MacOS
mkdir -p "${APPDIR}"/Contents/Frameworks
mkdir -p "${APPDIR}"/Contents/Resources

cp -R ./lib "${APPDIR}"/Contents/Frameworks

cp -a "${DIR}"/skeleton.app/Contents/{Resources,Info.plist.in} \
    "${APPDIR}"/Contents

# Layout a 'relocatable' python framework in the app directory
"${DIR}"/python-framework.sh \
    --version "${PYTHON_VERSION}" \
    --macos 10.9 \
    --install-certifi \
    "${APPDIR}"/Contents/Frameworks

ln -fs ../Frameworks/Python.framework/Versions/${PYVER}/Resources/Python.app/Contents/MacOS/Python \
    "${APPDIR}"/Contents/MacOS/PythonApp

ln -fs ../Frameworks/Python.framework/Versions/${PYVER}/bin/python${PYVER} \
    "${APPDIR}"/Contents/MacOS/python

"${APPDIR}"/Contents/MacOS/python -m ensurepip
"${APPDIR}"/Contents/MacOS/python -m pip install pip~=22.2.0 wheel


cat <<'EOF' > "${APPDIR}"/Contents/MacOS/ENV

# Create an environment for running python from the bundle
# Should be run as "source ENV"

BUNDLE_DIR=`dirname "$0"`/../
BUNDLE_DIR=`perl -MCwd=realpath -e 'print realpath($ARGV[0])' "$BUNDLE_DIR"`/
FRAMEWORKS_DIR="$BUNDLE_DIR"Frameworks/
RESOURCES_DIR="$BUNDLE_DIR"Resources/

PYVERSION="3.8"
PYTHONEXECUTABLE="$FRAMEWORKS_DIR"Python.framework/Resources/Python.app/Contents/MacOS/Python
PYTHONHOME="$FRAMEWORKS_DIR"Python.framework/Versions/"$PYVERSION"/
DYLD_FRAMEWORK_PATH="$FRAMEWORKS_DIR"${DYLD_FRAMEWORK_PATH:+:$DYLD_FRAMEWORK_PATH}

export PYTHONNOUSERSITE=1

# Some non framework libraries are put in $FRAMEWORKS_DIR by machlib standalone
base_ver=11.0
ver=$(sw_vers | grep ProductVersion | cut -d':' -f2 | tr -d ' ')
if [ $(echo -e $base_ver"\n"$ver | sort -V | tail -1) == "$base_ver" ]
then
   export DYLD_LIBRARY_PATH="$FRAMEWORKS_DIR"${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}lib/os10
else
   export DYLD_LIBRARY_PATH="$FRAMEWORKS_DIR"${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}lib/os11
fi
EOF

cat <<'EOF' > "${APPDIR}"/Contents/MacOS/Oasys1
#!/bin/bash

DIR=$(dirname "$0")
source "$DIR"/ENV

# LaunchServices passes the Carbon process identifier to the application with
# -psn parameter - we do not want it
if [[ "${1}" == -psn_* ]]; then
    shift 1
fi

# Disable user site packages
export PYTHONNOUSERSITE=1

exec "${DIR}"/PythonApp -m oasys.canvas --force-discovery "$@"
EOF
chmod +x "${APPDIR}"/Contents/MacOS/Oasys1

cat <<'EOF' > "${APPDIR}"/Contents/MacOS/pip
#!/bin/bash

DIR=$(dirname "$0")

# Disable user site packages
export PYTHONNOUSERSITE=1

exec -a "$0" "${DIR}"/python -m pip "$@"
EOF
chmod +x "${APPDIR}"/Contents/MacOS/pip

PYTHON="${APPDIR}"/Contents/MacOS/python

"${PYTHON}" -m pip install --no-warn-script-location "${PIP_REQ_ARGS[@]}"

VERSION=$("${PYTHON}" -m pip show oasys1 | grep -E '^Version:' |
          cut -d " " -f 2)

m4 -D__VERSION__="${VERSION:?}" "${APPDIR}"/Contents/Info.plist.in \
    > "${APPDIR}"/Contents/Info.plist
rm "${APPDIR}"/Contents/Info.plist.in

# Sanity check
(
    # run from an empty dir to avoid importing/finding any packages on ./
    tempdir=$(mktemp -d)
    cleanup() { rm -r "${tempdir}"; }
    trap cleanup EXIT
    cd "${tempdir}"
    "${PYTHON}" -m pip install --no-cache-dir --no-index oasys1 PyQt5==5.15.2
    "${PYTHON}" -m oasys.canvas --help > /dev/null
)
