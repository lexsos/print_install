#!/usr/bin/python

import ldap
import sys
import ConfigParser
import getpass


def extruct_group(fqdn):
   return  fqdn.split(',')[0].replace('CN=', '')


def get_user_list(ldap_domain, ldap_tree_scoupe, user_name, password):
    l = ldap.initialize("ldap://" + ldap_domain)
    l.set_option(ldap.OPT_REFERRALS, 0)
    l.protocol_version = 3
    l.simple_bind_s(user_name + "@" + ldap_domain, password)

    r = l.search(
        ldap_tree_scoupe,
        ldap.SCOPE_SUBTREE,
        '(&(objectCategory=person)(objectClass=user))',
        ['sAMAccountName', 'memberOf']
    )

    Type,Rez = l.result(r, 1, 10)

    users = {}
    for rez in Rez:
        try:
            groups = []
            for mem in rez[1]['memberOf']:
                groups.append(extruct_group(mem).lower())
            users[ rez[1]['sAMAccountName'][0].lower() ] = groups
        except:
            pass

    return users


config = ConfigParser.RawConfigParser()
config.read('printers.conf')

ldap_domain = config.get('general', 'ldap_domain')
ldap_tree_scoupe = config.get('general', 'ldap_tree_scoupe')
user_name = config.get('general', 'user_name')
out_dir = config.get('general', 'out_dir')
printer_list = dict(config.items('printers'))
user_defaults = dict(config.items('user_defaults'))

print 'Enter password for user {0}'.format(user_name)
password= getpass.getpass()

user_list = get_user_list(ldap_domain, ldap_tree_scoupe, user_name, password)

for user in user_list:
    cmd = open(out_dir + user + '.bat', 'w')
    for printer in printer_list:
        if printer in user_list[user]:
            cmd.write('rundll32 printui.dll,PrintUIEntry /in /n "{0}"\n'.format(printer_list[printer]))
    if user in user_defaults:
        try:
            printer_path = printer_list[user_defaults[user]]
            cmd.write('rundll32 printui.dll,PrintUIEntry /y /n "{0}"\n'.format(printer_path))
        except:
            pass
    cmd.close()
