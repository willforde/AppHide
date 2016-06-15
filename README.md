# Description
Hide applications from the gnome shell overview window. Works by making a copy of the .desktop file from the system application folder and placing it into the users local applications folder. The .desktop file will be modified with the "NoDisplay" option set the True, witch will tell gnome not to show this application.

-------------

# Dependencies
* PyXDG       => Python library to access freedesktop.org standards     => https://freedesktop.org/wiki/Software/pyxdg/
* PyGObject   => Development files for the pygobject bindings           => https://wiki.gnome.org/action/show/Projects/PyGObject

#### Ubuntu
* python3-gi
* python3-xdg

#### ArchLinux
* python-xdg
* pygobject-devel

-------------
# Build
To build and install this program run:
```
./autogen.sh --prefix=/usr/local
sudo make install
```
Running "make install", installs the application in /usr/local/bin
and installs the apphide.desktop file in /usr/local/share/applications

You can now run the application by typing "Apphide" in the Overview.

----------------
To uninstall, type:
```
sudo make uninstall
```
----------------
To create a tarball type:
```
make distcheck
```
This will create apphide-0.1.tar.xz

----------------
# Toto:
Select or create a suitable icon

----------------
# Version
0.1

----------------
# License
GPLv2