---

title: Tutorial
layout: article

aside:
  toc: true

sidebar:
  nav: docs-en

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

    family.associate family_dest #fa#fam_0_0 upper_name fam_1_0

You should receive a message in the chat: "Done" 

You should also have received a message in your mastodon inbox.
The message is like this (of course the real alias and the task URI will change)



```

@dafrissia_atdred Hello #al#pat.fam_0_1@www.adelphos.it,

this is adelphos, you have a new task as diakonos:

Your request to associate the family governed by #al#john.fam_0_0@www.adelphos.it,

to create the new family fam_1_0 has been accepted.

The dikastes for this task is

#al#john.fam_0_0@www.adelphos.it.

He/she will have to login to adelphos to mark it completed.

You have to wait or do it.

The URI for this task is:

#tk#d0eb4f1bb1153482830cf794714129654722419d441b58fc70047acabde408f5@www.adelphos.it


```


Instead John should have received a message of this kind


```

@dafrissia_atdred Hello #al#john.fam_0_0@www.adelphos.it,

this is adelphos, you are dikastes (Judge) for a new task:

You have receive an invite from #al#pat.fam_0_1@www.adelphos.it to associate

with his family to create a new family of name fam_1_0

You have received this invite because you are the boss of the

family.

Login to adelphos to mark it completed or cancel it.

The URI for this task is:

#tk#d0eb4f1bb1153482830cf794714129654722419d441b58fc70047acabde408f5@www.adelphos.it



```

In adelphos each task has a _διάκονος_ (diakonos, a doer, servant
in ancient Greek) and a _δικαστής_ (dikastes, a judge, always in
ancient Greek)

Each object in adelphos has a [Federated URI](FederatedUri), an
identifier (for now you can think of it like an address).

To finalize the association john should login, (you could use the
tab that you have used in the past login, if you have saved it,
otherwise open another).

After the login you can see that you have actually a task to do
as judge. Type the following in the chat.


    alias.tasks_as_dikastes

In my example I have obtained

```

[ { '_fdb_cid': 0,

'_fdb_ref_count': 2,

'_fdb_uri': '#tk#d0eb4f1bb1153482830cf794714129654722419d441b58fc70047acabde408f5@www.adelphos.it',

'_fdb_version': 0,

'active_step': 0,

'created_on': '2026-10-26T14:22:24.004446',

'data': None,

'linked_ob': None,

'state': 0,

'steps': [ { 'completed_on': None,

'data': { 'diakonos_uri': '#al#pat.fam_0_1@www.adelphos.it',

'dikastes_uri': '#al#john.fam_0_0@www.adelphos.it',

'pars': { 'family_dest': '#fa#fam_0_0',

'family_dst_chain': [ '#fa#fam_0_0@www.adelphos.it'],

'family_source': '#fa#fam_0_1@www.adelphos.it',

'family_src_chain': [ '#fa#fam_0_1@www.adelphos.it'],

'import_export_tax': 1.02,

'upper_name': 'fam_1_0'}},

'task_step_type': 'default_state'}],

'task_type': 'ASSOCIATE_FAMILY'}]

```


    
You can notice that the task URI is the same. You can accept the
association with this message

    task.accept_associate task_uri #tk#d0eb4f1bb1153482830cf794714129654722419d441b58fc70047acabde408f5@www.adelphos.it

You should receive a message

    Done

Pat will receive a message:

```

    @banulius_daehonan Completed task or marked completed by the judge.

    Thank you for using adelphos.

```

And the task is gone. If john types

    alias.tasks_as_dikastes


You will receive an empty list []

### Get the details of the new family

This action has created a new family of level 1, this new family
has a common ἀγορά (agora, a place, market).

Every trade in adelphos happens in an agora of a certain level.

Pat is now the boss of this new family and she can get the
details. Type this in Pat's chat.

    family.get_details family_uri #fa#fam_1_0 

You will get this message


```

{ 'balance': 0.0,

'brotherhood_ratio': 0.6180339887536743,

'import_export_tax': 1.02,

'in_trust': 4.988844874600123,

'in_trust_db': 6.98,

'level': 1,

'my_trust': 5.000000000000001,

'my_trust_db': 6.989700043360188,

'pending_balance': 0.0}


```

