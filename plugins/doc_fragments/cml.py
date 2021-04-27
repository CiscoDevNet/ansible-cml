from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):
    # Standard files for documentation fragment
    DOCUMENTATION = r'''
notes:
  - This should be run with connection C(local)
options:
    host:
        description: FQDN of the target host
        required: false
        type: string
        default: 'env: CML_HOST'
        env:
            - name: CML_HOST
    username:
        description: user credential for target system
        required: false
        type: string
        default: 'env: CML_USERNAME'
        env:
            - name: CML_USERNAME
    password:
        description: user pass for the target system
        required: false
        type: string
        default: 'env: CML_PASSWORD'
        env:
            - name: CML_PASSWORD
'''
