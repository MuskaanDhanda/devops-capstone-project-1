#!/bin/bash
# Installs Java and Jenkins on the Jenkins master (run by playbook.yml on localhost)
set -euo pipefail

# Install Java
sudo apt update
sudo apt install openjdk-21-jdk -y

# Install Jenkins
sudo mkdir -p /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key
echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" \
  | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt update
sudo apt install jenkins -y
