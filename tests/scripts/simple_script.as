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

