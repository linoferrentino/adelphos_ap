root.push_alias alias a1.f1_l0

family.change_carrier family_uri #fa#f7_l0 new_carrier_uri #al#c2.f2_l0 \
		==> { "errno" : 12 }

family.change_carrier family_uri #fa#f1_l0 new_carrier_uri #al#c2.f2_l0 \
		==> { "errno" : 33 }

family.change_carrier family_uri #fa#f1_l0 new_carrier_uri #al#b1.f1_l0

$ assert_uri_k_v | #ag#f1_l0_main_agora carrier $#al#b1.f1_l0@www.adelphos.it

root.pop_alias

root.push_alias alias b7.f7_l0

family.change_carrier family_uri #fa#f4-7_l2 new_carrier_uri #al#a1.f1_l0 \
		==> { "errno" : 33 }

root.pop_alias

family.change_carrier family_uri #fa#f4-7_l2 new_carrier_uri #al#a1.f1_l0 \
		==> { "errno" : 33 }

family.change_carrier family_uri #fa#f4-7_l2 new_carrier_uri #al#a4.f4_l0 

$ assert_uri_k_v | #ag#f4-7_l2_main_agora carrier $#al#a4.f4_l0@www.adelphos.it

root.push_alias alias a4.f4_l0

$ pop_msg | amsg 

$ assert | pars['amsg']['mmsg'] == "new_carrier"
$ assert | pars['amsg']['cur_boss'] == "#al#b7.f7_l0@www.adelphos.it"
$ assert | pars['amsg']['family_uri'] == "#fa#f4-7_l2@www.adelphos.it"

root.pop_alias
