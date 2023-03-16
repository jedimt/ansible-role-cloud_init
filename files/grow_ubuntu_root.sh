#!/bin/bash
#This script grows the root filesystem on Ubuntu hosts
#This is reqiured because LVM is not handled natively by cloud-init yet

DISK=$(lsscsi | grep -m 1 -i nebvolume | awk '{print $6}')
#export DISK
#echo "Re-sising device:"  $DISK"3"

growpart $DISK 3
pvresize $DISK"3"
lvresize -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
resize2fs /dev/ubuntu-vg/ubuntu-lv
