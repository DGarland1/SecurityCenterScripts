"""-------------------------------------------------------------------------------
 Purpose:     Retrieves Accept Risk Rule information from SecurityCenter

 Author:      DGarland
-------------------------------------------------------------------------------

Requirements:
    dicttoxml and pysecuritycenter Python modules needs to be downloaded and installed

    a 'pyTenableConfig.py' file needs to be created and protected so that only the
    LocalSystem, service account, and/or domain admins can access it as this file
    will contain a username and password (in plaintext) to log into SecurityCenter
    The 'pyTenableConfig.py' file has to contain the following variables:
        hostip          - host IP of SecurityCenter
        username        - username to log into SecurityCenter
        password        - password to log into SecurityCenter
        fldrloc         - folder location to store results

    'pyLogging.py' file is a set of reusable code so that the scripts
    can write to both console (when this script is ran from console) as well
    as to a defined log file.

    'pyCommon.py' file is a set of reusable code for various purposes.  Most of my
    scripts make use of the functions in this Python script.
"""

# Import python modules
import sys
import os
import getpass
from configparser import ConfigParser

# adds higher directory to python module path to import
# custom modules one directory up
sys.path.append(".")

# Import reusable code dealing with setting up logging
from pyLogging import clsLogging
from pyCommon import converttime, writexml

#--- Prevent the creation of compiled import modules ---
sys.dont_write_bytecode = True

# --- Get location and name of script and store as variables ---
scriptloc = os.path.join(os.path.dirname(os.path.realpath(__file__)), '')
# What to save all files as (leave out file extension)
scriptname = os.path.splitext(os.path.basename(__file__))[0]

#--- Begin Logging Configuration Section ---
# Initialize logging
loginstance = clsLogging(scriptloc, scriptname)
logger = loginstance.setup()

logger.info('Running on Python version {}'.format(sys.version))

# --- Main function, runs automatically ---


def main():
    configfile = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), '..', 'config.conf')
    config = ConfigParser()

    if not os.path.exists(configfile):
        # Well there wasn't a config file located in the parent directory
        # so we should create a new one.
        config.add_section('SecurityCenter')
        config.set('SecurityCenter', 'host', input(
            'SecurityCenter IP Address : '))
        config.set('SecurityCenter', 'user', input(
            'SecurityCenter Username : '))
        config.set('SecurityCenter', 'pass', getpass.getpass(
            'SecurityCenter Password : '))
        config.set('SecurityCenter', 'path', os.path.join(input(
            'Folder to place reports : '), ''))

        with open(configfile, 'w') as fobj:
            config.write(fobj)
    else:
        config.read(configfile)

    hostip = config.get('SecurityCenter', 'host')
    username = config.get('SecurityCenter', 'user')
    password = config.get('SecurityCenter', 'pass')
    fldrloc = config.get('SecurityCenter', 'path')

    data = getRuleData(hostip, username, password)

    # What the element header for each set of data should be called
    elementname = 'AcceptRiskRules'

    # Write parse data (stored as dictionary objects in a list variable) to XML
    try:
        writexml(fldrloc, scriptname, data, elementname, logger)
    except Exception:
        logger.error('Error in writexml function', exc_info=True)
        closeexit(1)

    # Close log file and exit script cleanly
    closeexit(0)


