
root.push_alias alias b7.f7_l0

family.change_tax family_uri #fa#f7_l0 new_tax 1.10 ==> \
	{ "errno" : 12 }

root.pop_alias

root.push_alias alias a7.f7_l0

family.change_tax family_uri #fa#f7_l0 new_tax 0.10 ==> \
	{ "errno" : 21 }

family.change_tax family_uri #fa#f7_l0 new_tax 1.10 

root.pop_alias

$ assert_uri_k_v | #fa#f7_l0 import_export_tax ~1.10

family.change_tax family_uri #fa#f7_l0 new_tax 1.09

$ assert_uri_k_v | #fa#f7_l0 import_export_tax ~1.09

root.push_alias alias a7.f7_l0

agora.find_first_object_title uplevel 0 ob_title lego

$ exec | pars['lego_uri'] = pars['$?']['res'][0]['uri']

root.pop_alias

root.buy_object_uri as_adelphos a3.f3_l0 ob_uri {lego_uri} \
	hearts 5 ==> { "errno" : 0 }

$ assert_uri_k_v | #fa#f7_l0 balance ~4.216
$ assert_uri_k_v | #fa#f3_l0 balance ~-1.673

