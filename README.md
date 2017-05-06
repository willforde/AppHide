[![Codacy Badge](https://api.codacy.com/project/badge/Grade/cafa154108e84a64beb02a7c610169a1)](https://www.codacy.com/app/willforde/AppHide?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=willforde/AppHide&amp;utm_campaign=Badge_Grade)
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/willforde)

# Description
Hide applications from the "Gnome Shell" Overview. This works by changing the
state of the **NoDisplay** option within the applications "*.desktop*" file,
which will tell "Gnome Shell" not to show that application.

![Screenshot of Gui](/screenshot.png "Screenshot")

-------------

## Dependencies
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

## Install
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

## Command-line arguments
#### Usage
```
apphide.py [-h] [-s id | -i id | -t id] [-l] [-y | -n] [-o]

optional arguments:
  -h, --help          show this help message and exit
  -s id, --show id    UnHide the specified application
  -i id, --hide id    Hide the specified application
  -t id, --toggle id  Toggle the Hide/Show state for specified application

  -l, --list          List available applications
  -y, --hidden        Apply filter to only show hidden applications
  -n, --not-hidden    Apply filter to only show applications that are not hidden
  -o, --no-headers    Cleaner output for easier parsing
```

#### List applications
```
$apphide -l
---------------------------------------------------------------------------------------
Hidden | Name                     | Description                                 | AppID
---------------------------------------------------------------------------------------
No     | AppHide                  | Hide applications from the gnome shell      | apphide
No     | Archive Manager          | Create and modify an archive                | org.gnome.fileroller
No     | Atom                     | A hackable text editor for the 21st Century | atom
Yes    | Avahi SSH Server Browser | Browse for Zeroconf-enabled SSH Servers     | bssh
Yes    | Avahi VNC Server Browser | Browse for Zeroconf-enabled VNC Servers     | bvnc
No     | Boxes                    | View and use virtual machines               | org.gnome.boxes
...
```

#### Hide application
```
$apphide -i org.gnome.boxes
Hiding application: Boxes

$apphide -l | grep Boxes
Yes    | Boxes                    | View and use virtual machines                | org.gnome.boxes
```