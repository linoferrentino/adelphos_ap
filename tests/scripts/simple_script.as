# Test for creating family trees.

root.add_user user bob
root.add_user user alice

root.add_user user alice ==> { "errno" : 2, "res_re" : "alice" }

root.add_alias alias bob.fam_bob user bob password bob_pass

root.add_alias alias alice.fam_bob user alice password alice_pass ==> \
	{ "errno" : 1, "res_re" : "fam_bob already present" }

