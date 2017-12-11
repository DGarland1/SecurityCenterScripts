# Accept Risk Rules script
*Important: See Requirements and Setup Instructions below before trying to run this script*

This script exports the Accept Risk Rules out of SecurityCenter 5 into an XML format (which you can easily open in Excel if need be).

In addition to exporting the rules, it does a little extra.

- Since Accept Risk Rules can be applied to IP, Asset, or All Hosts the script will identify all IPs in the Asset and All Hosts of a repository and add the IPs to the export.  This way you can directly identify the IPs that are getting these rules applied without having to go cross reference the Asset or IP ranges of a repository.
- One thing that I found to be such a headache was determining if an Accept Risk Rule still applied.  Over time, patches and system changes on remote systems will sooner or later remove the vulnerabilities that Nessus identifies.  So eventually, the Accept Risk Rule that you put in no longer applies.  This is such a pain to determine manually and even a bigger pain when you have to explain to an auditor every Accept Risk Rule you have in effect.

The XML export will provide the following fields:
- **IP** - IP of the host device the rule applies to.
- **RuleApplies** - This tells you whether the rule currently applies or not.  Helpful to determine if you still need the rule anymore.
- **RuleStatus** - Tells you if the rule is still active or not.  Normally this status is determined on the Expiration Date of the rule, but I placed this here in case Tenable is nice enough to add a way to turn rules on and off in the future.
- **RuleTarget** - The Rule Target is either IP, Asset, or All Hosts.  This is here to help you find the rule easier in SecurityCenter if you need to change or remove it.
- **Protocol** - Tells you the ip protocol the rule applies to.  Typically TCP or UDP.
- **Port** - Port number the rule applies to.
- **Expires** - Expiration date of the rule.  If there is no expiration date, it'll be set to Never.
- **PluginID** - Plugin ID that the rule applies to.
- **PluginName** - Name of the plugin ID.
- **Comments** - Here are the comments entered when the Accept Risk Rule was created.
- **CreatedTime** - Time the rule was created.
- **CreatedBy** - SecurityCenter user who created the rule.

Sorry, I haven't been able to figure out a way to get the plugin severity to show as I've only been able to get it to show for active vulnerabilities.  Since this script pulls rules for vulnerabilities that no longer apply it is unable to determine the plugin severity.  I might figure out a way to get this information in the future.

## Requirements
Tenable SecurityCenter 5
Python 3 (script was designed using Python 3.6)

Aside from the standard library of modules that come with Python 3 you will need to install the following modules:
- [pySecurityCenter](https://github.com/SteveMcGrath/pySecurityCenter)
- [dicttoxml](https://github.com/quandyfactory/dicttoxml)

Hopefully I'm not forgetting anything.  Let me know if I am.

If your system running Python has access to the internet, you can install the modules using the commands:
'''
pip install pysecuritycenter
pip install dicttoxml
'''

If you need to install manually, I would recommend you go to the pySecurityCenter and dicttoxml GitHub sites directly and follow their instructions for a manual installation of those modules.

## Included files in this package
- AcceptRiskRules.py
- pyCommon.py
- pyLogging.py
- pyTenableConfig.py

## Setup Instructions
