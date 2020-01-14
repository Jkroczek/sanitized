#!/usr/bin/python3
# Example script to test out paramiko and running sudo commands on remote servers. This example creates a home directory, chmods it, and then chowns it.
# This was part of a larger new user creation script.
# Created by jkroczek 1/14/20

import paramiko
import getpass
ldap_username = 'jefftest'


print('Home directory creation time\n')
remote_user = input('Enter the remote username (administrator, for testing): ')
remote_pass = getpass.getpass('Password: ')
remote_pass_sudo = remote_pass + '\n' # adds a return character to the password. This is so it will hit the enter key after the password when prompted for sudo
remote_directory_command = 'sudo mkdir /home/' + ldap_username
remote_chmod_command = 'sudo chmod 755 /home/' + ldap_username
remote_chown_command = 'sudo chown ' + ldap_username + ':' + ldap_username + ' /home/' + ldap_username

# Lists all the commands above
print('Command Summary:','----------------', sep='\n')
print(remote_directory_command, remote_chmod_command, remote_chown_command, sep='\n')

# Just for readability
ssh = paramiko.SSHClient()

# Function creates the connection to a remote server (hostname) via ssh
def ssh_connection(hostname, username, password):
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname, username=username, password=password)

# Function for remote commands, whatever you want to run remotely is the command variable. remote_pass_sudo is a global variable defined above. (/n at the end for a return)
def ssh_command(command):
    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
    stdin.write(remote_pass_sudo)
    stderr.read() # shows errors, if any

# Connects to the server, in this case, cloud
ssh_connection('cloud', remote_user, remote_pass)

# Actually do the thing
ssh_command(remote_directory_command)
ssh_command(remote_chmod_command)
ssh_command(remote_chown_command)

# Closes ssh session
ssh.close()