# -*- coding: utf-8 -*-

# Copyright (c) 2017 Cisco and/or its affiliates.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
name: cml_node_definition
author:
    - Jason King (@jasonkin)
version_added: '1.2.0'
short_description: Get CML node definitions
description:
    - This lookup returns a list of dictionaries containing the node definitions in a CML instance.
requirements:
    - virl2_client
options:
    cml_host:
        description: The hostname or IP address of the CML instance
        required: True
    cml_username:
        description: The username to authenticate to the CML instance
        required: True
    cml_password:
        description: The password to authenticate to the CML instance
        required: True
    validate_certs:
        description: Whether to validate SSL certificates
        required: False
        default: False
    id:
        description: The ID of the node definition to return (optional)
        required: False
"""
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
from ansible_collections.cisco.cml.plugins.module_utils.cml_utils import cmlPlugin

display = Display()


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        ret = []

        host = self.get_option('cml_host')
        username = self.get_option('cml_username')
        password = self.get_option('cml_password')
        validate_certs = self.get_option('validate_certs')

        cml = cmlPlugin(self, host, username, password, validate_certs)

        try:
            nodedefs = cml.client.definitions.node_definitions()
        except Exception as e:
            self.fail("Failed to get node definitions: %s" % e)

        if self.get_option('id') is not None:
            for nodedef in nodedefs:
                if nodedef['id'] == self.get_option('id'):
                    ret = [nodedef]
        else:
            ret = nodedefs

        return ret

    def fail(self, msg):
        raise AnsibleError(msg)
