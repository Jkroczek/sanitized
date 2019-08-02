#!/usr/bin/python3
# Script to create a new user in OpenLDAP
# Usage: create_user.py <username> <password> <email>
#
# Created by jkroczek 3/22/19
# Updated by jkroczek 8/2/19

import sys
import ldap3
import re
import getpass
from passlib.hash import ldap_md5_crypt

# Email format function
def isValidEmail(email):
    if len(email) > 7:
        if re.match(r"^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", email) != None:
            return True
        return False

# Prompting for username, email, and password. the if not statement just checks to make sure the variable isn't ""
ldap_username = input('Enter the username: ') # Username
if not ldap_username:
    print('Username is empty!')
    sys.exit()

ldap_userpass = input('Enter the password: ') # Password
if not ldap_userpass:
    print('Password is empty!')
    sys.exit()

ldap_email = input('Enter the email address: ') # Email
if not ldap_email:
    print('Email is empty!')
    sys.exit()

# Checks if email is in a valid format
if isValidEmail(ldap_email) == False:
    print('Not a valid email')
    sys.exit()

# hashing password with md5_crypt
# hash will be similar to '{CRYPT}$1$wa6OLvW3$uzcIj2Puf3GcFDf2KztQN0'
ldap_userpass_hash = ldap_md5_crypt.encrypt(ldap_userpass)

# Display summary on screen
print('Username: ' + ldap_username)
print('Password: ' + ldap_userpass)
print('Email: ' + ldap_email)

# Prompt for LDAP admin password. Using getpass.getpass so it doesn't echo
ldap_adminpass = getpass.getpass('Enter LDAP admin password: ')

# LDAP server connection
server = ldap3.Server('ldap-server.companyname.com', port=389)
connection = ldap3.Connection(server, user='cn=admin,dc=companyname,dc=com', password=ldap_adminpass)
connection.bind()

# Search to find all uid numbers and find next available uid
connection.search(search_base='ou=users,dc=companyname,dc=com', search_filter = '(objectClass=account)', attributes=['uidNumber'])
dirty_uid_list = connection.entries

new_list = [] # Declares new_list as a list
for uid in dirty_uid_list:
    x = re.search(r'(\d+)$', str(uid))
    if x:
        new_list.append(x.group(0))

# Manipulates the list in various ways to determine what the next available uidNumber is going to be.
new_list.sort(key=float) # Since the list is strings, this sorts them by float, but leaves them as strings
new_list.remove('9999') # Removes the 9999 uidNumber
new_uid = int(new_list[-1]) + 1 # Takes the last entry in the list, and adds 1 to it, defining the next available uidNumber as new_uid

# Add the group
groupcn = 'cn=' + ldap_username + ',ou=groups,dc=companyname,dc=com'
connection.add(groupcn, ['posixGroup', 'top'], {'gidNumber': new_uid})
print(connection.result)


# Add the user
usercn = 'uid=' + ldap_username + ',ou=users,dc=companyname,dc=com'
connection.add(usercn, [
                        'extensibleObject',
                        'posixAccount',
                        'shadowAccount',
                        'account',
                        'top'
                        ], 
                       {'cn': ldap_username,
                        'email': ldap_email,
                        'gecos': ldap_username,
                        'gidNumber': new_uid,
                        'homeDirectory': '/home/' + ldap_username,
                        'loginShell': '/bin/bash',
                        'userPassword': ldap_userpass_hash,
                        'shadowLastChange': 99999, 
                        'shadowMax': 0, 
                        'shadowWarning': 0, 
                        'uidNumber': new_uid 
                        }
)

# Clean disconnect
connection.unbind()