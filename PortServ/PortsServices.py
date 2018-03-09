'''-------------------------------------------------------------------------------
Purpose:     Gathers Ports and Services from SecurityCenter

Author:      DGarland
-------------------------------------------------------------------------------

Requirements:
    dicttoxml and pysecuritycenter Python modules needs to be downloaded and installed

    'pyLogging.py' file is a set of reusable code so that the scripts
    can write to both console (when this script is ran from console) as well
    as to a defined log file.

    'pyCommon.py' file is a set of reusable code for various purposes.  Most of my
    scripts make use of the functions in this Python script.
'''

# Import python modules
import sys
import os
import getpass
import getopt
from configparser import ConfigParser

# adds higher directory to python module path to import
# custom modules one directory up
sys.path.append(".")

# Import reusable code dealing with setting up logging
from pyLogging import clsLogging
from pyCommon import converttime, writexml, gethostname, ipversion

#--- Prevent the creation of compiled import modules ---
sys.dont_write_bytecode = True

# --- Get location and name of script and store as variables ---
scriptloc = os.path.join(os.path.dirname(os.path.realpath(__file__)), '')
# What to save all files as (leave out file extension)
scriptname = os.path.splitext(os.path.basename(__file__))[0]

repoID = '0'  # Set repository ID to All
filename = ''  # Initialize filename variable to empty
endDay = '0'
startDay = 'all'

# Get options passed via commandline
try:
    opts, args = getopt.getopt(sys.argv[1:], 'r:f:', [
                               'repoID=', 'filename=', 'endDay=', 'startDay='])
except getopt.GetoptError as err:
    print('Example: PortServ/PortsServices.py -r 1')
    print('Example: PortServ/PortsServices.py -r 1 -f "sitePortsServices"')
    print('Example: PortServ/PortsServices.py --startDay 90 --endDay 30')
    sys.exit(1)
for opt, arg in opts:
    if opt in ('-r', '--repoID'):
        repoID = str(arg)
        scriptname = scriptname + '-Repo' + repoID
    if opt in ('-f', '--filename'):
        filename = str(arg)
    if opt in '--endDay':
        endDay = str(arg)
    if opt in '--startDay':
        startDay = str(arg)
    if opt in ('-h', '--help'):
        print('Example: PortServ/PortsServices.py -r 1')
        print('Example: PortServ/PortsServices.py -r 1 -f "sitePortsServices"')
        print('Example: PortServ/PortsServices.py --startDay 90 --endDay 30')
        sys.exit(0)

if filename:
    scriptname = filename

#--- Begin Logging Configuration Section ---
# Initialize logging
loginstance = clsLogging(scriptloc, scriptname)
logger = loginstance.setup()

logger.info('Running on Python version {}'.format(sys.version))


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

    # What the element header for each set of data should be called
    elementname = 'PortsAndServices'

    # Begin collecting data from SecurityCenter
    data = collect(hostip, username, password)

    # Enable the writedev line below to help with development and
    # troubleshooting data from SecurityCenter
    #
    # Creates a JSON and XML output of the raw SecurityCenter data
    #
    # If you are developing, it is helpful to comment out the
    # data = parsedata(data) and writexml lines in order to get the JSON
    # file by itself to see what the data structure is like
    #writedev(fldrloc, scriptname, data, logger)

    # Parse the data retrieved from SecurityCenter
    data = parsedata(data)

    # Write parse data (stored as dictionary objects in a list variable) to XML
    try:
        writexml(fldrloc, scriptname, data, elementname, logger)
        pass
    except Exception:
        logger.error('Error in writexml function', exc_info=True)
        closeexit(1)

    # Close log file and exit script cleanly
    closeexit(0)


