
root.push_alias alias a7.f7_l0

agora.find_first_object_title uplevel 0 ob_title spiderman

root.pop_alias

root.push_alias alias a6.f6_l0

agora.find_first_object_title uplevel 0 ob_title spiderman ==>  \
	{ "errno" : 19 }

agora.find_first_object_title uplevel 1 ob_title spiderman

$ exec | pars['spiderman_uri'] = pars['$?']['res'][0]['uri']

root.pop_alias

root.buy_object_uri as_adelphos b7.f7_l0 ob_uri {spiderman_uri} \
	hearts 5 ==> { "errno" : 18 }


root.buy_object_uri as_adelphos a6.f6_l0 ob_uri {spiderman_uri} \
	hearts 5 ==> { "errno" : 0 }

$ assert_uri_k_v | #fa#f7_l0 balance ~1.99
$ assert_uri_k_v | #fa#f6_l0 balance ~-2.07
$ assert_uri_k_v | #fa#f6-7_l1 balance ~0.0804

root.push_alias alias a5.f5_l0

agora.find_first_object_title uplevel 0 ob_title pokemon ==>  \
	{ "errno" : 19 }

agora.find_first_object_title uplevel 1 ob_title pokemon ==>  \
	{ "errno" : 19 }

agora.find_first_object_title uplevel 2 ob_title pokemon 

$ exec | pars['pokemon_uri'] = pars['$?']['res'][0]['uri']

root.pop_alias

root.buy_object_uri as_adelphos a5.f5_l0 ob_uri {pokemon_uri} \
	hearts 5 ==> { "errno" : 0 }

$ assert_uri_k_v | #fa#f7_l0 balance ~2.86
$ assert_uri_k_v | #fa#f5_l0 balance ~-0.9716993500319999

root.push_alias alias a3.f3_l0

agora.find_first_object_title uplevel 0 ob_title "hello kitty" ==>  \
	{ "errno" : 19 }

agora.find_first_object_title uplevel 1 ob_title "hello kitty" ==>  \
	{ "errno" : 19 }

agora.find_first_object_title uplevel 2 ob_title "hello kitty" ==>  \
	{ "errno" : 19 }

agora.find_first_object_title uplevel 3 ob_title "hello kitty"

$ exec | pars['hello_kitty_uri'] = pars['$?']['res'][0]['uri']

root.pop_alias

root.buy_object_uri as_adelphos a3.f3_l0 ob_uri {hello_kitty_uri} \
	hearts 5 ==> { "errno" : 0 }


$ assert_uri_k_v | #fa#f7_l0 balance ~3.59
