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

reboot

%packages
@core
%end

%post --log=/var/log/anaconda-post.log --erroronfail
sed s/#PasswordAuthentication/PasswordAuthentication/ -i /etc/ssh/sshd_config
#sed s/PasswordAuthentication\ yes/PasswordAuthentication\ no/ -i /etc/ssh/sshd_config
sed s/PasswordAuthentication\ no/PasswordAuthentication\ yes/ -i /etc/ssh/sshd_config
sed s/#RSAAuthentication/RSAAuthentication/ -i /etc/ssh/sshd_config
sed s/RSAAuthentication\ no/RSAAuthentication\ yes/ -i /etc/ssh/sshd_config
sed s/#PubkeyAuthentication/PubkeyAuthentication/ -i /etc/ssh/
sed s/PubkeyAuthentication\ no/PubkeyAuthentication\ yes/ -i /etc/ssh/sshd_config
#sed s/#PermitRootLogin/PermitRootLogin/ -i /etc/ssh/sshd_config

mkdir /root/.ssh
chmod 700 /root/.ssh
ssh-keygen -f /root/.ssh/vm -t rsa -N ''
cat vm.pub >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
systemctl restart sshd

#SSH
SSH_USER=nao
SSH_PASS=ns1192
SSH_HOST=192.168.11.2
SSH_DIR=~/

if [ -n "$PASSWORD" ]; then
  cat <<< "$PASSWORD"
  exit 0
fi

export PASSWORD=$SSH_PASS
export SSH_ASKPASS=$0
export DISPLAY=dummy:0
#exec setsid scp /root/.ssh/vm.pub $SSH_USER@$SSH_HOST:$SSH_DIR

%end
