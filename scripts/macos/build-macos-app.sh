#!/usr/bin/env bash

set -e

usage() {
    echo 'usage: build-macos-app.sh [--python-version VER] [--pip-arg ARG] APPPATH
Create (build) an macOS application bundle

Options:
    --python-version VERSION
        Python version to install in the application bundle (default: 3.7.3)

    --pip-arg  ARG
        Pip install arguments to populate the python environemnt in the
        application bundle. Can be used multiple times.
        If not supplied then by default the latest PyPi published Orange3 and
        requirements as recorded in scripts/macos/requirements.txt are
        installed.

    -h|--help
        Print this help

Examples
    build-macos-app.sh ~/Applications/Oasys1.2.app
        Build the application using the latest published version on pypi

    build-macos-app.sh --pip-arg={Orange3==3.3.12,PyQt5} ~/Applications/Oasys1.2.app
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
PYTHON_VERSION=3.7.3

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
    PIP_REQ_ARGS+=( Oasys1 -r "${DIR}"/requirements.txt )
fi

mkdir -p "${APPDIR}"/Contents/MacOS
mkdir -p "${APPDIR}"/Contents/Frameworks
mkdir -p "${APPDIR}"/Contents/Resources

cp -a "${DIR}"/skeleton.app/Contents/{Resources,Info.plist.in} \
    "${APPDIR}"/Contents

cp -R "${DIR}"/skeleton.app/Contents/Frameworks/lib \
"${APPDIR}"/Contents/Frameworks

cp -f "${DIR}"/skeleton.app/Contents/MacOS/ENV \
"${APPDIR}"/Contents/MacOS


# Layout a 'relocatable' python framework in the app directory
"${DIR}"/python-framework.sh \
    --version "${PYTHON_VERSION}" \
    "${APPDIR}"/Contents/Frameworks

ln -fs ../Frameworks/Python.framework/Versions/${PYVER}/Resources/Python.app/Contents/MacOS/Python \
    "${APPDIR}"/Contents/MacOS/PythonApp

ln -fs ../Frameworks/Python.framework/Versions/${PYVER}/bin/python${PYVER} \
    "${APPDIR}"/Contents/MacOS/python

"${APPDIR}"/Contents/MacOS/python -m ensurepip
"${APPDIR}"/Contents/MacOS/python -m pip install pip~=19.1.1 wheel

# Python 3.6 on macOS no longer links the obsolete system libssl.
# Instead it builds/ships a it's own which expects a cert.pem in hardcoded
# /Library/Python.framework/3.6/etc/openssl/ path (but does no actually ship
# the file in the framework installer). Instead a user is prompted during
# .pkg install to run a script that pip install's certifi and links its
# cacert.pem to the etc/openssl dir. We do the same but must also patch
# ssl.py to load the cert store from a python prefix relative path (this is
# done by python-framework.sh script). Another option would be to export system
# certificates at runtime using the 'security' command line tool.
"${APPDIR}"/Contents/MacOS/python -m pip install certifi
# link the certifi supplied cert store to ${prefix}/etc/openssl/cert.pem
ln -fs ../../lib/python${PYVER}/site-packages/certifi/cacert.pem \
    "${APPDIR}"/Contents/Frameworks/Python.framework/Versions/${PYVER}/etc/openssl/cert.pem
# sanity check
test -r "${APPDIR}"/Contents/Frameworks/Python.framework/Versions/${PYVER}/etc/openssl/cert.pem

cp -f "${DIR}"/skeleton.app/Contents/Frameworks/xraylib/*.* \
"${APPDIR}"/Contents/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages

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

exec "${DIR}"/PythonApp -m oasys.canvas "$@"
EOF
chmod +x "${APPDIR}"/Contents/MacOS/Oasys1

cat <<'EOF' > "${APPDIR}"/Contents/MacOS/pip
#!/bin/bash

DIR=$(dirname "$0")
source "$DIR"/ENV

# Disable user site packages
export PYTHONNOUSERSITE=1

exec -a "$0" "${DIR}"/python -m pip "$@"
EOF
chmod +x "${APPDIR}"/Contents/MacOS/pip

PYTHON="${APPDIR}"/Contents/MacOS/python

"${PYTHON}" -m pip install "${PIP_REQ_ARGS[@]}"

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
    "${PYTHON}" -m pip install --no-cache-dir --no-index oasys1
    "${PYTHON}" -m oasys.canvas --help > /dev/null
)
