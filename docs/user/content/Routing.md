---

title: Routing
layout: article

aside:
  toc: true

sidebar:
  nav: docs-en

---


### The up-down routing in adelphos

In this article we will explain more in detail the current
routing in adelphos.

Given that only families of level n-1 can join families of level
n, we have that the following statement holds:

In adelphos two families of level zero have at most one top
family in common, we call it the _vertex_ family, and, in the
case of the presence of the vertex family, the number of
_up-steps_ is equal to the number of _down-steps_.

As the object is found in the upper _agora_ or not, the fact that
a user in a family can see an object is the proof that the vertex
is reachable, otherwise we would not see it.


### The routing.

So, in this first version, to route an object from family A to
family B first of all adelphos takes the vertex family.

From the vertex family it builds two chains, the chain of
exports and the chain of imports.

The two chains have equal length (because we have constrained the
members of each family to store only families of exactly one
level lower) and they determine the final price of the object.

At each step, in fact, the price is multiplied by the
import/export tax.

The exporting families will share the gains, instead the
importing families will share the losses (but they will acquire
the import tax!).


### The distribution of gain/losses


The distribution of gain/losses follows the same fractal
(recursive) method of the routing. Let's start from the simplest
case and then we complicate things.

#### Level zero

The level zero is a bit useless, but nevertheless important.
Julie and Jane are in the same level zero family. Julie wants to
buy an object from Jane.

But they are in the same family, the brotherhood is one, $ \beta = 1 $,
so all the gains and losses are shared, so there is not really a
transaction. Jane simply gives the object to Julie. End of the
story.

Well, it is a trivial example because in a _l0_ family we do not
have really transactions. Do we? We trust each other endlessly.

#### Level one

This is the first example in which there is a real transaction.
In this example we have two _l0_ families which are associated to
a level one _l1_ family.

We will call them _fam_0_0_, _fam_0_1_ (the two _l0_ families)
and the containing family is _fam_1_0_

This is the same example used in the tutorial, so that the
interested reader could follow the tutorial to check the
computations.

In the tutorial the user pat put an ad for a pokemon card in her
family, of price 1.99.

The user john finds the pokemon, but it has a price of 2.0298.

The price is greater than 1.99 because adelphos imposes on us the
tax, which by default is 1.02, so we have 
$ expPrice = 1.02 \times 1.99 = 2.0298 $

When john buys the pokemon card, adelphos does this; first of all
the pokemon card is exported in the vertex family, _fam_1_0_.
After that the object is _imported_ in the destination family,
_fam_0_0_, this is another step, so the price grows up another
bit.


$ finalPrice = 1.02 \times 2.0298 = 2.070396 $

The change of the balance for the three families involved is:

    #fa#fam_1_0@www.adelphos.it': 0.08039599999999991
    #fa#fam_0_0@www.adelphos.it': -2.0703959999999997
    #fa#fam_0_1@www.adelphos.it': 1.9899999999999998     

We can see that in this level zero example there is only one
family that has a negative delta, the family that has actually
bought the pokemon card.

The containing family _fam_1_0_ gets two times the tax, one time
going up (export) and one time going down, (import).


#### Level two

In the transaction in which the vertex family is of level one we
do not use the brotherhood ratio, because the first transaction
is total.

Let's see the difference when we have a pyramid of three steps.

This is the situation, the chain of exports.

    fam_0_0 -> fam_1_0 -> fam_2_0

And then the chain of imports

    fam_2_0 -> fam_1_1 -> fam_0_1


At the end the object will pass from family fam_0_0 to fam_0_1

The computations are these, let's start from the price in the
origin family. Let's say that the initial price is 2.35, and that
the tax of all the families is 1.02

The price in the vertex family is

$ vertexPrice = 2.35 \times 1.02^2 = 2.44494 $

Now the distribution of the losses and the gains goes backwards
from the $ vertexPrice $ downwards. 

#### first of all the losses

