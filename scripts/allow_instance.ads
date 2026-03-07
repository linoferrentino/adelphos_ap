#
sudo_adelphos_allow remote_adelphos www.adelphos.it

# force the login as user lino
_auto_su alias ##john.jf

# force the creation of user
_auto_create_user user ##user99.family password 99
# start commands as lino

# su john


_auto_expect last_msg OK
