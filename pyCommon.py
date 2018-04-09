#-------------------------------------------------------------------------------
# Name:        pyCommon
# Purpose:      Contains a list of common functions for use with SecurityCenter scripts
#
# Author:      DGarland
#-------------------------------------------------------------------------------

# Determine if IP address is IPv4, IPv6, or unknown


def ipversion(addr):
    '''Returns the IP version (version 4 or 6)
    Paramaters
    ----------
    addr : str
        IP address (version 4 or 6)

    Returns
    -------
    int : returns version of IP (4, 6, or 0 if unknown)

    '''
    import socket

    try:  # see if IP is version 4
        socket.inet_aton(addr)
        return 4
    except socket.error:
        pass
    try:  # see if IP is version 6
        socket.inet_pton(socket.AF_INET6, addr)
        return 6
    except socket.error:
        pass
    return 0  # unable to determine IP version

#
# Takes name, parses it to remove extra DNS or NetBIOS information, and
# returns it
#


def gethostname(name):
    '''Returns the hostname from a NetBIOS or FQDN
    Paramaters
    ----------
    name : str
        Computer name in NetBIOS or FQDN format

    Returns
    -------
    string : hostname of device

    '''
    if '.' in name:  # name is in DNS format
        x = name.split('.')  # split DNS name into its parts and store as list
        return x[0]  # return first item in list, which should be the hostname
    elif '\\' in name:  # name is in NetBIOS format
        # split NetBIOS name into its parts and store as list
        x = name.split('\\')
        return x[-1]  # return last item in list, which should be the hostname
    elif not name:  # name was blank, raise an error
        raise ValueError('Hostname passed to gethostname function was empty')
    else:  # name was already provided cleanly, just return it
        return name

# Converts epoch time to formatted time


def converttime(epoch):
    '''Converts Epoch time to local time
    Paramaters
    ----------
    epoch : str or int
        Time in Epoch format

    Returns
    -------
    string : Local time

    '''
    import time

    # convert to float if epoch is string or integer
    epochflt = float(epoch)
    # return time in correct format
    return time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(epochflt))

# Just a handy function to export the unformatted SecurityCenter data
# in both XML and JSON formats.


def writedev(fldrloc, filename, dictdetails, logger):
    '''Dump unparsed data from SC Analysis to an XML and JSON file for testing and troubleshooting
    Parameters
    ----------
    flrloc : str
        Folder location
    filename : str
        Filename of XML to write to
    dictdetails : list
        A list of dictionaries
    logger : obj
        Instance of logging obj

    Returns
    -------
    None

    '''

    import json
    from xml.dom.minidom import parseString

    try:
        # Import dicttoxml module (needs to be installed, not embedded into Python)
        # Provides direct conversion of dictionary objects to XML
        import dicttoxml
    except:
        # Log error and exit script
        logger.error('Failed to import dicttoxml module')
        logger.error(
            'Likely cause is that the dicttoxml module has not been downloaded and installed. See https://pypi.python.org/pypi/dicttoxml', exc_info=True)
        raise

    # Export JSON results to a JSON file in pretty format
    try:
        with open('{}{}_dev.json'.format(fldrloc, filename), 'w+', encoding='utf-8') as outfile:
            json.dump(dictdetails, outfile, sort_keys=True,
                      indent=4, ensure_ascii=False)
        outfile.close
        logger.info('Data written to JSON file at {}{}_dev.json'.format(
            fldrloc, filename))
    except:
        logger.error('Error encountered when trying to write data to JSON dev file at {}{}_dev.json'.format(
            fldrloc, filename))
        raise

    try:
        # convert JSON format (from SecurityCenter) to XML
        xml = dicttoxml.dicttoxml(dictdetails, attr_type=False)

        # parse XML in preparation for 'Pretty XML' format
        dom = parseString(xml)
        xmldomresult = dom.toprettyxml()

        # save XML in 'Pretty XML' format to text.xml file
        f1 = open('{}{}_dev.xml'.format(
            fldrloc, filename), 'w+', encoding='utf-8')
        f1.write(xmldomresult)
        f1.close()
        logger.info('Data written to XML dev file at {}{}_dev.xml'.format(
            fldrloc, filename))
    except:
        logger.error('Error encountered when trying to write data to XML dev file at {}{}_dev.json'.format(
            fldrloc, filename))
        raise

# Writes the results of the dictionary variable to XML


def writexml(fldrloc, filename, dictdetails, elementheader, logger):
    '''Write list (containing dictionaries) to an XML file
    Parameters
    ----------
    flrloc : str
        Folder location
    filename : str
        Filename of XML to write to
    dictdetails : list
        A list of dictionaries
    elementheader : str
        Name of element header for XML file
    logger : obj
        Instance of logging obj

    Returns
    -------
    None

    '''

    try:
        # Import dicttoxml module (needs to be installed, not embedded into Python)
        # Provides direct conversion of dictionary objects to XML
        import dicttoxml
    except:
        # Log error and exit script
        logger.error('Failed to import dicttoxml module')
        logger.error(
            'Likely cause is that the dicttoxml module has not been downloaded and installed. See https://pypi.python.org/pypi/dicttoxml', exc_info=True)
        raise

    try:
        logger.info('Convert parsed data to XML')

        # replace 'item' header tag name with variable 'elementheader'
        def my_item_func(x): return elementheader

        # convert parsed data to XML
        xml = dicttoxml.dicttoxml(
            dictdetails, attr_type=False, item_func=my_item_func)

        # Import parseString class from xml.dom.minidom module (embedded into Python)
        from xml.dom.minidom import parseString

        # Initialize xmldomresult variable so it won't crash the code if the results come back null/empty
        xmldomresult = ""

        # parse XML in preparation for 'Pretty XML' format
        dom = parseString(xml)
        xmldomresult = dom.toprettyxml()
    except:
        # Log error and exit script
        logger.error('Failed to convert parsed data to xml')
        raise

    # save XML in 'Pretty XML' format to 'scriptname' file
    try:
        logger.info('Saving {}{}.xml'.format(fldrloc, filename))
        f1 = open('{}{}.xml'.format(fldrloc, filename), 'w+', encoding='utf-8')
        f1.write(xmldomresult)
        f1.close()
    except:
        # Log error and exit script
        logger.error('Failed to write XML file')
        logger.error('Unable to write the XML file', exc_info=True)
        f1.close()
        raise


def writecsv(fldrloc, filename, dictdetails, logger):
    '''Write list (containing dictionaries) to an XML file
    Parameters
    ----------
    flrloc : str
        Folder location
    filename : str
        Filename of XML to write to
    dictdetails : list
        A list of dictionaries
    logger : obj
        Instance of logging obj

    Returns
    -------
    None

    '''
    # Import CSV module
    import csv

    try:
        # Open CSV file for writing
        logger.info('Saving {}{}.csv'.format(fldrloc, filename))
        csvFile = open(fldrloc + filename + '.csv', 'w', newline='')

        with csvFile:
            # Get a list of headers for the CSV from the dictdetails
            csvHeaders = list(dictdetails[0].keys())
            writer = csv.DictWriter(csvFile, fieldnames=csvHeaders)
            writer.writeheader()

            # Write data from dictdetails to CSV
            for user in dictdetails:
                writer.writerow(user)
    except:
        # Log error and exit script
        logger.error('Failed to write XML file')
        logger.error('Unable to write the XML file', exc_info=True)
    finally:
        csvFile.close()
