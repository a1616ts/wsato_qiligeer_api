#!/bin/bash

. ./virt_install_config.sh
. ./virt-addr.sh # @https://gist.github.com/mistofvongola/4447791

case $1 in
    "create")
        create_kvm $@
        ;;
    "start")
        virsh resume $2
        ;;
    "resume")
        virsh resume $2
        ;;
    "suspend")
        virsh suspend $2
        ;;
    "destroy")
        virsh destroy $2
        ;;
    "shutdown")
        virsh shutdown $2
        ;;
    "close")
        virsh undefine $2
        remove_img $@ # delete the local image
	;;
    "undefine")
        virsh undefine $2
        remove_img $@ # delete the local image
        ;;
    "getstate")
        virsh domstate $2
        ;;
    "listall")
        virsh list --all
        ;;
    "getip")
        virt-addr $2
        ;;
esac
