---
title: Rules of commerce
layout: article

aside:
  toc: true

sidebar:
  nav: docs-en

---

### Shared Gain and losses

Adelphos tries to mimic the mechanism of a family at a larger
level.

Family in real life share gains and losses, so families in
adelphos share gains and losses too and families at higher levels
share gains and losses too.

This is the exact opposite of a "Ponzi scheme" in which the
people at the top collect gains from the bottom and do not share
them.

But let's make an example.

In real life if you want to buy a thing and you do not have the
money for it, you might take some money from the _common purse_
of the family, a common account.

At the same time, if you sell and object, you might put the
gained money in part in your pocket for personal expenses, but
you might put a part of it in the _common purse_ of the family to
be used by others.

The same happens in adelphos: every family has a _common purse_
which is used automatically by the system to collect payments and
to share gains.


### How gains and losses are shared.

In the [routing](Routing) page we have defined the current
routing algorithm in adelphos.



### Change of trust based on a trade

In the [Basic Concepts](BasicConcepts) page we have already seen
that adelphos is able to limit the transactions. It limits the
amount of debt or credit that a family can have, but these limits
are not fixed.

Adelphos changes the trust limits based on the feedbacks (the
hearts) that the receiving user gives to the seller.

In the current version of adelphos the change is defined as this:

$ \Delta_{trust_{db}} = -0.03 + ( 0.01 * hearts) $  with $ hearts \in [ 0..5] $

This means that trust changes at most of $ 0.05 \pm trust_{db} $
for every trade.

Trust raises if the hearts are between three and five and shrinks
if between zero and two.


### The brotherhood constant

The brotherhood constant starts with a value which depends on a
level; its values is defined as this: $ \beta = \phi^{-lev} $
where $ \phi \approxeq 1.168 $ the Golden Ratio constant.

This means that the family of level zero has $ \beta = 1 $, level
one has $ \beta \approxeq 0.618 $ and so on...

When we give hearts after a trade the brotherhood constant
changes for the vertex family (the family at the top most level
see [routing](Routing) for the details).

But, as $ \beta $ is constrained in the interval $ [0..1] its
change is different from the trust (which is unbound), and it is
this:

$ \Delta_{\beta} = \left\\{ \begin{array}{rcl} - 0.01 * ( 3 - hearts) ) * \beta & \mbox{for} & hearts \in [0..2] \\\\ 0.01 * (hearts - 2) ) * (1.0 - \beta) & \mbox{for} & hearts \in [3..5] \end{array} \right. $


You can see that in this way the $ \beta $ is constrained in the
interval $ ( 0 .. 1 ) $ as the corrections are smaller and
smaller as $ \beta $ goes towards the limits of the interval.