As you can see the trust is the same but the brotherhood_ratio is
different. This is normal, see the [Basic
Concepts](BasicConcepts) page for details

### Put an ad.

In this first version adelphos is able to handle the trade of
physical objects, not of services.

We will put two ads in the Pat's agora. In Pat's chat this: 

    object.put_ad title 'a pokemon card' description 'pikachu' price 1.99

You will receive a message like this

    {'uri': '#ob#1_fam_0_1@www.adelphos.it'}

This is the URI of the new object in adelphos.

And then also this

    object.put_ad title 'man sneakers' description 'size 10' price 10.28

You will get the uri of the object.

    {'uri': '#ob#2_fam_0_1@www.adelphos.it'}


Let's put another object, just for test

    object.put_ad title 'a frying pan' description 'no stick' price 4.13

The URI will be

    {'uri': '#ob#3_fam_0_1@www.adelphos.it'}


If you type now

    agora.find_first_object_title uplevel 0 ob_title pokemon

This command means to find the first object in the agora of level 0 *your agora* the first object with "pokemon" in the title. You will get:


```

( { 'description': 'pikachu',

'price': 1.99,

'title': 'a pokemon card',

'uri': '#ob#1_fam_0_1@www.adelphos.it'},)


```


### Finding an ad.

Now login as john (or switch tab) and type

    agora.find_first_object_title uplevel 0 ob_title pokemon

You will get: 

    Adelphos core error #19#>: no object with title pokemon found

This is right, you are john and pokemon is in Pat's agora. Let's
search in a different uplevel

    agora.find_first_object_title uplevel 1 ob_title pokemon

You will get:

```

( { 'description': 'pikachu',

'price': 2.0298,

'title': 'a pokemon card',

'uri': '#ob#1_fam_0_1@www.adelphos.it'},)


```


You will see that the price is different, this because you have
to pay the import/export tax.

Try search for the sneakers:
    
    agora.find_first_object_title uplevel 1 ob_title sneakers

You will get:

    Adelphos core error #19#>: no object with title sneakers found 

This is correct, because the sneakers cost too much for your
trust.

If you try to search for the pan you will get it (try it!).
  

Now let's buy the pokemon card, in the chat type


    agora.buy_object_uri ob_uri #ob#1_fam_0_1@www.adelphos.it


You will get "Done".

### The routing.

In this example, very simple, we have only two users and one
common agora. In this case adelphos has created a very simple
routing of the object.

If you look at the Mastondon inbox, Pat will have receive a
message that says this:


```

@dafrissia_atdred Hello #al#john.fam_0_0@www.adelphos.it,

this is adelphos, you are dikastes (Judge) for a new task:

The diakonos #al#pat.fam_0_1@www.adelphos.it will give to you the object a pokemon card

and he will have to give to you the PIN 95178896.

Do NOT accept the object without the correct PIN.

Login to adelphos to mark it completed or cancel it.

The URI for this task is:

#tk#812ce0d312131602f22e8c771e6d8ae48e51254c35e6634921dbe270b3fc2c1e@www.adelphos.it


```

In this case, the receiver of the object is also the ultimate dikastes.


Pat, who has put an ad, has received the message:


```

@dafrissia_atdred Hello #al#pat.fam_0_1@www.adelphos.it,

this is adelphos, you have a new task as diakonos:

you have sold the item a pokemon card!

to #al#john.fam_0_0@www.adelphos.it, the carrier

of family #fa#fam_0_0@www.adelphos.it for the next routing leg.

You will have to give them the object and the PIN 95178896.

The dikastes for this task is

#al#john.fam_0_0@www.adelphos.it.

He/she will have to login to adelphos to mark it completed.

You have to wait or do it.

The URI for this task is:

#tk#812ce0d312131602f22e8c771e6d8ae48e51254c35e6634921dbe270b3fc2c1e@www.adelphos.it

```


Now, suppose that pam gives to john the pokemon card and the correct PIN.

