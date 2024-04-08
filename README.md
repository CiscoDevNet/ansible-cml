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

The dynamic inventory script will then return information about the nodes in the
lab:

```
ok: [hq-rtr1] => {
    "cml_facts": {
        "config": "hostname hq-rtr1\nvrf definition Mgmt-intf\n!\naddress-family ipv4\nexit-address-family\n!\naddress-family ipv6\nexit-address-family\n!\nusername admin privilege 15 secret 0 admin\ncdp run\nno aaa new-model\nip domain-name mdd.cisco.com\n!\ninterface GigabitEthernet1\nvrf forwarding Mgmt-intf\nip address dhcp\nnegotiation auto\nno cdp enable\nno shutdown\n!\ninterface GigabitEthernet2\ncdp enable\n!\ninterface GigabitEthernet3\ncdp enable\n!\ninterface GigabitEthernet4\ncdp enable\n!\nip http server\nip http secure-server\nip http max-connections 2\n!\nip ssh time-out 60\nip ssh version 2\nip ssh server algorithm encryption aes128-ctr aes192-ctr aes256-ctr\nip ssh client algorithm encryption aes128-ctr aes192-ctr aes256-ctr\n!\nline vty 0 4\nexec-timeout 30 0\nabsolute-timeout 60\nsession-limit 16\nlogin local\ntransport input ssh\n!\nend",
        "cpus": 1,
        "data_volume": null,
        "image_definition": null,
        "interfaces": [
            {
                "ipv4_addresses": null,
                "ipv6_addresses": null,
                "mac_address": null,
                "name": "Loopback0",
                "state": "STARTED"
            },
            {
                "ipv4_addresses": [
                    "192.168.255.199"
                ],
                "ipv6_addresses": [],
                "mac_address": "52:54:00:13:51:66",
                "name": "GigabitEthernet1",
                "state": "STARTED"
            }
        ],
        "node_definition": "csr1000v",
        "ram": 3072,
        "state": "BOOTED"
    }
}
```

The first IPv4 address found (in order of the interfaces) is used as `ansible_host` to enable the playbook to connect to the device.

To use the CML dynamic inventory plugin, the environmental variables must be set and a file (e.g. `cml.yml`) placed in the inventory specifying the plugin information:

```
plugin: cisco.cml.cml_inventory
group_tags: network, ios, nxos, router
```

Options:

`plugin:` Specfies the name of the inventory plugin
`group_tags:` The group tags that, if one or more are found in a CML device tags, will create an Ansible group of the same name

To create an Ansible group, specify a device tag in CML:

![CML Tag Example](cml_group_tag.png?raw=true "CML Tag Example")

When the CML dynamic inventory plugin runs, it will create a router group with all of the devices that have that tag:
```
mdd % ansible-playbook cisco.cml.inventory --limit=router

PLAY [cml_hosts] ******************************************************************************************************************************

TASK [debug] **********************************************************************************************************************************
ok: [hq-rtr1] => {
    "msg": "Node: hq-rtr1(csr1000v), State: BOOTED, Address: 192.168.255.199:22"
}
ok: [hq-rtr2] => {
    "msg": "Node: hq-rtr2(csr1000v), State: BOOTED, Address: 192.168.255.53:22"
}
ok: [site1-rtr1] => {
    "msg": "Node: site1-rtr1(csr1000v), State: BOOTED, Address: 192.168.255.63:22"
}
ok: [site2-rtr1] => {
    "msg": "Node: site2-rtr1(csr1000v), State: BOOTED, Address: 192.168.255.7:22"
}

PLAY RECAP ************************************************************************************************************************************
hq-rtr1                    : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
hq-rtr2                    : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
site1-rtr1                 : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
site2-rtr1                 : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

In addition to group tags, the CML dynamic inventory plugin will also parse tags to pass information from PATty and to create 
generic inventory facts. 

![PAT Tag Example](cml_pat_tags.png?raw=true "PAT Tag Example")

If a CML tag is specified that matches `^pat:(?:tcp|udp)?:?(\d+):(\d+)`, the CML server address (as opposed to the first IPv4 address found)
will be used for `ansible_host`.  To change `ansible_port` to point to the translated SSH port, the tag `ansible:ansible_port=2020` can
be set.  These two tags tell the Ansible playbook to connect to port 2020 of the CML server to automate the specified host in the topology.
The `ansible:` tag can also be used to specify other host facts.  For example, the tag `ansible:nso_api_port=2021` can be used to tell the
playbook the port to use to reach the Cisco NSO API.  Any arbitrary fact can be set in this way.


## Collection Playbooks

### `cisco.cml.build`

* Build a topology

extra_vars:
  * `startup`: Either `all` to start up all devices at one or `host` to startup devices individually (default: `all`)
  * `wait`: Whether to wait for the task to complete before returning (default: `no`)

notes:
  * `cml_lab_file` lab file must be defined and will be read in as a J2 template.
  * When `cml_config_file` is specified per host and `-e startup='host'` is specified, the file is read in as a J2 template and fed into the device at startup.

### `cisco.cml.clean`

* Clean a topology

tags:
  * `stop`: Just stop the topology
  * `wipe`: Stop and wipe the topology
  * `erase`: Stop, wipe, and erase the topology

### `cisco.cml.inventory`

* Show topology Inventory

## Example Playbooks

### Create a Lab
    - name: Create the lab
      cisco.cml.cml_lab:
        host: "{{ cml_host }}"
        user: "{{ cml_username }}"
        password: "{{ cml_password }}"
        lab: "{{ cml_lab }}"
        state: present
        file: "{{ cml_lab_file }}"
      register: results

### Start a Node

    - name: Start Node
      cisco.cml.cml_node:
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
      cisco.cml.cml_lab_facts:
        host: "{{ cml_host }}"
        user: "{{ cml_username }}"
        password: "{{ cml_password }}"
        lab: "{{ cml_lab }}"
      register: result

## License

GPLv3

## Development
### Running sanity tests locally
Clean existing build:
```
make clean
```

Build the collection:
```
make build
```

Test the collection:
```
make test
```
