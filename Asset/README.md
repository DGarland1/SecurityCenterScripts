# Get Assets script
*Important: See Requirements and Setup Instructions below before trying to run this script*

This script exports the a list of asset groups and the IPs in those groups out of SecurityCenter 5 into a CSV or XML format (which you can easily open in Excel if need be).

It is a basic script but helpful in identifying what IPs appear in an asset group.  This comes in really handy if you wish to identify what asset groups contain a particular IP or subnet of IPs.

The XML and CSV export will provide the following fields:
- **ip** - IP of the device in the asset.
- **assetName** - Name of the asset the IP is assigned to.
- **assetDesc** - Description of the asset.

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
        \---Asset
                GetAssets.py

Hopefully I'm not forgetting anything.  Let me know if I am.

If your system running Python has access to the internet, you can install the modules using the commands:
```
pip install pysecuritycenter
pip install dicttoxml
```

If you need to install manually, I would recommend you go to the pySecurityCenter and dicttoxml GitHub sites directly and follow their instructions for a manual installation of those modules.  Both modules above have additional module dependencies that you'll need to install manually as well.

## Files needed
You'll need to download all these files:
- GetAssets.py
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
Just run 'GetAssets.py' from your favorite Python IDE.

Or you can run it from command line.  If you use the command line, you must run python from the parent directory.

    python Asset/GetAssets.py

There are also some optional arguments you can use as well:

    --help | -h
        Display a short help of example commands

    --csv | -c
        OPTIONAL. By default, the script exports the results as an XML file.  Setting this option tells the script to export the results as a CSV file instead.

    --filename | -f <filename>
        OPTIONAL. Name of the file to save the results to.  Do not include the extension of the filename as the file will
        always be an XML file.

If you have a fairly large SecurityCenter deployment, this script can take several minutes to complete.  So be patient.
