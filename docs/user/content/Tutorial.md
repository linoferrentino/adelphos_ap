---

title: Tutorial
layout: home

aside:
  toc: true


---

## A ten-minutes tour in adelphos 


This tutorial is intended as a first guided tour to adelphos,
from zero to the sell/buy of an object.

This will not explain the theory in adelphos, for this it is
better to start from the [Basic Concepts](BasicConcepts)

This guide will give you a quick start to get a _feeling_ of what
is adelphos and how it is different from other similar systems,
with an emphasis on practice, not on theory.

A more linear guide with some theory can be found
[here](LevelZero)


### Prerequisites

As with any fediverse application to use adelphos you need to
have a Fediverse account. Adelphos relies on Mastodon as a
support to give to you a User Interface.

If you do not have a Mastodon user (or you do not want to use
yours to make this test) you can use a simulated mastodon located
[here](https://activitypub.academy/auth/sign_up).

This mastodon instance gives to you a simulated user, for example
mine is now: _@bidatus_grodrast@activitypub.academy_ (yours might
be different). If you want to have more information on fediverse
handles (the meaning of the double _@_ sign, you can look
[here](AdelphosAndActivityPub))


### First step: create a family.

The first step to enter adelphos is to start a new family, you
have to give to this family a name and you have to create a nick
in this family. For this example we use _famtut_01_ and as nick
we choose john

The family must be unique in all the host, so please attach some
random characters to the family name, otherwise the creation of
the family will fail as maybe another user has created already
the family.

Create a private mention to the adelphos daemon like this

    @adelphos@www.adelphos.it alias.create alias john.fam_0_0 password john99

You will receive a message like this

    @bidatus_grodrast Alias created, you can login, now.

If the family is already existent you will get

    @bidatus_grodrast Adelphos core error #1#>: family fam_0_0 already present in this host

In this case please pick another name for the family.

With this command you have created a family and a member in it in
adelphos which is linked to your ActivityPub handle.

### Login in adelphos

Now you can login: go [here](/api/daemon_cli). You will have a
chat like interface.

Type the following command:

    alias.login alias john.fam_0_0 password john99

(of course if you have changed the name of the family, or the
user or the password please update the command)

You should receive a message in the chat

    Login OK, check your Mastodon inbox to get the token.

Now go to Mastodon. You should have received a message like this:



```

@bidatus_grodrast Someone has entered your correct password in adelphos

If it was you, copy in the chat the last line to finalize login, otherwise

please change password immediately. DO NOT SHARE THE TOKEN with anyone.

alias.put_token tk 7QoS35ObJeuqyyAwCKvgbSdL1p0SQck5swOhDYQng1U


```

Of course your token will be different. Copy the token into the
chat (you have to copy all the line from ``alias.put_token...''
to the end of the line.)

If all goes well you will receive the message


    Login OK, welcome to adelphos, john.fam_0_0.



### Getting family details

You are now in adelphos, actually you are the boss of your family
and you can get the details of it.

Type this in the chat

    family.get_details family_uri #fa#fam_0_0  

You will receive a message like this

```

{'in_trust_db': 6.98, 'in_trust': 4.988844874600123,
'my_trust_db': 6.989700043360188, 'my_trust': 5.000000000000001,
'import_export_tax': 1.02, 'balance': 0.0, 'pending_balance':
0.0, 'level': 0, 'brotherhood_ratio': 1.0}

```

There are several fields, but the most important for now is
_balance_ which is zero. Your family has not yet done any trade.
For the other fields please refer to the [basic
concepts](BasicConcepts) page.


### Create another family

Now repeat the steps to create another family, you can use the
same Mastodon account.

    @adelphos@www.adelphos.it alias.create alias pat.fam_0_1 password pat99

(you should change the name of the family if it is already taken)

Then login (open another tab, if possible)

You can at any time know what is your current user. Just type

    alias.whoami

You will receive something like

    {'active_login': 'pat.fam_0_1'}

If you wait more then 10 minutes your session will expire and you
will get:

    Adelphos app error #3#

### Associate the two families


Now let's associate the two families. Type the following command in
the Pat's chat.

    family.associate import_export_tax 1.02 family_dest #fa#fam_0_0 upper_name fam_1_0
    

    
