#!/bin/bash
# Made by jkroczek 7/26/19 using examples from here:
# https://serverfault.com/questions/647805/how-to-set-up-icinga2-remote-client-without-using-cli-wizard

# variables
pki_dir="/etc/icinga2/pki"                        # /etc/icinga2/pki in the default installation
fqdn=$(hostname)                                  # hostname of the client.
icinga2_master=""       # resolvable fqdn of the master
icinga2_master_port="5665"                        # the port the master is connectable on.

#asking for ticket

echo "generated on the master via 'icinga2 pki ticket --cn $fqdn'"
read ticket                                        # asks for the ticket number after running the echoed command on the master

# action
mkdir nagios:nagios 0700 $pki_dir
icinga2 pki new-cert --cn $fqdn --key $pki_dir/$fqdn.key --cert $pki_dir/$fqdn.crt
icinga2 pki save-cert --key $pki_dir/$fqdn.key --cert $pki_dir/$fqdn.crt --trustedcert $pki_dir/trusted-master.crt --host $icinga2_master
icinga2 pki request --host $icinga2_master --port $icinga2_master_port --ticket $ticket --key $pki_dir/$fqdn.key --cert $pki_dir/$fqdn.crt --trustedcert $pki_dir/trusted-master.crt --ca $pki_dir/ca.key
icinga2 node setup --ticket $ticket \
--endpoint $icinga2_master \
--zone $fqdn \
--master_host $icinga2_master \
--trustedcert $pki_dir/trusted-master.crt \
--accept-commands \
--accept-config \
--disable-confd

# restarts the service
systemctl restart icinga2