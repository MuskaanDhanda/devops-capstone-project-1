# Install Ansible on an Ubuntu EC2 instance

Use an Ubuntu EC2 instance as your Ansible control node. Connect to the instance using SSH, then run:

```bash
sudo apt update
sudo apt install -y ansible
ansible --version
```

If the `ansible` package is not available in the enabled repositories, enable Ubuntu's `universe` repository and try again:

```bash
sudo add-apt-repository --yes universe
sudo apt update
sudo apt install -y ansible
```

The EC2 instance needs outbound network access to the Ubuntu package repositories, and the connected user needs `sudo` privileges. To manage other EC2 instances with Ansible, configure SSH access and an inventory on the control node.