def getRuleData(hostip, username, password):
    '''Collect and parse the Accept Risk Rules from SecurityCenter and returns it at as a list of dictionaries

    Parameters
    ----------
    hostip : str
        IP address of SecurityCenter
    username : str
        Username with at least full read privileges in SecurityCenter
    password : str
        Password of user with at least full read privileges in SecurityCenter

    Returns
    -------
    list: A list containing a series of parsed Accept Risk Rule dictionaries

    References and Footnotes
    ------------------------

    Refer to the following sites for more information on how to build the query
    pySecurityCenter Python Module

    [1]https://github.com/SteveMcGrath/pySecurityCenter

    [2]https://github.com/SteveMcGrath/pySecurityCenter/tree/master/examples/sc5

    SecurityCenter 5 API

    [3]https://support.tenable.com/support-center/cerberus-support-center/includes/widgets/sc_api/index.html

    Tenable Community Forum for pySecurityCenter module

    [4]https://community.tenable.com/search.jspa?q=pysecuritycenter

    '''

    try:
        # Import SecurityCenter5 class from securitycenter module
        from securitycenter import SecurityCenter5
    except Exception:
        # Log error and exit script
        logger.error('Failed to import SecurityCenter module')
        logger.error('Likely cause is that the securitycenter module has not been downloaded and installed. See https://pypi.python.org/pypi/pySecurityCenter', exc_info=True)
        closeexit(1)

    #--- Connect to SecurityCenter ---
    try:
        # Create connection to SecurityCenter server using variables stored in pyTenableConfig.py
        # Results are returned as a series of dictionary objects within the 'sc' list variable
        sc = SecurityCenter5(hostip)
        sc.login(username, password)
    except Exception:
        # Log error and exit script
        logger.error('Failed to connect to SecurityCenter server')
        logger.error(
            'Likely cause is that the credentials to login into SecurityCenter are incorrect', exc_info=True)
        closeexit(1)

    #--- Retrieve data from SecurityCenter and export to XML ---

    try:
        # Get data from SecurityCenter
        logger.info('Getting Accept Risk Rules from SecurityCenter')
        #
        # Getting all the Accepted Risk Rules from SecurityCenter
        # so there is no need to modify the 'resp' and 'rules' lines below
        #
        resp = sc.get('acceptRiskRule', params={
            'fields': 'plugin,hostValue,hostType,port,protocol,repository,user,comments,plugin,expires,createdTime,modifiedTime,status,organization'})
        rules = resp.json()['response']
        # Each entry of data is returned as a dictionary variable stored in list 'rules'
    except Exception:
        # Problem with trying to get data from SecurityCenter
        # Log error and exit script
        logger.error('Failed to get data from SecurityCenter')
        logger.error('Likely cause is the query is malformed', exc_info=True)
        closeexit(1)

    try:
        if rules is not None:  # If rules variable doesn't come back null/empty
            return parserules(sc, rules)
        else:
            logger.info('No Accept Risk Rules found')
            closeexit(0)
    except Exception as e:
        logger.error('Error parsing Accept Risk Rules in getRuleData function')
        logger.error('Data string follows')
        logger.error(e, exc_info=True)
        closeexit(1)


def parserules(sc, rules):
    """Parse out the collected Accept Risk Rules
    Parameters
    ----------
    sc : obj
        SecurityCenter connection

    rules : list
        Collection of accept risk rule dictionaries from the SC anlysis

    Returns
    -------
    list: A list containing a series of parsed Accept Risk Rule dictionaries
    """

    # Create a new list for the all accepted risk rules
    rulelist = []
    # Create a new dictionary for the individual accepted risk rule
    ruledict = {}

    # loop through each rule found
    for rule in rules:
        writeval = False

        # Get when the rule expires
        # '-1' for never
        # otherwise, time is in Epoch and needs to be converted to standard date format
        if rule['expires'] == '-1':
            expires = 'Never'
        else:
            expires = converttime(rule['expires'])

        # Determine if the rule is active or inactive
        if rule['status'] == '0':
            status = 'Active'
        else:
            status = 'Inactive'

        # Get comments from accepted risk rules
        comments = rule['comments']

        # Determine if there is a specific port defined in rule
        if rule['port'] == 'any' or rule['port'] == '0':
            portFilter = 0
        else:
            portFilter = 1

        # Get the Plugin Severity
        plugSeverity = getSeverity(sc, rule['plugin']['id'])

        # Rule Target is 'IP'
        if rule['hostType'] == 'ip':
            targetIP = rule['hostValue']
            if portFilter == 1:
                vulndetails = sc.analysis(('acceptRiskStatus', '=', "accepted"), ('pluginID', '=', rule['plugin']['id']), (
                    'port', '=', rule['port']), ('ip', '=', targetIP), tool='sumip')
            else:
                vulndetails = sc.analysis(('acceptRiskStatus', '=', "accepted"), (
                    'pluginID', '=', rule['plugin']['id']), ('ip', '=', targetIP), tool='sumip')

            # Store Status of whether the rule still applies to IP
            if vulndetails is not None:
                CurrentlyApplies = 'True'
            else:
                CurrentlyApplies = 'False'

            target = targetIP
            writeval = True

        # Rule Target is 'All Hosts'
        elif rule['hostType'] == 'all':
            getall = sc.analysis(
                ('repositoryIDs', '=', rule['repository']['id']), tool='sumip')

            # If SC Analysis did not return empty, parse data
            if getall is not None:
                for devices in getall:
                    targetIP = devices['ip']
                    if portFilter == 1:
                        vulndetails = sc.analysis(('acceptRiskStatus', '=', "accepted"), (
                            'pluginID', '=', rule['plugin']['id']), ('port', '=', rule['port']), ('ip', '=', targetIP), tool='sumip')
                    else:
                        vulndetails = sc.analysis(('acceptRiskStatus', '=', "accepted"), (
                            'pluginID', '=', rule['plugin']['id']), ('ip', '=', targetIP), tool='sumip')

                    # Store Status of whether the rule still applies to IP
                    if vulndetails is not None:
                        CurrentlyApplies = 'True'
                    else:
                        CurrentlyApplies = 'False'

                    target = 'All Hosts'
                    writeval = True

        # Rule Target is an 'Asset'
        elif rule['hostType'] == 'asset':
            assetID = rule['hostValue']['id']
            assetName = rule['hostValue']['name']
            getassets = sc.analysis(
                ('assetID', '=', assetID), ('repositoryIDs', '=', rule['repository']['id']), tool='sumip')

            # If SC Analysis did not return empty, parse data
            # Accept Risk Rules are repository specific, where Assets are not
            # So an accept risk rule may exist for some repositories, but not others
            # So an empty SC Analysis is possible
            if getassets is not None:
                for devices in getassets:
                    targetIP = devices['ip']
                    if portFilter == 1:
                        vulndetails = sc.analysis(('acceptRiskStatus', '=', "accepted"), ('pluginID', '=', rule['plugin']['id']), (
                            'port', '=', rule['port']), ('assetID', '=', assetID), ('ip', '=', targetIP), tool='sumip')
                    else:
                        vulndetails = sc.analysis(('acceptRiskStatus', '=', "accepted"), (
                            'pluginID', '=', rule['plugin']['id']), ('assetID', '=', assetID), ('ip', '=', targetIP), tool='sumip')

                    # Store Status of whether the rule still applies to IP
                    if vulndetails is not None:
                        CurrentlyApplies = 'True'
                    else:
                        CurrentlyApplies = 'False'

                    target = 'Asset: ' + assetName
                    writeval = True

        if writeval:
            ruledict = writetodict(
                rule, targetIP, CurrentlyApplies, status, target, expires, plugSeverity, comments)
            rulelist.append(ruledict)  # append dictionary to list
            ruledict = {}  # clear dictionary for next run through

    return rulelist


