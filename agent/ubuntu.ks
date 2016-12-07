#version=RHEL7

install
text
cmdline
skipx

lang en_US.UTF-8
keyboard --vckeymap=jp106 --xlayouts=jp
timezone Asia/Tokyo --isUtc --nontp

network --activate --bootproto=dhcp --noipv6

bootloader --location=mbr

clearpart --all --initlabel
part / --fstype=xfs --grow --size=1 --asprimary --label=root

rootpw --plaintext password
auth --enableshadow --passalgo=sha51
selinux --disabled
firewall --disabled
firstboot --disabled

clearpart --all --initlable
autopart

reboot

%packages
@core
%end

%post --log=/var/log/anaconda-post.log --erroronfail
apt-get install openssh-server
apt-get install sshpass

sed s/#PasswordAuthentication/PasswordAuthentication/ -i /etc/ssh/sshd_config
sed s/PasswordAuthentication\ yes/PasswordAuthentication\ no/ -i /etc/ssh/sshd_config
#sed s/PasswordAuthentication\ no/PasswordAuthentication\ yes/ -i /etc/ssh/sshd_config
sed s/#RSAAuthentication/RSAAuthentication/ -i /etc/ssh/sshd_config
sed s/RSAAuthentication\ no/RSAAuthentication\ yes/ -i /etc/ssh/sshd_config
sed s/#PubkeyAuthentication/PubkeyAuthentication/ -i /etc/ssh/
sed s/PubkeyAuthentication\ no/PubkeyAuthentication\ yes/ -i /etc/ssh/sshd_config
#sed s/#PermitRootLogin/PermitRootLogin/ -i /etc/ssh/sshd_config

mkdir /root/.ssh
chmod 700 /root/.ssh
ssh-keygen -f /root/.ssh/vm -t rsa -N ''
cat /root/.ssh/vm.pub >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
sshpass -p 'centos' scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=no /root/.ssh/vm.pub root@192.168.1.2:~/agent/pub
systemctl restart sshd

#SSH
SSH_USER=root
SSH_PASS=centos
SSH_HOST=192.168.1.2
SSH_DIR=~/agent/

#export PASSWORD=$SSH_PASS
#export SSH_ASKPASS=$0
#export DISPLAY=dummy:0

#exec setsid scp /root/.ssh/vm.pub $SSH_USER@$SSH_HOST:$SSH_DIR
#sshpass -p $SSH_PASS scp /root/.ssh/vm.pub $SSH_USER@SSH_HOST:$SSH_DIR

%end
