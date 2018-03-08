# Recast Risk Rules script
*Important: See Requirements and Setup Instructions below before trying to run this script*

This script exports the Recast Risk Rules out of SecurityCenter 5 into an XML format (which you can easily open in Excel if need be).

In addition to exporting the rules, it does a little extra.

- Since Recast Risk Rules can be applied to IP, Asset, or All Hosts the script will identify all IPs in the Asset and All Hosts of a repository and add the IPs to the export.  This way you can directly identify the IPs that are getting these rules applied without having to go cross reference the Asset or IP ranges of a repository.
- One thing that I found to be such a headache was determining if an Recast Risk Rule still applied.  Over time, patches and system changes on remote systems will sooner or later remove the vulnerabilities that Nessus identifies.  So eventually, the Recast Risk Rule that you put in no longer applies.  This is such a pain to determine manually and even a bigger pain when you have to explain to an auditor every Recast Risk Rule you have in effect. *Note: Removing a rule doesn't make the vulnerability show back up immediately, it will show back up again after the next scan.  Go complain to Tenable to fix this.*

The XML export will provide the following fields:
- **IP** - IP of the host device the rule applies to.
- **RepoName** - Name of the repository the rule applies to.
- **RuleApplies** - This tells you whether the rule currently applies or not for a given IP.  This is handy as some vulnerabilities get cleared due to a patch or a configuration change and you may no longer need this rule.  *Note: Keep in mind that some vulnerabilities can come and go for various, so I would advise that you keep a record of any rules you remove.*
- **RuleStatus** - Tells you if the rule is still active or not.  Normally the status is determined on the Expiration Date of the rule, but I placed this here in case Tenable is nice enough to add a way to turn rules on and off in the future.
- **RuleTarget** - The Rule Target is either IP, Asset, or All Hosts.  This is here to help you find the rule easier in SecurityCenter if you need to change or remove it.
- **Protocol** - Tells you the ip protocol the rule applies to.  Typically TCP or UDP.
- **Port** - Port number the rule applies to.
- **PluginID** - Plugin ID that the rule applies to.
- **OrigSeverity** - Original Plugin Severity.
- **NewSeverity** - Recasted Plugin Severity.
- **PluginName** - Name of the plugin ID.
- **Comments** - Here are the comments entered when the Recast Risk Rule was created.
- **CreatedTime** - Time the rule was created.
- **CreatedBy** - SecurityCenter user who created the rule.

Log files for the script are stored in the same directory as the script itself.

Script results are stored in whatever directory you signify.  See Setup Instructions below.

## Requirements
- Tenable SecurityCenter 5
- Python 3 (script was designed using Python 3.6)

Aside from the standard library of modules that come with Python 3 you will need to install the following modules:
- [pySecurityCenter](https://github.com/SteveMcGrath/pySecurityCenter)
- [dicttoxml](https://github.com/quandyfactory/dicttoxml)

You'll also need the pyLogging.py and pyCommon.py files in the parent directory as well.

To run this script, your folder structure should look like this

    \---SecurityCenterScripts
        |   pyCommon.py
        |   pyLogging.py
        |
        \---RiskRecast
                RecastRiskRules.py

Hopefully I'm not forgetting anything.  Let me know if I am.

If your system running Python has access to the internet, you can install the modules using the commands:
```
pip install pysecuritycenter
pip install dicttoxml
```

If you need to install manually, I would recommend you go to the pySecurityCenter and dicttoxml GitHub sites directly and follow their instructions for a manual installation of those modules.  Both modules above have additional module dependencies that you'll need to install manually as well.

## Files needed
You'll need to download all these files:
- RecastRiskRules.py
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
Just run 'RecastRiskRules.py' from your favorite Python IDE.

Or you can run it from command line.  If you use the command line, you must run python from the parent directory.

    python RiskRecast/RecastRiskRules.py

There are also some optional arguments you can use as well:

    --help | -h
        Display a short help of example commands

    --repoID | -r <repository ID#>
        Tells the script to only return results for the selected repository ID#.  The repository ID# is assigned
        to the repository by SecurityCenter when the respository is created.

    --filename | -f <filename>
        Name of the file to save the results to.  Do not include the extension of the filename as the file will
        always be an XML file.

If you have a fairly large SecurityCenter deployment, this script can take several minutes to complete.  So be patient.