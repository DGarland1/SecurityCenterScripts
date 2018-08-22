# Installed Software script
*Important: See Requirements and Setup Instructions below before trying to run this script*

This script exports a list of installed software collected by SecurityCenter using Nessus pluginID 34252 (for Windows) and 25221 (for Linux/AIX).

The CSV and XML export will provide the following fields:
- **AssetName** - Hostname
- **IPAddress** - IP address
- **Protocol** - Protocol type (usually TCP or UDP)
- **PortNumber** - Port number that the process is using
- **Process** - Filename of the process using the port
- **CreatDate** - The date the results were collected
- **pluginText** - The full plugin text results from SecurityCenter

Log files for the script are stored in the same directory as the script itself.

Script results are stored in whatever directory you signify.  See Setup Instructions below.

## Requirements
- Tenable SecurityCenter 5
- Python 3 (script was designed using Python 3.6)

Aside from the standard library of modules that come with Python 3 you will need to install the following modules:
- [pySecurityCenter](https://github.com/SteveMcGrath/pySecurityCenter)
- [dicttoxml](https://github.com/quandyfactory/dicttoxml)
- [configparser](https://pypi.org/project/configparser)

You'll also need the pyLogging.py and pyCommon.py files in the parent directory as well.

To run this script, your folder structure should look like this

    \---SecurityCenterScripts
        |   pyCommon.py
        |   pyLogging.py
        |
        \---PortServ
                PortsServices.py

If your system running Python has access to the internet, you can install the modules using the commands:
```
pip install pysecuritycenter
pip install dicttoxml
pip install configparser
```

If you need to install manually, I would recommend you go to the pySecurityCenter and dicttoxml GitHub sites directly and follow their instructions for a manual installation of those modules.  Both modules above have additional module dependencies that you'll need to install manually as well.

## Files needed
You'll need to download all these files:
- PortsServices.py
- pyCommon.py
- pyLogging.py

## Setup Instructions
A config.conf file containing the IP address of your SecurityCenter server, a user account with at least full read privileges (Auditor), a password, and a folder location to export the file to.  This config.conf file will be required for all of my SecurityCenter scripts.

If you don't already have the config.conf file, running the script from a command line for the first time you'll be asked a series of questions (IP, username, password, path) and the config.conf file will be built for you automatically and stored in the parent directory.

See below for an example of the config.conf file:

    [SecurityCenter]
    host = 10.11.12.13
    user = username
    pass = password
    path = C:\scripts\

## Run Instructions
Just run 'PortsServices.py' from your favorite Python IDE.

Or you can run it from command line.  If you use the command line, you must run python from the parent directory.

    python PortServ/PortsServices.py

There are also some optional arguments you can use as well:

    --help | -h
        Display a short help of example commands

    --csv | -c
        OPTIONAL. By default, the script exports the results as an XML file.  Setting this option tells the script to export the results as a CSV file instead.

    --repoID | -r <repository ID#>
        OPTIONAL. Tells the script to only return results for the selected repository ID#.  The repository ID# is assigned
        to the repository by SecurityCenter when the respository is created.

    --filename | -f <filename>
        OPTIONAL. Name of the file to save the results to.  Do not include the extension of the filename as the file will
        always be an XML file.

    --startDay <integer>
        OPTIONAL. Default 'all'.  The number of days ago to start looking for results from SecurityCenter.  This number needs to be larger than endDay.  Both endDay and startDay are provided in the number of days ago. [e.g. '90' is between endDay and 90 days ago]

    --endDay <integer>
        OPTIONAL. Default '0'.  The number of days ago to stop looking for results from SecurityCenter.  This number needs to be smaller than startDay.  Both endDay and startDay are provided in the number of days ago. [e.g. '9' is between 9 days ago and endDay ago]

    startDay and endDay arguments are based on the lastseen value in SecurityCenter.  So for example, if a scan result was last seen a week ago but you are only looking between an endDay of 0 and and a startDay of 1 day ago (the last 24 hours) then the result will not be included in the XML file.  This is handy if you are importing the XML into another program or database to monitor for software changes.
    
    Examples for using endDay and startDay arguments:
        This example gets results from SecurityCenter from now to 1 days ago.  endDay defaults to 0 if left out.
            python PortServ/PortsServices.py --startDay 1

        This example gets results from SecurityCenter from 30 to 60 days ago.
            python PortServ/PortsServices.py --startDay 60 --endDay 30

        This example gets results from SecurityCenter from 90 days ago and beyond.  startDay defaults to 'all' if left out.
            python PortServ/PortsServices.py --endDay 90

If you have a fairly large SecurityCenter deployment, this script can take several minutes to complete.  So be patient.
