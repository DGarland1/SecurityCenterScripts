#-------------------------------------------------------------------------------
# Purpose:     Retrieves Accept Risk Rule information from SecurityCenter
#
# Author:      DGarland
#-------------------------------------------------------------------------------

# Requirements:
#    dicttoxml and pysecuritycenter Python modules needs to be downloaded and installed
#
#    a 'pyTenableConfig.py' file needs to be created and protected so that only the
#    LocalSystem, service account, and/or domain admins can access it as this file
#    will contain a username and password (in plaintext) to log into SecurityCenter
#    The 'pyTenableConfig.py' file has to contain the following variables:
#        hostip          - host IP of SecurityCenter
#        username        - username to log into SecurityCenter
#        password        - password to log into SecurityCenter
#        fldrloc         - folder location to store results
#
#    'pyEmail.py' file is used to send out email alerts for failed scripts.
#    Edit the variables 'host', 'port', 'sender', and 'recipient' variables in
#    the 'pyEmail.py' file for use with the SMTP email server.
#
#    'pyLogging.py' file is a set of reusable code so that the scripts
#    can write to both console (when this script is ran from console) as well
#    as to a defined log file.
#
#    variable 'scriptname' required for pyEmail.py and pyLogging.py classes
#    Must be defined in calling script as:
#       import os
#       scriptname = os.path.splitext(os.path.basename(__file__))[0]

# Import SYS module
import sys
# Import OS module
import os
# Import reusable code dealing with setting up logging
from pyLogging import clsLogging

#--- Prevent the creation of compiled import modules ---
# Used to prevent compiling pyTenableConfig.py (protected) into a
# pyc file (unprotected)
# Also ensures that this script is always using the latest module code
sys.dont_write_bytecode = True

# --- Get name of script and store as variable ---
# What to save all files as (leave out file extension)
scriptname = os.path.splitext(os.path.basename(__file__))[0]

#--- Begin Logging Configuration Section ---
# Initialize logging
loginstance = clsLogging(scriptname)
logger = loginstance.setup()

logger.info('Running on Python version {}'.format(sys.version))

# Import common functions from pyCommon
try:
    logger.info('Import common functions from pyCommon')
    from pyCommon import converttime, writedev, writexml
except Exception:
    logger.error('Unable to import common functions from pyCommon')
    logger.error(
        'Likely cause is pyCommon.py is missing or corrupt', exc_info=True)
    closeexit(1)

# --- Main function, runs automatically ---


def main():
    # What the element header for each set of data should be called
    # Example:
    #   PortsAndServices
    #
    #-----------------------------------------------------------------------
    #    MODIFY elementname TO CHANGE THE NAME OF THE HEADER ELEMENT TAG
    #    IN XML FILE
    #-----------------------------------------------------------------------
    #
    elementname = 'AcceptRiskRules'

    #--- Import variables from pyTenableConfig.py script ---
    try:
        # Try importing variables from pyTenableConfig.py script
        # hostip - IP Address of SecurityCenter
        # username - user account that has at least an Auditor role in SecurityCenter
        # password - password for user in SecurityCenter
        # fldrloc - Folder location where to store the results
        logger.info('Importing variables from pyTenableConfig.py')
        from pyTenableConfig import hostip, username, password, fldrloc
    except Exception:
        # Log error and exit script
        logger.error('Failed to import variables from pyTenableConfig.py file')
        logger.error('Possible causes are: variables are missing from pyTenableConfig.py, pyTenableConfig.py is missing or protected (see Security settings of file)', exc_info=True)
        closeexit(1)

    data = getRuleData(hostip, username, password)

    # Enable the writedev line below to help with development and
    # troubleshooting data from SecurityCenter
    #
    # Creates a JSON and XML output of the raw SecurityCenter data
    #
    # If you are developing, it is helpful to comment out the
    # data = parsedata(data) and writexml lines in order to get the JSON
    # file by itself to see what the data structure is like

    #writedev(fldrloc, scriptname, data, logger)

    # Write parse data (stored as dictionary objects in a list variable) to XML
    try:
        writexml(fldrloc, scriptname, data, elementname, logger)
        pass
    except Exception:
        logger.error('Error in writexml function', exc_info=True)
        closeexit(1)

    # Close log file and exit script cleanly
    closeexit(0)


