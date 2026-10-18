
root.push_alias alias b0.f0_l0

family.get_details family_uri #fa#f7_l0 ==> \
	{ "errno" : 12 }

root.pop_alias


root.push_alias alias a0.f0_l0

family.get_details family_uri #fa#f7_l0 ==> \
	{ "errno" : 0 }

$ assert_val | pars['$?']['res']['in_trust_db'] ~6.98
$ assert_val | pars['$?']['res']['in_trust'] ~4.988

root.pop_alias


family.get_details family_uri #fa#f0-7_l3 ==> \
	{ "errno" : 0 }

$ assert_val | pars['$?']['res']['in_trust'] ~10.0
$ assert_val | pars['$?']['res']['in_trust_db'] ~10.0

