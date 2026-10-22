---
title: Basic Concepts
layout: article

aside:
  toc: true

sidebar:
  nav: docs-en

---

## Introduction

Here we will present the basic concepts of adelphos without going
too much in detail, just to highlight the key concepts that make
it different from other similar systems.

The interested reader can find more details in the linked pages.


## Money

In adelphos users exchange goods and services using a virtual
currency based on trust and credit called AdelphosCoin AC which
is not convertible to any real currency. See [Adelphos
Coin](AdelphosCoin) for details.


## Trust and credit

In adelphos each user issues some money in exchange for a good,
there is no central mint, nor a private _mining_ like in
cryptocurrencies.

The system, however, limits the amount of credit / debit that
each user can get / can give.






## Trust and credit.

### The AdelphosCoin


Let's return to the example of the library book; that example worked
because there was trust between the participants and there was no
money involved in the overall transaction.

But in real life?

    * Would you trust to bring an object from a person you know to a
      person you know?

    * Would you trust to sell an object giving it to a friend knowing
      that it will reach destination?

So, Adelphos is able to do the routing, but how to put it into
practice? In a world where people do not trust and also real carriers
with a centralized logistic have complains, losses and delays, how to
make it work without a centralized brain and, most of all, without
real gains (not in real money, however?)


With money things become complex because the transaction can happen if
the seller can receive something concrete in exchange. 

Let's think about a used phone, for example. Alice wants to sell a
used phone and she wants 80€ from it.

In the "usual" way Alice puts an ad in one of the sites that allow
users to put ads; there are many of them, there is also a version in
the fediverse, called flohmarket.

Bob sees the ad, the price and the shipping cost, let's say 5.00€. He
thinks that this is a deal, he contacts Alice, sends her the money and
the shipping address. Alice does the packaging and sends it.

Eventually Bob receives it and, in some platforms, can leave a
feedback to Alice.

This works because Alice and Bob agree on the nature and value of
money and Alice knows that she can use those 80€ for something else,
also outside the exchange platform.

But Adelphos is different. It wants to create a different
economy, based on trust and credit, not using centralized currencies
based on debt issued by Central Banks.

But experiments like this have not had too much success; I think that
the main obstacle to a widespread adoption of a virtual currency is
the lack of trust and the fact that they rely on an external entity to
do the routing.

But the main obstacle is trust.

Suppose that Alice agrees to use Adelphos and puts the ad into it,
Adelphos uses an internal currency, called AdelphosCoin (AC), she puts
the ad and puts the price 80AC.

(For now we have used the simple equation 1AC = 1€, but this is not
fixed, you can see in [Adelphos Coin](content/AdelphosCoin) some more
details about the relationship between AC and the real world
currency.)

Alice puts the ad in Adelphos if she trusts that:

    * she can spend later the 80AC into something else

Adelphos gives the used phone to Bob if it trusts that:

    * he will later contribute to the community by putting into the
      system something of equal value.

From this simple example we see that trust is bidirectional, from the
user to the system (the user trusts the system to have something back
for that amount of AdelphosCoin) and from the system to the user; the
system, in the form of the overall set of users, trusts the user that
he will repay the system (not Alice in particular) by giving something
back. 

Adelphos models this scenario dividing the trust in two ways: trust
from the system (in-trust) and trust to the system (out-trust).  Both
trusts are independently updated and govern the overall behavior of
the system.

But how can a computer measure an aleatory value like trust which,
like love and friendship, escapes a formal definition?  Computers do
not have friends, they need an algorithm, clear data to compute, we
just cannot tell a PC ``Alice trusts Bob'', we need to tell it ``how
much Alice trusts Bob?''.

Let's return to the phone example, because the key is in the credit.

Alice maybe does not trust adelphos for 80€/AC (given the equivalence
1€=1AC), at least initially, but suppose that she has a used book that
she does not use any more. The book has not any real value, maybe 1 or
2€. Probably she will trust to sell it to adelphos, because the risk
is less.

We can say that the trust of Alice is a number between 2 and 80.

It also depends on the person to whom Alice is selling. If she gives
the phone to her brother Bob, maybe she does not want to be paid,
because maybe later in time she will need Bob's help to configure her
laptop, for example, or to repair her scooter.


### The logarithmic nature of the trust.

So, Alice trusts Bob for 80€. But how about a Bob's friend? Let's
suppose that Bob has a friend, Carol, that would like to buy Alice's
phone. Will Alice give to her 80€ in credit? Probably not.

But how much? 60? 40? The problem is that escaping the circle of the
family trust drops sharply, that is why usually these currencies based
on credit are not widely adopted.

Yes, of course, there are fuzzy system, AI agents, etc..., but from
the start I wanted to create a system that could run on a very simple
laptop, with only 4 Giga of Ram, no graphic card, to be able to run it
on a solar panel also in a remote area with an unstable internet
connection. Current AI systems are very hungry on system resources
and/or memory.

