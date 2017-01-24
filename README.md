[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5f439fccd6194bf485db4c3dab1797cd)](https://www.codacy.com/app/willforde/AppHide?utm_source=github.com&utm_medium=referral&utm_content=willforde/AppHide&utm_campaign=badger)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=SLQMJBWX7G2PU)

# Description
Hide applications from the "Gnome Shell" Overview. This works by making a copy of the "*.desktop*" file from the System Application folder and placing it into the users Local Applications folder. The "*.desktop*" file will be modified with the "**NoDisplay**" option set to "true", which will tell "Gnome Shell" not to show that application.

![Alt text](/screenshot-adwaita.png "Screenshot")

-------------

# Dependencies
* PyXDG       => Python library to access freedesktop.org standards     => https://freedesktop.org/wiki/Software/pyxdg/
* PyGObject   => Development files for the pygobject bindings           => https://wiki.gnome.org/action/show/Projects/PyGObject

#### Ubuntu - packages
* python3-gi
* python3-xdg

#### ArchLinux - packages
* python-xdg
* pygobject-devel

# Build
To build and install this program run:
```
git clone https://github.com/willforde/AppHide.git
cd AppHide
./autogen.sh --prefix=/usr/local
sudo make install
```
Running "*make install*", installs the application in */usr/local/bin*
and installs the "*apphide.desktop*" file in */usr/local/share/applications*

You can now run this application by typing "*Apphide*" in the Overview.

----------------
To uninstall, type:
```
sudo make uninstall
```
----------------
To create a "tarball", type:
```
make distcheck
```
This will create a "*apphide-0.1.tar.xz*" file


----------------
## Todo:
* Select or create a suitable "icon"

----------------
## Version
0.1

----------------
## Licence
GPLv2
