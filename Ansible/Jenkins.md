# DevOps Capstone Project 1

## Problem Statement

You have been hired as a Sr. DevOps Engineer in Abode Software. They want to implement DevOps Lifecycle in their company. You have been asked to implement this lifecycle as fast as possible. Abode Software wants the following setup:

<https://github.com/hshar/website.git>

Following are the specifications of the lifecycle:

1. Install the necessary software on the machines using a configuration management tool
2. Git workflow has to be implemented
3. CodeBuild should automatically be triggered once a commit is made to master branch or develop branch.
   - a. If a commit is made to master branch, test and push to prod
   - b. If a commit is made to develop branch, just test the product, do not push to prod
4. The code should be containerized with the help of a Dockerfile. The Dockerfile should be built every time there is a push to GitHub. Use the following pre-built container for your application: `hshar/webapp:latest`
5. The above tasks should be defined in a Jenkins Pipeline with the following jobs:
   - a. Job1 : build
   - b. Job2 : test
   - c. Job3 : prod

---

## Solution

### 1. Launch EC2 instances

Log in to the AWS console, go to EC2, launch 3 instances (Master, Test, Prod) and connect to all three machines.

![image1](image1.png)

Run in all EC2:

```bash
sudo apt update
```

### 2. Install Ansible (Master EC2)

```bash
sudo nano ansible_install.sh
```

![image2](image2.png)

Code:

```bash
sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install ansible -y
```

```bash
bash ansible_install.sh
ansible --version
```

![image3](image3.png)

### 3. Set up passwordless SSH

For key generation (Master EC2):

```bash
cd .ssh
ssh-keygen -t rsa
sudo cat id_rsa.pub
```

![image4](image4.png)

Copy the key and paste it in the Test and Prod EC2.

Run in Test & Prod EC2:

```bash
cd .ssh
ls
sudo nano authorized_keys
```

![image5](image5.png)

![image6](image6.png)

### 4. Configure Ansible inventory (Master EC2)

```bash
cd ..
cd /etc/ansible
ls
sudo nano hosts
```

```ini
[slave]
172.31.19.121
172.31.25.232
```

```bash
ls
sudo nano ansible.cfg
```

```ini
[defaults]
host_key_checking = False
```

```bash
ansible -m ping all
```

![image7](image7.png)

### 5. Playbook and scripts

```bash
sudo nano play.yaml
```

```yaml
---
- name: install java and jenkins in localhost
  hosts: localhost
  become: true
  tasks:
    - name: installing java and jenkins
      script: localhost.sh

- name: install java and docker in test and prod
  hosts: slave
  become: true
  tasks:
    - name: installing java and docker
      script: slave.sh
```

```bash
sudo nano localhost.sh
```

```bash
# Install Java
sudo apt update
sudo apt install openjdk-21-jdk -y

# Install Jenkins
sudo wget -O /etc/apt/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key
echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/" | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt update
sudo apt install jenkins -y
```

```bash
sudo nano slave.sh
```

```bash
# Install Java in Slaves
sudo apt update
sudo apt install openjdk-21-jdk -y

# Install Docker in Slaves
sudo apt install docker.io -y
```

![image8](image8.png)

![image9](image9.png)

![image10](image10.png)

### 6. Jenkins setup

Go to the browser and paste the Master EC2 public IP: `http://<Public IP>:8080`

![image11](image11.png)

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

You will get the password from this — paste it in Administrator password.

![image12](image12.png)

![image13](image13.png)

### 7. Add the Test node

Go to **Settings > Nodes > New Node** and create it.

![image14](image14.png)

![image15](image15.png)

- **Remote root directory:** `/home/ubuntu/jenkins/`
- **Labels:** `test`
- **Launch method:** Launch agents via SSH
- **Host:** Private IP (Test EC2)
- **Credentials:** + ADD > Global > SSH Username with private key > Username: `ubuntu` > enter key (.pem) directly

![image16](image16.png)

- **Host Key Verification Strategy:** Non verifying verification strategy

**SAVE**

![image17](image17.png)

![image18](image18.png)

---

## JOB1: Build

![image19](image19.png)

Fork (copy) the code from <https://github.com/hshar/website>

![image20](image20.png)

![image21](image21.png)

After creating the fork, copy the GitHub link.

![image22](image22.png)

![image23](image23.png)

- **Restrict where this project can be run:** yes
- **Label Expression:** `test` (node)
- **Source Code Management:** Git
- **Repositories:** Paste the same link as the project URL
- **Credentials:** ubuntu (created in node)
- **Branches to build:** `*/master`
- **Triggers:** GitHub hook trigger for GITScm polling

Go to GitHub > forked repo **Settings > Webhooks > Add webhook**:

- **Payload URL:** `http://100.53.188.134:8080/github-webhook/`

The link up to `8080/` is the Jenkins dashboard link, followed by `github-webhook/`.

![image24](image24.png)

**SAVE > click Build Now**

![image25](image25.png)

![image26](image26.png)

![image27](image27.png)

![image28](image28.png)

![image29](image29.png)

![image30](image30.png)

![image31](image31.png)

---

## JOB2: Test

GitHub > website repo > **+ Add file > Create new file** > `Dockerfile`:

```dockerfile
FROM ubuntu
RUN apt update
RUN apt install apache2 -y
COPY . /var/www/html/
ENTRYPOINT apachectl -D FOREGROUND
```

![image32](image32.png)

Commit it.

![image33](image33.png)

GitHub > website > go to master branch > search `develop` > create branch `develop` from master.

![image34](image34.png)

The develop branch has the same files as master, including the Dockerfile.

![image35](image35.png)

Let's create Job2.

![image36](image36.png)

- **Restrict where this project can be run:** yes
- **Label Expression:** `test` (node)
- **Source Code Management:** Git
- **Repositories:** Paste the same link as the project URL
- **Credentials:** ubuntu (created in node)
- **Branches to build:** `*/develop`
- **Triggers:** GitHub hook trigger for GITScm polling

![image37](image37.png)

**Build Steps** — Add Build Step > Execute Shell

![image38](image38.png)

```bash
sudo docker build . -t img1
sudo docker run -itd -p 81:80 --name c1 img1
```

**SAVE > Build Now**

![image39](image39.png)

![image40](image40.png)

Copy the public IP of the Test EC2 and paste it in the browser with `:81` (as per the container port).

![image41](image41.png)

### Fixing the build failure

The Jenkins build fails on re-runs because a container cannot run again on the same port with the same name.

![image42](image42.png)

Resolution: Jenkins > Job2 > Configure > Build Steps > add (before the build commands):

```bash
sudo docker rm -f c1
```

![image43](image43.png)

This removes the previous container and adds a new one.

![image44](image44.png)

**SAVE**

![image45](image45.png)

![image46](image46.png)

![image47](image47.png)

---

## JOB3: Prod

Create node: **Settings > Nodes > New > prod > done**

![image48](image48.png)

![image49](image49.png)

![image50](image50.png)

![image51](image51.png)

![image52](image52.png)

![image53](image53.png)

![image54](image54.png)

![image55](image55.png)

![image56](image56.png)

![image57](image57.png)

![image58](image58.png)

![image59](image59.png)

![image60](image60.png)
