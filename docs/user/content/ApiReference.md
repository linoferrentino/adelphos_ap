---

title: Api Reference
layout: article

aside:
  toc: true

sidebar:
  nav: docs-en

---

### List of current system calls of adelphos

Currently adelphos has three main gateways from which it receives
commands:

    * the ActivityPub daemon

    * the Cli interface (the web socket)

    * the RPC internal tunnel encapsulated in ActivityPub

The last one is used only between adelphos instances and it will
not be documented here (it is important only for developers of
adelphos), but it is nevertheless mentioned here because it uses
the same interface of the daemon.

### The Activity Pub Daemon

There is only one system call called by a human user in this
channel, it is the alias.create.


### The Cli interface

The Cli interface is divided in contexts. Each system call is in
the form

    $context.$call [$param $value...]

Here we list the calls grouping them by context.

    #### Task context


#### Object context


#### Agora context


#### Family context


#### Alias context

#### Root context



### Social RPC context
