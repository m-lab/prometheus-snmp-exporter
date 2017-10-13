#!/usr/bin/env python
"""Generate an snmp_exporter configuration file for M-Lab's Juniper switches."""

# Copyright 2017 Measurement Lab
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import logging
import string
import sys


def parse_options(args):
    """Parses the options passed to this script.

    Args:
        args: list of options passed on command line

    Returns:
        An argparse.ArgumentParser object containing the passed options and
        their values.
    """
    parser = argparse.ArgumentParser(
        description='Generates an snmp_exporter config M-Lab QFX5100 switches.')
    parser.add_argument('--output_file',
                        dest='output_file',
                        default='mlab.yml',
                        help='Filename where output will be written.')
    parser.add_argument('--juniper_template_path',
                        dest='juniper_template_path',
                        default='juniper-snmp_exporter-template',
                        help='Path to the Juniper config template file.')
    parser.add_argument('--other_template_path',
                        dest='other_template_path',
                        default='other-snmp_exporter-template',
                        help='Path to config template file for HPs and Ciscos.')

    args = parser.parse_args(args)

    return args


# TODO: the contents of this function are hopefully temporary. At the time of
# this writing, M-Lab does not have a centralized data store where site
# configuration data can be stored, retrieved and updated. In this particular
# example, the current canonical source of information for default switch SNMP
# communities and uplink ports is a file (switch-details.json) in the
# switch-config repository. In a better future, this function will consult some
# sort of centralized data store.
def read_switch_details():  # pragma: no cover
    """Retrieves switch details.

    Returns: A dict with all Juniper switch details
    """
    switch_details_path = 'switch-config/switch-details.json'

    with open(switch_details_path, 'r') as details_file:
        switch_details = json.load(details_file)

    return switch_details


def generate_site_config(site, details, config_template):
    """Generates an snmp_exporter config section for a given site.

    Args:
        site: str, short name of site (e.g., abc01).
        details: dict, switch configuration details.
        config_template: str, the string template for the switch.

    Returns:
        str, a valid snmp_exporter configuration for the passed site.
    """
    template = string.Template(config_template)

    template_vars = {'site': site, 'community': details['community']}

    try:
        site_config = template.substitute(template_vars)
    except KeyError, err:
        logging.error(err)
        raise

    return site_config


def write_config(switch_details, templates, output):
    """Writes configs for each site to a single config file.

    Args:
        switch_details: dict, all switch configuration details.
        templates: dict, string templates for various switch types.
        output: file, file handle to write output to.

    """
    for site, details in sorted(switch_details.iteritems()):
        if details['switch_make'] == 'juniper':
            config_template = templates['juniper']
        else:
            config_template = templates['other']

        site_config = generate_site_config(site, details, config_template)
        output.write(site_config)


def main(argv):
    """Main."""
    args = parse_options(argv[1:])
    switch_details = read_switch_details()
    exporter_config_file = open(args.output_file, 'w')

    templates = {}
    try:
        templates['juniper'] = open(args.juniper_template_path, 'r').read()
        templates['other'] = open(args.other_template_path, 'r').read()
    except IOError, err:
        logging.error(err)
        raise

    write_config(switch_details, templates, exporter_config_file)

    exporter_config_file.close()


if __name__ == '__main__':  # pragma: no cover
    main(sys.argv)