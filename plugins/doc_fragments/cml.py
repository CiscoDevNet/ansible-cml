from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    # Standard files for documentation fragment
    DOCUMENTATION = r'''
notes:
  - This should be run with connection C(local)
options:
    host:
        description: FQDN of the target host (env: CML_HOST)
        required: false
        type: string
    username:
        description: user credential for target system (env: CML_USERNAME)
        required: false
        type: string
    password:
        description: user pass for the target system (env: CML_PASSWORD)
        required: false
        type: string
    validate_certs:
        description: certificate validation (env: CML_VALIDATE_CERTS)
        required: false
        type: boolean
'''
