
root.push_alias alias a7.f7_l0

agora.find_first_object_title uplevel 0 ob_title spiderman

root.pop_alias

root.push_alias alias a6.f6_l0

agora.find_first_object_title uplevel 0 ob_title spiderman ==>  \
	{ "errno" : 19 }

agora.find_first_object_title uplevel 1 ob_title spiderman

root.pop_alias

root.push_alias alias a5.f5_l0

agora.find_first_object_title uplevel 0 ob_title spiderman ==>  \
	{ "errno" : 19 }

agora.find_first_object_title uplevel 1 ob_title spiderman ==>  \
	{ "errno" : 19 }

agora.find_first_object_title uplevel 2 ob_title spiderman

root.pop_alias

root.push_alias alias a3.f3_l0

agora.find_first_object_title uplevel 0 ob_title spiderman ==>  \
	{ "errno" : 19 }

agora.find_first_object_title uplevel 1 ob_title spiderman ==>  \
	{ "errno" : 19 }

agora.find_first_object_title uplevel 2 ob_title spiderman ==>  \
	{ "errno" : 19 }

agora.find_first_object_title uplevel 3 ob_title spiderman 

root.pop_alias
