# Install Ansible on an Ubuntu EC2 instance

Use an Ubuntu EC2 instance as your Ansible control node. Connect to the instance using web, then run:

```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install ansible
```


# Verify Installation

Check that Ansible is installed 

```bash
ansible --version
```

The EC2 instance needs outbound network access to the Ubuntu package repositories, and the connected user needs `sudo` privileges. To manage other EC2 instances with Ansible, configure SSH access and an inventory on the control node.

