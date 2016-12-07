#!/bin/bash

create_img(){
    local NAME=$2
    local SIZE=$4

    if [ ! -e "./images/${NAME}.img" ]; then
        qemu-img create -f qcow2 ./images/${NAME}.img ${SIZE}G
    fi
}

remove_img(){
    local NAME=$2

    if [ -e "./images/${NAME}.img" ]; then
        rm -f ./images/${NAME}.img
    fi
}

# iso image @ http://ftp.riken.jp/Linux/centos/7.2.1511/isos/x86_64/
create_centos7(){
    local NAME=$2
    local SIZE=$4
    local CPU=$5
    local RAM=$6

    echo "create_centos7"
    virt-install \
    --connect qemu:///system \
    --name=${NAME} \
    --ram=${RAM} \
    --disk path=./images/${NAME}.img,format=qcow2,size=${SIZE} \
    --vcpus ${CPU} \
    --os-type linux \
    --os-variant generic \
    --network bridge=virbr0 \
    --noautoconsole \
    --graphics none \
    --location=./iso/CentOS-7-x86_64-Minimal-1511.iso \
    --initrd-inject=./centos.ks \
    --extra-args "inst.ks=file:/centos.ks console=ttyS0"
}

create_ubuntu1404(){
    local NAME=$2
    local SIZE=$4
    local CPU=$5
    local RAM=$6

    virt-install \
    --connect qemu:///system \
    --name=${NAME} \
    --ram=${RAM} \
    --disk path=/var/lib/libvirt/images/${NAME}.img,format=qcow2,size=${SIZE} \
    --vcpus ${CPU} \
    --os-type linux \
    --os-variant generic \
    --network network='default' \
    --noautoconsole \
    --nographics \
    --location='http://jp.archive.ubuntu.com/ubuntu/dists/trusty/main/installer-amd64/' \
    --initrd-inject=./ubuntu.ks \
    --extra-args "inst.ks=file:/ubuntu.ks console=ttyS0"
}

# iso image @ http://ftp.riken.jp/Linux/opensuse/distribution/13.2/iso/
create_opensuse13(){
    local NAME=$2
    local SIZE=$4
    local CPU=$5
    local RAM=$6

    virt-install \
    --connect qemu:///system \
    --name=${NAME} \
    --ram=${RAM} \
    --disk path=/var/lib/libvirt/images/${NAME}.img,format=qcow2,size=${SIZE} \
    --vcpus ${CPU} \
    --os-type linux \
    --os-variant generic \
    --network network='default' \
    --noautoconsole \
    --nographics \
    --location=./iso/openSUSE-13.2-GNOME-Live-x86_64.iso \
    --initrd-inject=./opensuse.ks \
    --extra-args "inst.ks=file:/opensuse.ks console=ttyS0"
}

# iso image @ http://ftp.riken.jp/Linux/debian/debian-cdimage/release/8.6.0/amd64/iso-cd/
create_debian8(){
    local NAME=$2
    local SIZE=$4
    local CPU=$5
    local RAM=$6

    virt-install \
        --connect qemu:///system \
        --name=${NAME} \
        --ram=${RAM} \
        --disk path=/var/lib/libvirt/images/${NAME}.img,format=qcow2,size=${SIZE} \
        --vcpus ${CPU} \
        --os-type linux \
        --os-variant generic \
        --network network='default' \
        --graphics none \
        --location ./iso/debian-8.6.0-amd64-xfce-CD-1.iso \
        --initrd-inject=./centos.ks \
        --extra-args "inst.ks=file:/centos.ks console=ttyS0"
}

create_kvm(){
    local NAME=$2
    local OS=$3

    create_img $@

    case $OS in
        "centos7" )
            create_centos7 $@
            ;;
        "debian8" )
            create_debian8 $@
            ;;
        "ubuntu1404" )
            create_ubuntu1404 $@
            ;;
        "opensuse13" )
            create_opensuse13 $@
            ;;
    esac
}
