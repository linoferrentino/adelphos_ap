---
title: Basic Concepts
layout: article

---

## Trust and credit.

### The AdelphosCoin

Let's return to the example of the library book; that example worked
because there was trust between the participants and there was no
money involved in the overall transaction.

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
the phone to her brother Bob, maybe she does not want to be payed,
because maybe later in time she will need Bob's help to configure her
laptop, for example, or to repair her scooter.


### The logarithmic nature of the trust.

So, Alice trusts Bob for 80€. But how about a Bob's friend? Let's
suppose that Bob has a friend, Carol, that would like to buy Alice's
phone. Will Alice give to her 80€ in credit? Probably not.

But how much? 60? 40? The problem is that escaping the circle of the
family trust drops sharply, that is why usually these currencies based
on credit are not widely adopted.

My impression is that trust is logarithmic in scale, not linear. In
physics logarithmic scales are used for example for sounds, and are
called deciBel. A decibel is actually a quantity obtained from a value
Q using this formula

    q decibel = 10 * log ( Q / Q0 )

Where Q0 is some reference value.

In this case a factor of 10x increase will translate into the addition
of 10.

Adelphos uses the same principle to measure trust.

Q0 is 1 Adelphos Coin.

So the trust of 0 Db is actually a trust of 1 Adelphos Coin

This because 10 * log ( 1 / 1 ) = 10 * log (1) = 10 * 0 = 0

A trust of 10 Db is a trust of 10 Adelphos Coin
A trust of 20 Db is a trust of 100 Adelphos Coin

And so on.






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
but they too are mathematically complex, adelphos wants to 



Yes, there are 






    










In the past there have been some tentatives to measure the trust of
a network of users: a notable example



When we talk about a simple book to return of the library our mind
does not see any problem, because the value is clear (it is a book)
and the people involved are in a clear relationship (brother, mother,
friend).



    * Would you trust to bring an object from a person you know to a
      person you know?

    * Would you trust to sell an object giving it to a friend knowing
      that it will reach destination?




So, Adelphos is able to do the routing, but how to put it into
practice? In a world where people do not trust and also real carriers
with a centralized logistic have complains, losses and delays, how to
make it work without a centralized brain and, most of all, without
real gains (not in real money, however?)

When we talked about the 



The key is based on a simple idea: trust can be measured

This is based on trust



## Expansion from the family to upper levels

## The Brotherhood

## Trust in the system and of the system in you

### The logarithmic scale of trust  



Adelphos wants to fill this lack of trust equating trust with credit,
thus we can extract another cardinal rule of adelphos.

    * In adelphos one unit of trust is equal to one unit of credit and
      the system tracks 



But to do that we need to explore better how people trust each other.


The trusts cannot be modified by the user, however; it is Adelphos
who, based on a particular algorithm, will modify them after each
successful transaction.



