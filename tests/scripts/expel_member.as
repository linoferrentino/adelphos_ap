
family.expel_member family_uri #fa#f1_l0 member_to_expel #al#c1.f1_l0 ==> \
	{ "errno" : 34 }

family.expel_member family_uri #fa#f0_l0 \
	member_to_expel #al#c1.f1_l0 \
	new_family f1_l0_bis ==> \
        { "errno" : 9998 , \
	"res_re" : "Federated Db error #43#" }

