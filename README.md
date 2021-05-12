# ansible-cml

Ansible Modules for CML^2

## Requirements

* Ansible v2.9 or newer is required for collection support

## What is Cisco Modelling Labs?

Cisco Modeling Labs is an on-premise network simulation tool that runs on workstations and servers. With Cisco Modeling Labs, you can quickly and easily simulate Cisco and non-Cisco networks, using real Cisco images. This gives you highly reliable models for designing, testing, and troubleshooting. Compared to building out real-world labs, Cisco Modeling Labs returns results faster, more easily, and for a fraction of the cost.

## Installation
### Directly from Ansible Galaxy

```
  ansible-galaxy collection install cisco.cml
```

### via git repository

```
  ansible-galaxy collection install 'git@github.com:CiscoDevNet/ansible-cml.git,branch'
```

## Environmental Variables

* `CML_USERNAME`: Username for the CML user (used when `host` not specified)
* `CML_PASSWORD`: Password for the CML user (used when `password` not specified)
* `CML_HOST`: The CML host (used when `host` not specified)
* `CML_LAB`: The name of the lab

## Inventory

To use the dynamic inventory plugin, the environmental variables must be set and a file (e.g. `cml.yml`) placed in the inventory specifying the plugin information:

```
plugin: cisco.cml.cml_inventory
```

The dynamic inventory script will then return information about the nodes in the
lab:

```
ok: [hq-host1] => {
    "cml_facts": {
        "config": "#cloud-config\npassword: admin\nchpasswd: { expire: False }\nssh_pwauth: True\nhostname: hq-host1\nruncmd:\n - sudo ip address add 10.0.1.10/24 dev enp0s2\n - sudo ip link set dev enp0s2 up\n - sudo ip route add default via 10.0.1.1\n",
        "cpus": null,
        "data_volume": null,
        "image_definition": "ubuntu-18-04",
        "interfaces": [
            {
                "ipv4_addresses": [],
                "ipv6_addresses": [],
                "mac_address": "52:54:00:13:1b:fb",
                "name": "enp0s2",
                "state": "STARTED"
            }
        ],
        "node_definition": "ubuntu",
        "ram": null,
        "state": "BOOTED"
    }
}
```

## Example Playbooks

### Create a Lab
    - name: Create the lab
      cml_lab:
        host: "{{ cml_host }}"
        user: "{{ cml_username }}"
        password: "{{ cml_password }}"
        lab: "{{ cml_lab }}"
        state: present
        file: "{{ cml_lab_file }}"
      register: results

### Start a Node

    - name: Start Node
      cml_node:
        name: "{{ inventory_hostname }}"
        host: "{{ cml_host }}"
        user: "{{ cml_username }}"
        password: "{{ cml_password }}"
        lab: "{{ cml_lab }}"
        state: started
        image_definition: "{{ cml_image_definition | default(omit) }}"
        config: "{{ day0_config | default(omit) }}"

### Collect facts about the Lab
    - name: Collect Facts
      cml_lab_facts:
        host: "{{ cml_host }}"
        user: "{{ cml_username }}"
        password: "{{ cml_password }}"
        lab: "{{ cml_lab }}"
      register: result

## License

GPLv3