def writetodict(wrule, ip, ruleapplies, rulestatus, ruletarget, expires, severity, comments):
    """Simple function to organize parsed rule data and return it in a dictionary format
    Parameters
    ----------
    wrule : dictionary
        Parsed rule data in dictionary format
    ip : str
        IP address of device the accept risk rule applies to
    ruleapplies : str
        Determines whether the rule currently applies to any active vulnerability
    ruletarget : str
        The accept risk rule target rule (IP, All Hosts, or Asset)
    expires : str
        Date and time the rule expires.  'Never' if it doesn't expire
    severity : str
        Severity of the plugin the accept risk rule applies to
    comments : str
        Comments from accept risk rule

    Returns
    -------
    dict : Compiled dictionary containing all the accept risk rule information for a given IP
    """

    dictvar = {}

    reponame = wrule['repository']['name']
    protocol = wrule['protocol']
    port = wrule['port']
    pluginid = wrule['plugin']['id']
    pluginname = wrule['plugin']['name']
    time = converttime(wrule['createdTime'])
    createdby = wrule['user']['username']

    try:
        # Write data to dictionary variable
        dictvar['IP'] = ip
        dictvar['RepoName'] = reponame
        dictvar['RuleApplies'] = ruleapplies
        dictvar['RuleStatus'] = rulestatus
        dictvar['RuleTarget'] = ruletarget
        dictvar['Protocol'] = protocol
        dictvar['Port'] = port
        dictvar['Expires'] = expires
        dictvar['PluginID'] = pluginid
        dictvar['Severity'] = severity
        dictvar['PluginName'] = pluginname
        dictvar['Comments'] = comments
        dictvar['CreatedTime'] = time
        dictvar['CreatedBy'] = createdby
    except Exception as e:
        logger.error('Adding data to dictionary failed')
        logger.error('Data string follows')
        logger.error(e, exc_info=True)
        closeexit(1)

    return dictvar


def getSeverity(sc, pluginID):
    """Returns the severity level of a plugin

    sc = SecurityCenter connection

    pluginID = Plugin ID number to search the severity for
    """

    resp = sc.get('plugin', params={
        'id': pluginID,
        'fields': 'riskFactor'})
    plugresp = resp.json()['response']

    return plugresp['riskFactor']


def closeexit(exit_code):
    """Function to handle exiting the script either cleanly or with an error

    exit_code - 0 for clean exit, 1 for exiting due to script error
    """

    if exit_code == 0:  # Script completed without an error
        logger.info('Script complete')
    else:  # Script had an error
        logger.info('Exiting script due to an error')

    # Cleanly close the logging files
    # Function below comes from pyLogging.py script
    loginstance.closeHandlers()
    sys.exit()


if __name__ == '__main__':
    main()
