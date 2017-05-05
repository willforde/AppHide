[![Codacy Badge](https://api.codacy.com/project/badge/Grade/cafa154108e84a64beb02a7c610169a1)](https://www.codacy.com/app/willforde/AppHide?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=willforde/AppHide&amp;utm_campaign=Badge_Grade)

# Description
Hide applications from the "Gnome Shell" Overview. This works by changeing the
state of the **NoDisplay** option within the applications "*.desktop*" file,
which will tell "Gnome Shell" not to show that application.

![Alt text](https://raw.githubusercontent.com/willforde/AppHide/master/screenshot-adwaita.png "Screenshot")

-------------

# Dependencies
* PyXDG       => Python library to access freedesktop.org standards     => https://freedesktop.org/wiki/Software/pyxdg/
* PyGObject   => Development files for the pygobject bindings           => https://wiki.gnome.org/action/show/Projects/PyGObject

#### Using PIP
```
sudo pip install pyxdg PyGObject
```

#### Ubuntu
```
sudo apt-get install python3-xdg python3-gi
```

#### ArchLinux
```
sudo pacman -Sy python-xdg pygobject-devel
```

# Install
First clone this repo and change into AppHide directory
```
git clone https://github.com/willforde/AppHide.git
cd AppHide
```
Install required Dependencies if not already installed
```
sudo pip install -r requirements.txt
```
Build the install scripts and install
```
./autogen.sh --prefix=/usr/local
sudo make install
```
Running "*make install*", installs the application in */usr/local/bin*
and installs the "*apphide.desktop*" file in */usr/local/share/applications*

You can now run this application by typing **Apphide** in the Overview.
Or by typing **apphide** on the command line.

----------------
To uninstall, type:
```
sudo make uninstall
```