John will now login to adelphos and type


    task.confirm_routing_step task_uri #tk#812ce0d312131602f22e8c771e6d8ae48e51254c35e6634921dbe270b3fc2c1e@www.adelphos.it pin 95178896

You should get "done"

Now in mastodon john has the last task, give feedback

```

@dafrissia_atdred Hello #al#john.fam_0_0@www.adelphos.it,

this is adelphos, you have a new task as diakonos:

you should have received the item a pokemon card!

Your next task is to give feeback. You can do it by issuing the following

command in adelphos CLI:

task.give_hearts hearts [number between 0 and 5] task_uri #tk#812ce0d312131602f22e8c771e6d8ae48e51254c35e6634921dbe270b3fc2c1e@www.adelphos.it

Remember that hearts from 0 to 2 are a negative feedback.

The URI for this task is:

#tk#812ce0d312131602f22e8c771e6d8ae48e51254c35e6634921dbe270b3fc2c1e@www.adelphos.it

```

Instead pat has obtained the message:

```

@dafrissia_atdred Completed task or marked completed by the judge.

Thank you for using adelphos.

```

Now let's give feedback, but first let's see the family details of the upper
family; as john type:


    family.get_details family_uri #fa#fam_1_0

You will get

```
{ 'balance': 0.08039599999999991,

'brotherhood_ratio': 0.6180339887536743,

'import_export_tax': 1.02,

'in_trust': 4.988844874600123,

'in_trust_db': 6.98,

'level': 1,

'my_trust': 5.000000000000001,

'my_trust_db': 6.989700043360188,

'pending_balance': 0.0}


```

Now, let's give five hearts, the maximum


    task.give_hearts hearts 5 task_uri #tk#812ce0d312131602f22e8c771e6d8ae48e51254c35e6634921dbe270b3fc2c1e@www.adelphos.it 

You should get Done. Now let's try to search again the details:


    family.get_details family_uri #fa#fam_1_0

you will get

```

{ 'balance': 0.08039599999999991,

'brotherhood_ratio': 0.6294929690910641,

'import_export_tax': 1.02,

'in_trust': 4.988844874600123,

'in_trust_db': 6.98,

'level': 1,

'my_trust': 5.000000000000001,

'my_trust_db': 6.989700043360188,

'pending_balance': 0.0}

```

As you can see the details are not the same, because the brotherhood_ratio has
risen a bit.

Let's see our details:


    family.get_details family_uri #fa#fam_0_0

You see:

```

{ 'balance': -2.0703959999999997,

'brotherhood_ratio': 1.0,

'import_export_tax': 1.02,

'in_trust': 5.011872336272722,

'in_trust_db': 7.0,

'level': 0,

'my_trust': 5.000000000000001,

'my_trust_db': 6.989700043360188,

'pending_balance': 0.0}


```

You see that we are in debit, because we have bought a pokemon card!

Let's try to buy also the pan...

    agora.buy_object_uri ob_uri #ob#3_fam_0_1@www.adelphos.it

The system will tell us:

```

    Adelphos core error #21#>: Transaction aborted. The family #fa#fam_0_0@www.adelphos.it cannot buy, the system has not sufficient trust in it. Its new balance would be -6.367248 but its trust allows it only to have a negative balance of -5.011872336272722


```

The system has aborted the transaction, because adelphos trusts us only for 5Adelphos Coins, but if we bought the pan our balance would go down too much.

The solution to this is of course to sell something.


## Joining in families

To complete the tutorial let's do a join action.

Join the families in adelphos can be done in two ways, depending on the level
of the family involved.

This because in level zero we have not families inside families but people, so
in level zero we invite a user in fediverse to join our family


### Ask a fediverse user to join our family

We invite a fediverse user like this


    family.invite invite_code 83823 user_handle @brautus_hundravun@activitypub.academy

We choose a invite code and we send the mention to the user using his fediverse handle.

He will receive a mention like this:


```

@brautus_hundravun

Hello @brautus_hundravun@activitypub.academy

You have invited to join adelphos by

the fediverse user @brautus_hundravun@activitypub.academy who

is known in adelphos as #al#pat.fam_0_1@www.adelphos.it.

If this seems right to you please send

a private mention to adelphos

from this account like this:

@adelphos@www.adelphos.it alias.join_family alias <your_alias> family fam_0_1 invite_code 83823 password <your password>

Please be aware that joining a family means

that you will share totally

(100%) its gain and losses.

Do it only if you trust the invite.

```

