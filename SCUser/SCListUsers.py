"""-------------------------------------------------------------------------------
 Purpose:     Retrieves a list of users from SecurityCenter

 Author:      DGarland
-------------------------------------------------------------------------------

Requirements:
    dicttoxml and pysecuritycenter Python modules needs to be downloaded and installed

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
import getopt
from configparser import ConfigParser

# adds higher directory to python module path to import
# custom modules one directory up
sys.path.append(".")

# Import reusable code dealing with setting up logging
from pyLogging import clsLogging
from pyCommon import writexml, writecsv

#--- Prevent the creation of compiled import modules ---
sys.dont_write_bytecode = True

# --- Get location and name of script and store as variables ---
scriptloc = os.path.join(os.path.dirname(os.path.realpath(__file__)), '')
# What to save all files as (leave out file extension)
scriptname = os.path.splitext(os.path.basename(__file__))[0]

filename = ''  # Initialize filename variable to empty
optcsv = False

# Get options passed via commandline
try:
    opts, args = getopt.getopt(sys.argv[1:], 'hcf:', [
                               'help', 'csv', 'filename='])
except getopt.GetoptError as err:
    print('Example: SCUser/ListUsers.py --csv')
    print('Example: SCUser/ListUsers.py -f "SCUsers"')
    sys.exit(1)
for opt, arg in opts:
    if opt in ('-f', '--filename'):
        filename = str(arg)
    if opt in ('-h', '--help'):
        print('Example: SCUser/ListUsers.py --csv')
        print('Example: SCUser/ListUsers.py -f "SCUsers"')
        sys.exit(0)
    if opt in ('-c', '--csv'):
        optcsv = True

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

    data = getUserData(hostip, username, password)

    # What the element header for each set of data should be called
    elementname = 'Users'

    # Write parse data (stored as dictionary objects in a list variable) to XML
    try:
        if optcsv:
            writecsv(fldrloc, scriptname, data, logger)
        else:
            writexml(fldrloc, scriptname, data, elementname, logger)
    except Exception:
        logger.error('Error in writing the file', exc_info=True)
        closeexit(1)

    # Close log file and exit script cleanly
    closeexit(0)


def getUserData(hostip, username, password):
    '''Collect and parse the list of users from SecurityCenter and returns it at as a list of dictionaries

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
    list: A list containing a series of user dictionaries

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
        logger.info('Getting list of users from SecurityCenter')
        #
        # Getting all the Accepted Risk Rules from SecurityCenter
        # so there is no need to modify the 'resp' and 'rules' lines below
        #
        resp = sc.get('user', params={
            'fields': 'id,username,firstname,lastname,status,role,group'
        })
        users = resp.json()['response']
        # Each entry of data is returned as a dictionary variable stored in list 'rules'
    except Exception:
        # Problem with trying to get data from SecurityCenter
        # Log error and exit script
        logger.error('Failed to get data from SecurityCenter')
        logger.error('Likely cause is the query is malformed', exc_info=True)
        closeexit(1)

    try:
        if users is not None:  # If rules variable doesn't come back null/empty
            return parseusers(sc, users)
        else:
            logger.info('No list of users found')
            closeexit(0)
    except Exception as e:
        logger.error('Error parsing list of users in getUserData function')
        logger.error('Data string follows')
        logger.error(e, exc_info=True)
        closeexit(1)


def parseusers(sc, users):
    """Parse out the collected list of users
    Parameters
    ----------
    sc : obj
        SecurityCenter connection

    rules : list
        Collection of user dictionaries from the SC anlysis

    Returns
    -------
    list: A list containing a series of parsed user dictionaries
    """

    # Create a new list for the all users
    userlist = []
    # Create a new dictionary for the individual user data
    userdict = {}

    # loop through each user found
    for user in users:

        userid = user['id']
        username = user['username']
        firstname = user['firstname']
        lastname = user['lastname']
        role = user['role']['name']
        group = user['group']['name']

        userdict = writetodict(
            userid, username, firstname, lastname, role, group)
        userlist.append(userdict)  # append dictionary to list
        userdict = {}  # clear dictionary for next run through

    return userlist


def writetodict(userid, username, firstname, lastname, role, group):
    """Simple function to organize parsed rule data and return it in a dictionary format
    Parameters
    ----------
    userid : int
        User ID
    username : str
        Username of the SecurityCenter user
    firstname : str
        First name of the SecurityCenter user
    lastname : str
        Last name of the SecurityCenter user
    role : str
        Role the user is assigned to
    group : str
        Group the user is assigned to

    Returns
    -------
    dict : Compiled dictionary containing the user information
    """
    dictvar = {}

    try:
        # Write data to dictionary variable
        dictvar['userID'] = userid
        dictvar['username'] = username
        dictvar['firstname'] = firstname
        dictvar['lastname'] = lastname
        dictvar['role'] = role
        dictvar['group'] = group
    except Exception as e:
        logger.error('Adding data to dictionary failed')
        logger.error('Data string follows')
        logger.error(e, exc_info=True)
        closeexit(1)

    return dictvar


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
