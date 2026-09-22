# Test for creating family trees.

root.add_user user bob
root.add_user user alice

root.add_user user alice ==> { "errno" : 2, "res_re" : "alice" }

root.add_alias alias bob.fam_bob user bob password bob_pass \
	location "Milan, via Petrarca 12"

root.add_alias alias alice.fam_bob user alice password alice_pass \
	location "Milan, via Petrarca 12" ==> \
	{ "errno" : 1, "res_re" : "fam_bob already present" }

root.alias_join_family alias alice family fam_bob user \
	alice password alice_pass ==> { "errno" : 0, \
	"res_re" : "Created alias #al#alice.fam_bob@www.adelphos.it" }

root.alias_join_family alias alice family fam_bob user \
	alice password alice_pass ==> { "errno" : 23, \
	"res_re" : "alias alice already present" }

root.add_user user john
root.add_user user mary

root.add_alias alias john.smith user john password jpass \
	location 'Milan, via Mazzini 55'

root.alias_join_family alias mary family smith user mary password mpass

root.do_association family_source #fa#fam_bob@www.adelphos.it \
	family_dest #fa#smith@www.adelphos.it \
	upper_name wall_street_family \
	location "Wall Street 5th" 

root.put_object as_adelphos #al#john.smith@www.adelphos.it \
title 'Joyce Ulysses' \
description 'used in good condition' price 4.32

root.put_object as_adelphos #al#john.smith@www.adelphos.it \
title 'iPhone 14' \
description 'battery low' price 232.35

root.buy_object_title as_adelphos mary.smith \
uplevel 0 ad_title Joyce hearts_given 5 ==> \
	{ "errno" : 18 }

root.add_user user jack
root.add_alias alias jack_al.morrison user jack password jpass \
	location 'Siena, via Dante 3'

root.put_object as_adelphos #al#jack_al.morrison@www.adelphos.it \
title 'bluetooth speaker' \
description 'red and working perfectly' price 11.99


root.put_object as_adelphos #al#jack_al.morrison@www.adelphos.it \
title 'a spiderman mug' \
description 'for children' price 3.25

root.push_alias alias jack_al.morrison

agora.list_ads uplevel 0 ==> { "errno" : 0, \
	"eval_exp" : "(len(res_ob['res']) == 2)" \
}

root.pop_alias

root.buy_object_title as_adelphos jack_al.morrison \
uplevel 2 ad_title Joyce hearts_given 5  ==> \
	{ "errno" : 14 }

root.buy_object_title as_adelphos bob.fam_bob \
uplevel 1 ad_title Joyce hearts_given 5 

root.clear_cache

root.buy_object_title as_adelphos bob.fam_bob \
uplevel 1 ad_title iPhone hearts_given 5  ==> \
	{ "errno" : 19 }

root.do_association family_source #fa#fam_bob@www.adelphos.it \
	family_dest #fa#morrison@www.adelphos.it \
	upper_name second_level \
	location "Central Park"  ==> { "errno" : 16 }

root.do_association family_source #fa#wall_street_family@www.adelphos.it \
	family_dest #fa#morrison@www.adelphos.it \
	upper_name second_level \
	location "Central Park" ==> { "errno" : 15 }

root.add_user user maria
root.add_alias alias maria_al.rossi user maria password mpass \
	location 'Pisa, via Manzoni 33'

root.do_association family_source #fa#morrison@www.adelphos.it \
	family_dest #fa#rossi@www.adelphos.it \
	upper_name tuscany \
	location "Pisa, via Manzoni 33"

root.push_alias alias maria_al.rossi

agora.list_ads uplevel 0 ==> { "errno" : 0, \
	"eval_exp" : "len(res_ob['res']) == 0" \
}

agora.list_ads uplevel 1 ==> { "errno" : 0, \
	"eval_exp" : "len(res_ob['res']) == 1" \
}

root.pop_alias


root.do_association family_source #fa#tuscany@www.adelphos.it \
	family_dest #fa#wall_street_family@www.adelphos.it \
	upper_name america_tuscany \
	location "Florence, via Verdi 1"

root.push_alias alias maria_al.rossi

agora.list_ads uplevel 2 ==> { "errno" : 0, \
	"eval_exp" : "len(res_ob['res']) == 1" \
}

root.pop_alias

root.put_object as_adelphos #al#john.smith@www.adelphos.it \
title 'Ms. Dalloway' \
description 'used in good condition' price 1.51

root.put_object as_adelphos #al#john.smith@www.adelphos.it \
title 'Misery' \
description 'a bit scratched, missing two pages' price 4.88 

root.push_alias alias maria_al.rossi

agora.list_ads uplevel 2 ==> { "errno" : 0, \
	"eval_exp" : "len(res_ob['res']) == 1" \
}

root.pop_alias

root.clear_cache

root.push_alias alias maria_al.rossi

agora.list_ads uplevel 1 ==> { "errno" : 0, \
	"eval_exp" : "len(res_ob['res']) == 1" \
}

agora.list_ads uplevel 2 ==> { "errno" : 0, \
	"eval_exp" : "len(res_ob['res']) == 3" \
}

agora.buy_object_title uplevel 2 ad_title Dalloway 


root.pop_alias

root.push_alias alias john.smith

$ pop_msg | jmsg

$ assert | re.search('SHIP_OBJECT', pars['jmsg']['hmsg']) is not None

$ exec | pars['jtask_uri'] = pars['jmsg']['task_uri']

$ exec | pars['jtask_pin'] = pars['jmsg']['active_step']['data']['pin_to_give']

root.pop_alias

root.push_alias alias maria_al.rossi

agora.buy_object_title uplevel 2 ad_title Misery ==> \
	{ "errno" : 20 }

task.give_hearts hearts 9 task_uri task_uri ==> \
	{ "errno" : 21 }

task.give_hearts hearts 3 task_uri inexistent ==> \
	{ "errno" : 26 }

root.pop_alias

root.push_alias alias john.smith

task.first_step task_uri {jtask_uri} ==> \
	{ "errno" : 26 }

root.pop_alias

root.push_alias alias bob.fam_bob

$ pop_msg | bmsg

$ exec | pars['btask_pin'] = pars['bmsg']['active_step']['data']['pin_to_give']

$ assert | pars['btask_pin'] == pars['jtask_pin']

root.pop_alias