In our example we have re-used the same handle, but in your case
obviously you will use another handle.

The user can accept to join the family by choosing an alias and a
password, for example

    @adelphos@www.adelphos.it alias.join_family alias tjoin family fam_0_1 invite_code 83823 password tjoin11

In this case you can join the family choosing an alias and a
password.

You will receive a mention from adelphos like this:


    @brautus_hundravun OK, You can join family fam_0_1.

Now you can open a CLI interface and login to adelphos like this,
using the password chosen:

    alias.login alias tjoin.fam_0_1 password tjoin11

You will be asked to input the token, after that you will get:

    Login OK, welcome to adelphos, tjoin.fam_0_1.

As you can see the family is the same of _pat_, but the alias is
different.

For adelphos the alias _tjoin_ has the same credits and debits as
pat, in fact, if he asks the family details he will get the same
data as pat

    family.get_details family_uri #fa#fam_0_1

The difference is that tjoin has not the permissions to invite
anybody in the family. In fact if he tries to do it, he will get
a DENIED erro

Try to invite someone:

    family.invite invite_code 83823 user_handle @brautus_hundravun@activitypub.academy

You will get:

    Adelphos core error #12#: You are #al#tjoin.fam_0_1@www.adelphos.it not #al#pat.fam_0_1@www.adelphos.it

The error number 12 is the EDENIED error, adelphos is telling you
that you are a _normal_ user, not the boss of the family


### Join a family in our family (level one and above)


To do this create another family with mention to adelphos

    @adelphos@www.adelphos.it alias.create alias bill.bill_fam password bill99


Then, as pat, you ask bill to join your level One family like this:

    family.join containing_family #fa#fam_1_0 inner_family #fa#bill_fam

As you can see you have to give the URIs of the family involved because in
theory you could join families in different adelphos instances.

You will receive a done message, and bill has receive a Mastodon mention like
this. 

```

@brautus_hundravun Hello #al#bill.bill_fam@www.adelphos.it,

this is adelphos, you are dikastes (Judge) for a new task:

You have received an invite from #al#pat.fam_0_1@www.adelphos.it to join the family

#fa#fam_1_0

You have received this invite because you are the boss of the

family #fa#bill_fam.

Login to adelphos to mark it completed or cancel it.

The URI for this task is:

#tk#4eb11b03779b5095b1b5e5e569c28ca27a19193a4501bfb160bd3b617eea15ab@www.adelphos.it


```


So, now, we login to adelphos as bill and we can join the family.

We login and we type

    alias.tasks_as_dikastes

We will see that we have a task to confirm:

```

[ { '_fdb_cid': 0,

'_fdb_ref_count': 2,

'_fdb_uri': '#tk#4eb11b03779b5095b1b5e5e569c28ca27a19193a4501bfb160bd3b617eea15ab@www.adelphos.it',

'_fdb_version': 0,

'active_step': 0,

'created_on': '2026-10-30T09:46:11.484595',

'data': None,

'linked_ob': None,

'state': 0,

'steps': [ { 'completed_on': None,

'data': { 'diakonos_uri': '#al#pat.fam_0_1@www.adelphos.it',

'dikastes_uri': '#al#bill.bill_fam@www.adelphos.it',

'pars': { 'containing_family': '#fa#fam_1_0',

'inner_family': '#fa#bill_fam'}},

'task_step_type': 'default_state'}],

'task_type': 'JOIN_FAMILY'}]


```

We can accept the join with this command

    task.accept_join task_uri  #tk#4eb11b03779b5095b1b5e5e569c28ca27a19193a4501bfb160bd3b617eea15ab@www.adelphos.it


To confirm that we are indeed in the family we can ask for the details of the
containing family

    family.get_details family_uri #fa#fam_1_0

We can see the details, so it means that the join has succeded.






This ends the tutorial, I hope this is enough to kick start your adelphos
experience!
    