Adelphos is a system that wants to help to expand the trust of users,
but to do that we need to *measure* trust because computer do
understand only computable things (even the current AI systems
transform the language into numbers called tokens, but this is another
story...).

There have been in the past some experiments to create a web of trust,
but they too are mathematically complex; the simple idea that I had in
designing the trust computation in adelphos is to note exactly how
trust feels in real life.

It is very high in the family and drops sharply; it is still high for
first order friends, maybe not so much for second link friends
(friends of friends) and then rapidly goes to zero.

-------

Suppose a simple example: would you accept a friend to sleep on your
couch? Alice is one of your greatest friend, she happens to pass by
wants to sleep one night at your place. You probably will say yes, and
you could be happy too for the visit.

A friend of friend? You know Alice very well. Alice asks you a bed for
her friend Julie. You DO NOT know Julie... would you accept her? Maybe
yes, maybe not.

A friend of a friend of a friend? Probably no. Unless you plan to be
paid for it. In that case the absence of trust is compensated by the
promise to gain some money.

------

This simple example shows that trust is logarithmic in scale, not
linear. In physics logarithmic scales are used for example for sounds,
and are called deciBel. A decibel is actually a quantity obtained from
a value Q using this formula

$ q_{db}  = 10 \log ( \frac{Q}{Q_{0}} ) $

Where $ Q_{0} $ is some reference value.

In this case a factor of 10x increase will translate into the addition
of 10.

Adelphos uses the same principle to measure trust.

$ Q_{0} $ is 1 Adelphos Coin. 

So the trust of $ 0_{Db} $ is actually a trust of 1 Adelphos Coin

This because $ 10 * \log ( \frac{1}{1} ) = 10 \log (1) = 10 * 0 = 0 $

A trust of 10 Db is a trust of 10 Adelphos Coin

A trust of 20 Db is a trust of 100 Adelphos Coin

And so on.

### In-trust and out-trust

We have talked earlier about the dual nature of trust; the trust from
adelphos to the user and from the user to adelphos. 

In this paragraph we will define them better.

In the previous paragraph we have equated trust with credit, and in
adelphos the trust limits the amount of credit / debit that a family
can have.

#### Out trust

The **out-trust** is the simplest of the two: this, in fact, is
usually the *normal* way in which we feel it: we *feel* the amount of
trust we put in one person not that trust that the person puts in
adelphos.

In a certain sense the out-trust is not really needed; if one person
wants to sell an object of value without any money he should be free
of doing it. But adelphos enforces it because it wants to exclude
possible disappointments.

Adelphos wants that the users build slowly trust into the system and
be loyal to it, instead of having a user that starts with a high
trust, and feels robbed after.

#### In trust

The **in-trust** is the opposite: it is the trust of the system in us,
so it limits the amount of things we can buy without selling anything.

The in trust should forbid the behaviour of a person who login into
adelphos and starts to buy things without anything in return dropping
in debt.

#### The limits and the trust.

The main rules of adelphos that link trust with credit are:

The **out-trust** limits the **credit**

The **in-trust** limits the **debit**

Every actor in adelphos has a balance, we start from level zero.


### The change of trust in adelphos.


The trusts cannot be modified by the user, however; it is Adelphos
who, based on a particular algorithm, will modify them after each
successful transaction.

We will talk about this later when we talk about the commerce of goods
and services and the feedback mechanism see
[here](contents/RulesOfCommerce)


## The Brotherhood

Adelphos wants to expand the mechanism of families to upper levels, to
families of families and so on.

One of the key concepts of a family is the brotherhood; well, this is
in some way a definition of the family: we distinguish friends from
members of our family just because we *feel* that members of our
family are *closer* than friends.

Closer in what sense?

We do not want to go down in the physical and emotional sense, but we
remain on a material part; husband and wife, also for the civil law,
need to love each other, be loyal, but, above all, to contribute
together to the **common good**.

The **common good** of the family is one of the greatest values of a
family, each member is free to pursue his/her interests, hobbies and
inspirations but should do all work with the common good of the family
in mind.

Adelphos limits to model this aspect of the family, which is important
and can be summarized as follows: **in adelphos members of the same
family share gains and losses**.

This seems obvious in level zero, in a certain sense it is obvious
that husband and wife share the same account, but adelphos is fractal
in nature, so it tries to put the rules of the family also to upper
levels, this means that **also in upper levels there is a sharing of
gains and losses**.

But we have to be practical: even in a _normal_ family there are
personal goods which are private for the husband and a wife, so also
adelphos remains to a practical level.

Adelphos defines a brotherhood constant called Beta $ \beta $, which
defines the ratio of the gain that the family distribute to other
members and the gain that goes to the seller.

Yes, in adelphos when you sell an object for 50 AC, for example, it is
not true that you will receive 50 AC, you will likely receive
less because a part of your gains goes to other families, maybe also
to people you do not know.

But this is also contrary! If you have 10 AC in your balance, you
might buy an object for 20 AC or more (it depends on the topology of
the network and by other characteristics) because people you might not
know put their credit to help you buy.




