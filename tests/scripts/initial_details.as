
root.push_alias alias b0.f0_l0

family.get_details family_uri #fa#f7_l0 ==> \
	{ "errno" : 12 }

root.pop_alias


root.push_alias alias a0.f0_l0

family.get_details family_uri #fa#f7_l0 ==> \
	{ "errno" : 0 }

$ assert | pars['$?']['res']['in_trust_db'] == 6.98

root.pop_alias

