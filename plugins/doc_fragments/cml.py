from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):
    # Standard files for documentation fragment
    DOCUMENTATION = r'''
notes:
  - This should be run with connection C(local)
options:
    host:
        description: 'FQDN of the target host (env: CML_HOST)'
        required: true
        type: str
    username:
        description: 'User credential for target system (env: CML_USERNAME)'
        required: true
        type: str
        aliases:
            - user
    password:
        description: 'User pass for the target system (env: CML_PASSWORD)'
        required: true
        type: str
    timeout:
        description: Timeout
        required: false
        type: int
        default: 30
    validate_certs:
        description: Certificate validation
        required: false
        default: false
        type: bool
'''
