
root.push_alias alias giacomo.leopardi

alias.send_msg alias_to #al#dante.alighieri msg "is there an afterlife?"

root.pop_alias

root.push_alias alias dante.alighieri

$ pop_msg | dmsg

$ assert | pars['dmsg']['alias_from_uri'] == "#al#giacomo.leopardi@www.adelphos.it"
$ assert | pars['dmsg']['alias_to_uri'] == "#al#dante.alighieri@www.adelphos.it"
$ assert | pars['dmsg']['raw'] == "is there an afterlife?"

alias.send_msg alias_to #al#giacomo.leopardi msg "Of course, Giacomo. I went there!"

root.pop_alias

root.push_alias alias giacomo.leopardi

$ pop_msg | dmsg
$ assert | pars['dmsg']['raw'] == "Of course, Giacomo. I went there!"

root.pop_alias
