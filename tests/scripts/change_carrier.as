root.push_alias alias a1.f1_l0

family.change_carrier family_uri #fa#f7_l0 new_carrier_uri #al#c2.f2_l0 \
		==> { "errno" : 12 }

family.change_carrier family_uri #fa#f1_l0 new_carrier_uri #al#c2.f2_l0 \
		==> { "errno" : 33 }

family.change_carrier family_uri #fa#f1_l0 new_carrier_uri #al#b1.f1_l0

$ assert_uri_k_v | #ag#f1_l0_main_agora carrier $#al#b1.f1_l0@www.adelphos.it

root.pop_alias


