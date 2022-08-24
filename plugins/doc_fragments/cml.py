from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    # Standard files for documentation fragment
    DOCUMENTATION = r'''
notes:
  - This should be run with connection C(local)
options:
    host:
        description: FQDN of the target host (CML_HOST)
        required: true
        type: str
    username:
        description: user credential for target system (CML_USERNAME)
        required: true
        type: str
        aliases:
            - user
    password:
        description: user pass for the target system (CML_PASSWORD)
        required: true
        type: str
    timeout:
        description: API Timeout
        required: false
        type: int
        default: 30
    validate_certs:
        description: certificate validation (CML_VALIDATE_CERTS)
        required: false
        type: bool
        default: false
'''
