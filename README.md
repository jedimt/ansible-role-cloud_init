Ansible Role: Cloud-Init
=========

Prepares an Ubuntu host for Cloud Init.

Requirements
------------

None.

Role Variables
--------------

The following variables are defined in defaults/main.yml:

    # Vault protected password to use for account configuration
    ssh_password: "{{ vault_ansible_password }}"

    # Nebulon On credentials
    neb_username: "{{ vault_automation_username }}"
    neb_password: "{{ vault_automation_password }}"

    # Public SSH keys to pull in from Ansible Vault
    vault_pubkeys: "{{ vault_pubkeys }}"

    # Password to use to connect when SSH keys are not installed
    ansible_password: "{{ vault_ansible_password }}"
    ansible_sudo_pass: "{{ vault_ansible_password }}"

    # Non-root user to use for first connection before SSH is configured to allow root access
    ansible_user: "apatt"

    # Path to put Nebulon configuration scripts
    user_data_path: "/etc/cloud/nebulon/"

Dependencies
------------

None.

Example Playbook
----------------

    - name: Cloud Init image prep for Ubuntu 20/22 in TME environment
      hosts: servers[0]
      gather_facts: false
      become: true

      vars_files:
        # Ansible vault with all required passwords
        - "../../credentials.yml"

      roles:
        - { role: ansible-role-cloud-init,
            ansible_password: "{{ vault_ansible_password }}"
        }

License
-------

MIT

Author Information
------------------

Aaron Patten
aaronpatten@gmail.com
