---
title: Basic Concepts
layout: article

---


## Adelphos is Federated 

Adelphos is a distributed system; this means that there is _not_ a single
instance, a centralized organization that governs it, like facebook, x,
ebay or other _monolithic_ systems.

You are probably reading this documentation in the site www.adelphos.it,
but this is only the first instance of Adelphos; everyone with sufficient
skills in system deployment can deploy a private adelphos instance in a
matter of hours and be online with a modest monthly cost (adelphos can run
on a laptop without any problem, so electricity bills should not be a
problem, we are not talking about costly GPUs for graphics or mining or
learning AI).

## Adelphos is a net of instances that speaks together

Adelphos can be run standalone, in which case all the activity will be done
on one site; but the site owner can allow his instance to speak to other
instances in order to share users, goods and services.

The way in which the adelphos instances speak together is using the
Activity Pub protocol; in this way adelphos is another application in the
Fediverse (the set of all the applications the speak the Activity Pub
protocol)

## Adelphos and Activity Pub

Adelphos, though, uses the AP protocol in a peculiar way, mostly as a
secure way to exchange messages between instances and users.

Each Adelphos instances runs a Fediverse account named @adelphos@host (in
AP the initial @ is used as a way to distinguish it from a normal mail
address). This adelphos account is responsible to

    * Send messages to other adelphos accounts (daemons) in order to
      synchronize data and tasks

    * Send messages to normal human users to notify them of activity in
      their account

## The fractal nature of adelphos


