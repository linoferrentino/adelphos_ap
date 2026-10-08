family.detach_upper family_uri #fa#f0-1_l1  ==> \
	{ "errno" : 36 }

family.detach_upper family_uri #fa#f0_l0  ==> \
	{ "errno" : 14 }

family.detach_upper family_uri #fa#f1_l0  

root.do_join containing_family #fa#f0-1_l1 inner_family #fa#f1_l0

root.do_join containing_family #fa#f0-1_l1 inner_family #fa#f1_l0 ==> \
	{ "errno" : 16 }
	
