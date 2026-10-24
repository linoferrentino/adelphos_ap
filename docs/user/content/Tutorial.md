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
The message is this:



```

@banulius_daehonan You have a task ASSOCIATE_FAMILY as diakonos.

The dikastes for this task is: #al#john.fam_0_0@www.adelphos.it.

He/she will have to login to adelphos to mark it completed.

You have to wait or do it.

```


Instead John should have received a message of this kind


```
@banulius_daehonan You have a new task as dikastes: ASSOCIATE_FAMILY.

Login to adelphos to mark it completed or deny it.

The URI for this task is:

#tk#173fe7789d259c6a7934516d33d5a3f9abfc5a860b08aecd0bbaa2d88431a9ec@www.adelphos.it

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


    [{'type': 'ASSOCIATE_FAMILY', 'uri':
    '#tk#173fe7789d259c6a7934516d33d5a3f9abfc5a860b08aecd0bbaa2d88431a9ec@www.adelphos.it',
    'dikastes': '#al#john.fam_0_0@www.adelphos.it', 'diakonos':
    '#al#pat.fam_0_1@www.adelphos.it'}]

    
You can notice that the task URI is the same. You can accept the
association with this message

    task.accept_associate task_uri #tk#173fe7789d259c6a7934516d33d5a3f9abfc5a860b08aecd0bbaa2d88431a9ec@www.adelphos.it

You should receive a message: "Done"

Pat will receive a message:

    @banulius_daehonan Completed task or marked completed by the judge.

    Thank you for using adelphos.

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

    {'in_trust_db': 6.98, 'in_trust': 4.988844874600123,
    'my_trust_db': 6.989700043360188, 'my_trust': 5.000000000000001,
    'import_export_tax': 1.02, 'balance': 0.0, 'pending_balance':
    0.0, 'level': 1, 'brotherhood_ratio': 0.6180339887536743}

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

If you type now

    agora.find_first_object_title uplevel 0 ob_title pokemon

you will get

    ({'price': 1.99, 'uri': '#ob#1_fam_0_1@www.adelphos.it',
'title': 'a pokemon card', 'description': 'pikachu'},)


## find an ad.

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
trust,  

Now let's buy the pokemon card, in the chat type


    agora.buy_object_uri ob_uri #ob#1_fam_0_1@www.adelphos.it


You will get "Done".

### The routing.

In this example, very simple, we have only two users and one
common agora. In this case adelphos has created a very simple
routing of the object.

If you look at the Mastondon inbox, Pat will have receive a
message that says this:





    

    
