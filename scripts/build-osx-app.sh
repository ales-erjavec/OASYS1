#!/bin/bash -e
# Build an OSX Applicaiton (.app) for Orange Canvas
#
# Example:
#
#     $ build-osx-app.sh $HOME/Applications/Orange3.app
#

function print_usage() {
    echo 'build-osx-app.sh [-i] [--template] Orange3.app

Build an Orange Canvas OSX application bundle (Orange3.app).

NOTE: this script should be run from the source root directory.

Options:

    --template TEMPLATE_URL  Path or url to an application template as build
                             by "build-osx-app-template.sh. If not provided
                             a default one will be downloaded.
    -i --inplace             The provided target application path is already
                             a template into which Orange should be installed
                             (this flag cannot be combined with --template).
    -h --help                Print this help'
}

while [[ ${1:0:1} = "-" ]]; do
    case $1 in
        --template)
            TEMPLATE_URL=$2
            shift 2;
            ;;
        -i|--inplace)
            INPLACE=1
            shift 1
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        -*)
            echo "Unknown argument $1"
            print_usage
            exit 1
            ;;
    esac
done

# extended glob expansion / fail on filename expansion
shopt -s extglob failglob

if [[ ! -f setup.py ]]; then
    echo "This script must be run from the source root directory!"
    print_usage
    exit 1
fi

APP=${1:-dist/Orange3.app}

if [[ $INPLACE ]]; then
    if [[ $TEMPLATE_URL ]]; then
        echo "--inplace and --template can not be combined"
        print_usage
        exit 1
    fi

    if [[ -e $APP && ! -d $APP ]]; then
        echo "$APP exists and is not a directory"
        print_usage
        exit 1
    fi
fi

TEMPLATE_URL=${TEMPLATE_URL:-"http://orange.biolab.si/download/files/bundle-templates/Orange3.app-template.tar.gz"}

SCHEMA_REGEX='^(https?|ftp|local)://.*'

if [[ ! $INPLACE ]]; then
    BUILD_DIR=$(mktemp -d -t orange-build)

    echo "Retrieving a template from $TEMPLATE_URL"
    # check for a url schema
    if [[ $TEMPLATE_URL =~ $SCHEMA_REGEX ]]; then
        curl --fail --silent --location --max-redirs 1 "$TEMPLATE_URL" | tar -x -C "$BUILD_DIR"
        TEMPLATE=( $BUILD_DIR/*.app )

    elif [[ -d $TEMPLATE_URL ]]; then
        cp -a $TEMPLATE_URL $BUILD_DIR
        TEMPLATE=$BUILD_DIR/$(basename "$TEMPLATE_URL")

    elif [[ -e $TEMPLATE_URL ]]; then
        # Assumed to be an archive
        tar -xf "$TEMPLATE_URL" -C "$BUILD_DIR"
        TEMPLATE=( $BUILD_DIR/*.app )
    else
        echo "Invalid --template $TEMPLATE_URL"
        exit 1
    fi
else
    TEMPLATE=$APP
fi
echo "Building application in $TEMPLATE"

PYTHON=$TEMPLATE/Contents/MacOS/python
PIP=$TEMPLATE/Contents/MacOS/pip
EASY_INSTALL=$TEMPLATE/Contents/MacOS/easy_install

PREFIX=$("$PYTHON" -c'import sys; print(sys.prefix)')
SITE_PACKAGES=$("$PYTHON" -c'import sysconfig as sc; print(sc.get_path("platlib"))')

cp -f "/opt/local/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages/_xraylib.la" "$SITE_PACKAGES"
cp -f "/opt/local/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages/_xraylib.so" "$SITE_PACKAGES"
cp -f "/opt/local/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages/xrayhelp.py" "$SITE_PACKAGES"
cp -f "/opt/local/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages/xraylib.py" "$SITE_PACKAGES"
cp -f "/opt/local/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages/xraymessages.py" "$SITE_PACKAGES"

cp -r "/opt/local/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages/Shadow"  "$SITE_PACKAGES"
cp -r "/opt/local/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages/PyMca5"  "$SITE_PACKAGES"

cp -r "/opt/local/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages/pyparsing-2.0.3.dist-info" "$SITE_PACKAGES"
cp -f "/opt/local/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages/pyparsing.py" "$SITE_PACKAGES"

cp -r "/opt/local/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages/dateutil" "$SITE_PACKAGES"

cp -f "/Users/labx/Documents/workspace/OASYS-Develop/OASYS1/scripts/easy-install.pth" "$SITE_PACKAGES"

"$PIP" uninstall -y numpy
"$PIP" install numpy

"$PIP" uninstall -y scipy
UMFPACK=None "$PIP" install scipy

#"$PIP" uninstall -y six
"$PIP" install six

"$PIP" uninstall -y matplotlib
"$PIP" install matplotlib

echo "Installing bottlechest"
echo "======================"
"$PIP" install git+https://github.com/biolab/bottlechest@bottlechest#egg=bottlechest

#cp -r "/Users/labx/Documents/workspace/OASYS-Develop/Orange-Shadow/orangecontrib" "$SITE_PACKAGES"

echo "Installing pyqtgraph sqlparse"
echo "============================="

"$PIP" install pyqtgraph sqlparse

echo "Installing Orange"
echo "================="

"$PYTHON" setup.py install

cat <<-'EOF' > "$TEMPLATE"/Contents/MacOS/Orange
	#!/bin/bash

	DIRNAME=$(dirname "$0")
	source "$DIRNAME"/ENV

	# LaunchServices passes the Carbon process identifier to the application with
	# -psn parameter - we do not want it
	if [[ $1 == -psn_* ]]; then
	    shift 1
	fi

	exec -a "$0" "$DIRNAME"/PythonAppStart -m Orange.canvas "$@"
EOF

chmod +x "$TEMPLATE"/Contents/MacOS/Orange
#chmod +x "$TEMPLATE"/Contents/MacOS/orangecontrib

if [[ ! $INPLACE ]]; then
    echo "Moving the application to $APP"
    if [[ -e $APP ]]; then
        rm -rf "$APP"
    fi
	mkdir -p $(dirname "$APP")
    mv "$TEMPLATE" "$APP"
fi

rm -f "$APP"/Contents/Frameworks/libgfortran.2.0.0.dylib
cp -f /usr/local/gfortran/lib/libgfortran.3.dylib "$APP"/Contents/Frameworks/
cp -f /usr/local/gfortran/lib/libgcc_s.1.dylib "$APP"/Contents/Frameworks/

