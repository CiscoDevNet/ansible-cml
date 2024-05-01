from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
  name: cml_node_definition
  author: Jason King <jasonkin@cisco.com>
  version_added: "1.2.2"
  short_description: Get CML node definitions
  description:
      - This lookup returns a list of dictionaries containing the node definitions in a CML instance.
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
from ansible.errors import AnsibleError, AnsibleParserError
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

    cml = cmlPlugin(host, username, password, validate_certs)

    try:
      nodedefs = cml.client.definitions.node_definitions()
    except Exception as e:
      raise AnsibleError("Failed to get node definitions: %s" % e)

    if self.get_option('id') is not None:
      for nodedef in nodedefs:
        if nodedef['id'] == self.get_option('id'):
          ret = [nodedef]
    else:
      ret = nodedefs
    
    return ret