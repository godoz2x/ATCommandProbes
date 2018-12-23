#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This Python script takes input a filtered trace file in JSON format, and produces an output CSV file that has
all the desired filtered field specified in get_desired_fields function. It checks for the
desired fields in the packets payload and start writing them into the file.

How to Run:
    python extract_fields.py -f filtered_traces.json -o filter_fields.csv
"""

from argparse import ArgumentParser, RawTextHelpFormatter
from xml.etree import ElementTree as ET
from json import load
from csv import DictWriter


def get_desired_fields():

    """
    List of desired fields that we want to see in the CSV file. This method is
    used by CSV writer to produce a header for the output file. If you want to
    add some other field, just add its name in the list, and provide appropriate
    functions and call them from parse_XML function.
    :return: list of desired fields
    """
    return ['PDN', 'Primary_DNS', 'Secondary_DNS', 'Timestamp']


def get_parser():
    """
    Returns parser to parse provided command line arguments.
    :return parser: ArgumentParser
    """

    parser = ArgumentParser(description='Fields Extractor from mi2logs', formatter_class=RawTextHelpFormatter)
    parser.add_argument('-f', '--file', required=True, help='Path of the input file')
    parser.add_argument('-o', '--output', required=True, help='Path of the output CSV with extension')
    return parser


def extract_PDN(protocol):

    """
    Given a protocol, extract_PDN extracts the PDN IP address from the fields.
    :param protocol:
    :return: PDN IP
    """
    pdn = protocol.find("field/field[@name='nas_eps.esm.pdn_ipv4']")
    return pdn.attrib['show']


def extract_primary_DNS(protocol):

    """
    Given a protocol, extract_primary_DNS extracts the Primary DNS IP address from the fields.
    :param protocol:
    :return: Primary DNS IP
    """
    primary_dns = protocol.find("*//*[@name='ipcp.opt.pri_dns_address']")
    return primary_dns.attrib['show']


def extract_secondary_DNS(protocol):

    """
        Given a protocol, extract_secondary_DNS extracts the Secondary DNS IP address from the fields.
        :param protocol:
        :return: Secondary DNS IP
        """
    secondary_dns = protocol.find("*//*[@name='ipcp.opt.sec_dns_address']")
    return secondary_dns.attrib['show']


def parse_xml(xml_content):

    """
    Each packets has its payload in XML form, this function takes that XML as input and parses the XMl
    for its desired field. At first, it checks if the packet of NAS type. Once determined, it gets
    the protocol discriminator. Based on which it further checks for the message type and call the
    respective functions accordingly. It return a dictionary of filtered results or None otherwise.

    If we want to further extend this function for more fields, we need to find the appropriate
    protocol discriminator and message type, then we can simply call the filtering functions
    accordingly using XPath.

    :param xml_content: XMl of the current parsing packet.
    :return nas_fields: A key-value store of fields and values.
    """

    # get root element
    root = ET.fromstring(xml_content)

    # check if this is a NAS packet
    nas_packet = root.find("./pair[@key='Msg']/msg/packet/proto[@name='nas-eps']")

    if nas_packet:
        nas_fields = {}
        # find the protocol discriminator
        protocol_disc = nas_packet.find("./field[@name='gsm_a.L3_protocol_discriminator']").attrib['value']

        # If this is a session management protocol
        if protocol_disc == '2':
            # Check message type
            msg_type = nas_packet.find("./field[@name='nas_eps.nas_msg_esm_type']").attrib['value']
            # if Configuration message
            if msg_type == 'c1':
                nas_fields['Primary_DNS'] = extract_primary_DNS(nas_packet)
                nas_fields['Secondary_DNS'] = extract_secondary_DNS(nas_packet)
                nas_fields['PDN'] = extract_PDN(nas_packet)
        return nas_fields


def extract_fields(list_of_packets):

    """
    Given a list of packets with each packet in JSON format, extract_fields filters the required fields
    from packets and put the into a list of JSON with timestamp.

    :param list_of_packets: list of all the packets captured in the traces.
    :return record: once a desired packet is with filtered fields is found, it returns back the result
    and continue its execution for the next packet.
    """
    for packet in list_of_packets:
        record = parse_xml(packet['Payload'])
        if record:
            record['Timestamp'] = packet['Timestamp']
            yield record


def load_packets(input_file_path):
    """
    Given a JSON file path in the only argument, load_packets loads the file in JSON format and returns
    a list of all the captured trace.

    :argument
        input_file_path: path of the input JSON file
    :return
        packets: list of captured packets in JSON form
    """
    with open(input_file_path) as file_obj:
        packets = load(file_obj)
    return packets


def main():
    """
    Runs the main routine of the script
    """
    parser = get_parser().parse_args()
    packets = load_packets(parser.file)

    # Open CSV and start writing results as calculated
    with open(parser.output, 'w', newline='') as csv:
        # DicWriter to write results as per the parsing function above
        writer = DictWriter(csv, fieldnames=get_desired_fields())
        writer.writeheader()

        # If any filtered record is received from extract_field, write into file.
        for record in extract_fields(packets):
            writer.writerow(record)


if __name__ == '__main__':
    main()