In the losses we have to raise the price, because also the import
has a cost!

As in the level one the first step does not involve the
brotherhood ratio, but only the tax.

In the import chain the delta are negative, they are losses, but
the taxes are always positive!

So the vertexFamily importing the object will get a gain of:

$ vertexTax = ( vertexPrice \times 1.02) - vertexPrice = (-2.44494 \times 1.02) - (-2.44494) = 0.0488988 $

Now we have to pass the loss to level zero.

The price now has become:

$ levelOnePriceImport = vertexPrice + importTax \\
= -2.44494 - 0.0488988 = -2.4938388 $

So we have now to distribute this loss to the level one, but in
this case the level is not zero, so we take into consideration
the $ \beta $, the brotherhood ratio.

First of all we give to level one its gain (the import tax)

$ curLevelTax = ( upperDelta \times curTaxRatio ) - vertexPrice = (-2.4938388 \times 1.02) - (-2.4938388) = 0.049876776 $

And the current price in level one is

$ curDelta = upperDelta - curLevelTax = -2.4938388 - 0.049876776 = -2.543715576 $


In the level one the $ \beta $ starts with a value of $ 0.618 $,
so we divide the loss using this ratio

$ sharedDelta = upperDelta \times \beta = -2.543715576 \times 0.618 = -1.572016225968 $

And the family that does the transaction will incur a loss of

$ inferiorDelta = upperDelta - sharedDelta = -2.543715576 -
(-1.572016225968) = 0.97169935003 $

You can see that actually the level one family will get 60% of
the losses!

Then, if we go one level down we reach level zero and here the
recursion stops. The ultimate family will get all the delta.

So, at the end, this is the import chain of losses:

    lev 2: 0.04889879999999991
    lev 1: -1.5221394499679999
    lev 0: -0.9716993500319999                                                                                               

As you can see the level 2 family gets the import tax without any
other loss, but the level one family gets the import tax, but it
has only to share some of the losses because of the brotherhood
ratio.

In this case the gain has become a loss!


#### Then the gains

The gains are routed backwards from the _vertex_ family to the
origin family of the object.

The difference is that in this case the vertexPrice has already
the export taxes, so we have to change the computation.

$ vertexTax = ( vertexPrice \div 1.02) - vertexPrice = \\
(2.44494 \div 1.02) - (2.44494) = 0.04794 $

This export tax is a gain for the _vertex_ family, which will sum
to the import tax.

We have now a gain of

$ newDelta = vertexPrice - vertexTax = 2.44494 - 0.04794 = 2.397 $

This gain will go fully to the level one family, which gets,
again, its export tax

$ levelOneTax = ( newDelta \div 1.02 ) - newDelta = \\
(2.397 \div 1.02) - 2.397 = 0.047 $

And then we have the $ newDelta_{1} $, the price at level one
which is

$ newDelta_{1} = newDelta - levelOneTax = 2.397 - 0.047 = 2.35 $

Which is the price that the user has decided for his object.

But, when we have to pass it to the level zero we use the $ \beta $ the brotherhood ratio.

So we have to distribute 2.35 using a $ \beta = 0.618 $ 

The computation are the same as in the case of the losses

The family will get:

$ sharedGain = newDelta_{1} \times \beta = 2.35 \times 0.618 = 1.4523 $

$ personalGain = newDelta_{1} - sharedGain = 2.35 - 1.4523 = 0.8977 $

The shared gain will be added to the export tax.

So, in the end, the user wanted 2.35AC for his object, but in the
end he will receive only 0.89! This is not an error, because he
has put some of his gains in a common purse. Later, when he
decides to buy something, he can fetch money from the common
purse, just like a family member.


#### Level three and upwards

In the level three we simply do a recursion. From the _vertex_
family of level _n_ we consider the top-most import and export
families as _level_1_ (so without the brotherhood).

For the next level we treat them as level two, until we reach the
level zero which will get the all the remaining gain and loss.

