
family.expel_member family_uri #fa#f0-7_l3 member_to_expel #fa#f0-3_l2 ==> \
	{ "errno" : 14 }

family.expel_member family_uri #fa#f0-7_l3 member_to_expel #fa#f4-7_l2

root.do_join containing_family #fa#f0-7_l3 inner_family #fa#f4-7_l2

root.push_alias alias b0.f0_l0

family.expel_member family_uri #fa#f0-7_l3 member_to_expel #fa#f0-3_l2 ==> \
	{ "errno" : 12 }

root.pop_alias

root.push_alias alias a0.f0_l0

family.expel_member family_uri #fa#f0-7_l3 member_to_expel #fa#f0-3_l2 ==> \
	{ "errno" : 14 }

family.expel_member family_uri #fa#f0-7_l3 member_to_expel #fa#f4-7_l2

root.pop_alias

root.do_join containing_family #fa#f0-7_l3 inner_family #fa#f4-7_l2