def getRuleData(hostip, username, password):
    #--- Collect data from SecurityCenter ---
    #
    #    The following line in this section needs to be modified to gather the
    #    specific data you want from SecurityCenter
    #
    #        details = sc.analysis(('repositoryIDs','=','1'),('pluginID','=','34252'), tool='vulndetails')
    #
    #    Refer to the following sites for more information on how to build the query
    #    pySecurityCenter Python Module
    #    https://github.com/SteveMcGrath/pySecurityCenter
    #    https://github.com/SteveMcGrath/pySecurityCenter/tree/master/examples/sc5
    #
    #    SecurityCenter 5 API
    #    https://support.tenable.com/support-center/cerberus-support-center/includes/widgets/sc_api/index.html
    #
    #    Tenable Community Forum for pySecurityCenter module
    #    https://community.tenable.com/search.jspa?q=pysecuritycenter

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

    # Create a new list for the all accepted risk rules
    rulelist = []
    # Create a new dictionary for the individual accepted risk rule
    ruledict = {}

    try:
        if rules is not None:  # If details variable doesn't come back null/empty
            # loop through each rule found
            for rule in rules:
                # Get when the rule expires
                # '-1' for never
                # otherwise, time is in Epoch and needs to be converted to standard date format
                if rule['expires'] == '-1':
                    expires = 'Never'
                else:
                    expires = converttime(rule['expires'])

                if rule['status'] == '0':
                    status = 'Active'
                else:
                    status = 'Inactive'

                # Get comments from accepted risk rules
                comments = rule['comments']

                if rule['port'] == 'any' or rule['port'] == '0':
                    portFilter = 0
                else:
                    portFilter = 1

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

                    ruledict = writetodict(targetIP, CurrentlyApplies, status, targetIP, rule['protocol'], rule['port'], expires, rule[
                        'plugin']['id'], rule['plugin']['name'], comments, converttime(rule['createdTime']), rule['user']['username'])
                    rulelist.append(ruledict)  # append dictionary to list
                    ruledict = {}  # clear dictionary for next run through

                # Rule Target is 'All Hosts'
                elif rule['hostType'] == 'all':
                    getall = sc.analysis(
                        ('repositoryIDs', '=', rule['repository']['id']), tool='sumip')
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

                        ruledict = writetodict(targetIP, CurrentlyApplies, status, "All Hosts", rule['protocol'], rule['port'], expires, rule[
                            'plugin']['id'], rule['plugin']['name'], comments, converttime(rule['createdTime']), rule['user']['username'])
                        rulelist.append(ruledict)  # append dictionary to list
                        ruledict = {}  # clear dictionary for next run through

                # Rule Target is an 'Asset'
                elif rule['hostType'] == 'asset':
                    assetID = rule['hostValue']['id']
                    assetName = rule['hostValue']['name']
                    getassets = sc.analysis(
                        ('assetID', '=', assetID), tool='sumip')
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

                        ruledict = writetodict(targetIP, CurrentlyApplies, status, 'Asset: ' + assetName, rule['protocol'], rule['port'], expires, rule[
                            'plugin']['id'], rule['plugin']['name'], comments, converttime(rule['createdTime']), rule['user']['username'])
                        rulelist.append(ruledict)  # append dictionary to list
                        ruledict = {}  # clear dictionary for next run through

            return rulelist
        else:
            logger.info('No Accept Risk Rules found')
    except Exception as e:
        logger.error('Error parsing Accept Risk Rules in getRuleData function')
        logger.error('Data string follows')
        logger.error(e, exc_info=True)
        closeexit(1)


def writetodict(ip, ruleapplies, rulestatus, ruletarget, protocol, port, expires, pluginid, pluginname, comments, time, createdby):
    #
    # Simple function to organize the rule data and return it in a dictionary format
    #

    dictvar = {}

    try:
        # Write data to dictionary variable
        dictvar['IP'] = ip
        dictvar['RuleApplies'] = ruleapplies
        dictvar['RuleStatus'] = rulestatus
        dictvar['RuleTarget'] = ruletarget
        dictvar['Protocol'] = protocol
        dictvar['Port'] = port
        dictvar['Expires'] = expires
        dictvar['PluginID'] = pluginid
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


def closeexit(exit_code):
    #
    # exit_code - 0 for clean exit, 1 for exiting due to script error
    #
    # Function to handle exiting the script either cleanly or with an error
    # Function will send an email if on error

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