def collect(hostip, username, password):
    '''--- Collect data from SecurityCenter ---

       Refer to the following sites for more information on how to build the query
       pySecurityCenter Python Module
       https://github.com/SteveMcGrath/pySecurityCenter
       https://github.com/SteveMcGrath/pySecurityCenter/tree/master/examples/sc5

       SecurityCenter 5 API
       https://support.tenable.com/support-center/cerberus-support-center/includes/widgets/sc_api/index.html

       Tenable Community Forum for pySecurityCenter module
       https://community.tenable.com/search.jspa?q=pysecuritycenter
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
    # Filters must be applied in tuples and with the pysecuritycenter modules, filters are and-ed together.

    try:
        # Get data from SecurityCenter
        logger.info('Getting data from SecurityCenter')
        #
        # Edit the details line below only
        #
        # Explanations:
        #   ('repositoryIDs','=','1')  # NRG NERC Repository
        #   ('pluginID','=','34252')  # plugin to list Ports and Services from Windows
        #   ('lastSeen','=','0:1')  # Last seen in the past day
        #   tool='vulndetails' # Provides plugin detailed info.  This maps to the 'Vulnerability Detail List' dropdown option on the Analysis page in SecurityCenter
        #
        if repoID == '0':
            details = sc.analysis(
                ('pluginID', '=', '25221,34252'), ('lastSeen', '=', endDay+':'+startDay), tool='vulndetails')
        else:
            details = sc.analysis(('repositoryIDs', '=', repoID), ('pluginID',
                                                                   '=', '25221,34252'), ('lastSeen', '=', endDay+':'+startDay), tool='vulndetails')
        # Each entry of data is returned as a dictionary variable stored in list 'details'
        return details
    except Exception:
        # Problem with trying to get data from SecurityCenter
        # Log error and exit script
        logger.error('Failed to get data from SecurityCenter')
        logger.error('Likely cause is the query is malformed', exc_info=True)
        closeexit(1)


def parsedata(data):
    '''--- Parse the data collected from SecurityCenter ---
    This function is the only one that really needs to be modified to parse
    the data returned from SecurityCenter into a format to be converted and
    saved as XML.

    Data retrieved from SecurityCenter using the pySecurityCenter module is
    stored as dictionary objects (for each entry) and all dictionary objects
    are stored into a single list variable.

    For more information on dictionaries and lists see:
        http://sthurlow.com/python/lesson06/

    Since the data comes in as dictionaries stored in a single list, the parsed
    data coming out should also be as dictionaries stored in a single list.

    data structure notes, just here for reference while writing code:
      <PortsAndServices>
        <AssetName>computer1</AssetName>
        <IPAddress>10.10.10.1</IPAddress>
        <Protocol>TCP</Protocol>
        <IPVersion>4</IPVersion>
        <PortNumber>22</PortNumber>
        <Process>sshd</Process>
        <CreateDate>2017-08-30T07:00:23.420</CreateDate>
      </PortsAndServices>'''

    if data is not None:  # If details variable doesn't come back null/empty
        #--- Import additional Python modules needed ---
        # re module should already be embedded in Python 2.7
        import re

        # Create a new list
        newlist = []
        # Create a new dictionary
        newdict = {}

        logger.info('Processing data from SecurityCenter')

        # Determine the number of unique records were found
        logger.info('{} unique records found'.format(str(len(data))))

        try:
            # Loop through each 'x' dictionary variable in 'details' list variable
            # index variable provides where in list the data is from
            for x in data:

                servicename = ''

                # Get text value associated with 'pluginText' key in 'x' dictionary
                # and remove <plugin_output> headers from text
                x['pluginText'] = re.sub(
                    '(\\n)?(\\n)?<\/?plugin_output>(\\n)?', '', x['pluginText'])

                # This is a Windows box
                if x['pluginID'] == '34252':
                    # Filter out all extraneous text except for the process name (ie. svchost.exe)
                    # using the regular expressions module
                    servicename = re.findall(
                        '(?<=\')(.+)(?=\')', x['pluginText'])[0]

                # This is a linux/unix box of some kind
                if x['pluginID'] == '25221':
                    # Split multiline 'pluginText' value into individual lines and store into
                    # variable lines (list datatype)
                    lines = x['pluginText'].splitlines()

                    # Filter out all extraneous text except for the process name (ie. svchost.exe)
                    # using the regular expressions module
                    servicename = re.findall('([^/]*)$', lines[1])[0]

                dnsName = x['dnsName']
                netbiosName = x['netbiosName']
                if dnsName:  # check to see if dnsName contains any data
                    hostname = dnsName
                else:  # if not, then use NetBIOS Name
                    hostname = netbiosName

                if servicename:
                    # names in the x dictionary are case sensitive
                    try:
                        # Add data to dictionary
                        newdict['AssetName'] = gethostname(hostname)
                        newdict['IPAddress'] = x['ip']
                        newdict['Protocol'] = x['protocol']
                        newdict['IPVersion'] = ipversion(x['ip'])
                        newdict['PortNumber'] = x['port']
                        newdict['Process'] = servicename
                        newdict['CreateDate'] = converttime(x['lastSeen'])
                        newdict['pluginText'] = x['pluginText']
                    except Exception:
                        logger.error('Adding data to dictionary failed')
                        logger.error('Data string follows')
                        logger.error(x, exc_info=True)
                        closeexit(1)

                    newlist.append(newdict)  # append dictionary to list
                    newdict = {}  # clear dictionary for next run through
                else:
                    logger.warning('No formatter available for ' +
                                   hostname + '. Data for this system is not parsed nor saved to XML.')

            return newlist
        except Exception:
            logger.error('Parsing data failed', exc_info=True)
            closeexit(1)

    else:  # details variable came back null/empty
        logger.info('No information found from SecurityCenter')
        closeexit(0)


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