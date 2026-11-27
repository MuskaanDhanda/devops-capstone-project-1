#!/bin/bash
# Installs Java and Docker on the test and prod agents (run by playbook.yml on [slave] hosts)
set -euo pipefail

# Install Java
sudo apt update
sudo apt install openjdk-21-jdk -y

# Install Docker
sudo apt install docker.io -y
