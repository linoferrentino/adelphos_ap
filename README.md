# Adelphos AP, the fractal trust network

# Adelphos' principles:

Adelphos is a system that enables users to buy/sell goods and exchange
services in a way that does not require the use of real money. All the
exchanges are done using a currency internal in the system.

The users can form families and families can join together to form bigger
families who will share at some extent gains and losses.

The system uses the Activity Pub protocol to form a federated network of
instances that can talk together.

This document is a technical reference for developers and administrators of
an Adelphos instance. Normal user should refer to the user manual which is
published in another repository.


## Installation

Notes to install adelphos on a clean machine. Tested with Lubuntu 26.04.1

### Install uv.

Adelphos uses uv as the package manager. From the website you can run

    curl -LsSf https://astral.sh/uv/install.sh | sh

uv is installed, you will need to restart the shell to get it into your path,
or source the path, as it is printed on the terminal.

Then type

    uv sync

to get the environment.

Activate the environment

    . ./.venv/bin/activate

### Do the test

    pytest -x

You should not see any errors. Congratulations, adelphos is installed.


## Installing the documentation

The documentation is done in Jekyll which uses ruby. To install it go into the folder

    docs/user

I follow the steps on Jekyll website

    https://jekyllrb.com/docs/installation/ubuntu/

So, first of all 

    sudo apt-get install ruby-full build-essential zlib1g-dev

Then

    echo '# Install Ruby Gems to ~/gems' >> ~/.bashrc
    echo 'export GEM_HOME="$HOME/gems"' >> ~/.bashrc
    echo 'export PATH="$HOME/gems/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc

Then, lastly install jekyll and bundler

    gem install jekyll bundler

You have now the jekyll package, install the missing gems

    bundle install

and then run jekyll server as:

    bundle exec jekyll serve

The documentation is ready, you can point the browser to http://localhost:4000
to read it or copy it to your instance visible in the outside world (more on that
in the Deployment section)


## Configuring a local instance

Adelphos comes with a default configuration
adelphos_ap.prototype.yaml. You can customize it as you need. To start
you could simply copy it to the file adelphos_ap_local.yaml.

Then you can start the instance with

    python -m main.py --instance-name local

You will see something like

    INFO:     Uvicorn running on http://127.0.0.1:5000 (Press CTRL+C to quit)

If you point the browser to http://localhost:5000/api/daemon_cli you
will get the prompt of the daemon.

Try to login, type this into the chat

    alias.login alias root.admins password super_secret

(of course this works if you have not changed it!)

You should see the message

    Login OK, check your Mastodon inbox to get the token

If you have set up a local root there is not any Mastodon instance, of
course. The message is printed on the console.

    @rlocal Someone has entered your correct password in adelphos
    If it was you, copy in the chat the last line to finalize login, otherwise
    please change password immediately. DO NOT SHARE THE TOKEN with anyone.
    alias.put_token tk ZqRlJvxumSH52cnbOLN2GxrtH2x0KvSQa1lsUD8-fiw

Of course you will have a different token each time

    You can copy and paste the token to the chat and you can login.

## Deployment

To deploy an adelphos instance to the Internet, usable by other
others, there are several options. For now I have tested two options,
one essentially free and the other nearly free.

The one free uses ngrok to obtain a free domain name and a tunnel to
your adelphos instance.

The other uses nginx with a signed certificate and a Linux instance
running 24/7. Adelphos is very cheap on resources, so you can rent a
simple server with 4 Giga of RAM with as less as 5-10€ at month. A
simple domain costs about 10€/year. If you want there are also
providers that sign a certificate with no cost, and dynamic IP
providers. So in theory you can run adelphos also from your home and
a dynamic IP with the only cost of the electricity to run the laptop.

I suggest to use nginx, but you can try also with other web servers.

### ngrok deploy

You will need ngrok installed, please refer to the vendor website, I
have created a simple free-account that gives to you a free domain
name with a strange name, for example mine is

vulturelike-overturnable-idalia.ngrok-free.dev   

If you use the default configuration you will have adelphos listening
to port 5000.

So you can start ngrok simply with this command

    ngrok http 5000

And the tunnel is established, you will see something like this

Session Status                online                                                                                                                                 
Account                       lino.ferrentino@gmail.com (Plan: Free)
Version                       3.39.11
Region                        Europe (eu)
Latency                       4ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://vulturelike-overturnable-idalia.ngrok-free.dev -> http://localhost:5000

You can simply use the provided address appending '/api/daemon_cli'
and you can connect to your adelphos from the outside

For the first time ngrok will warn to you that this is a free site,
you will have to accept it.


### nginx deploy

Deploy with nginx is the _normal_ way of deploying adelphos; the
website www.adelphos.it is deployed in this way.

You will need:

    - a Linux server
    - a domain name
    - the private key and the certificate for this domain.

These are the steps, this might not be the optimal configuration, but
it works.

#### Install adelphos

Install adelphos as usual, in this case you can choose a different
port, for example 8000. In this way you could run in the same machine
either an instance under nginx and another served by ngrok on a
different port.

It is perfectly fine to have more than one adelphos instance on one
host, but of course you should at least change the port and the db
name (see the adelphos_ap.prototype.yaml file as a reference)

nginx is a complex system, but to have adelphos running you can have a
simple configuration.

I copy here my configuration, of course you will need to edit the
certificate part with your actual certificate

In my server I have created a local adelphos running on port 8000, you
will see the reverse proxy configuration here, of course you can
change the port.


```
server {
        listen 80 default_server;
        listen [::]:80 default_server;
        server_name _;
        return 301 https://$host$request_uri;
}

server {

        listen 443 ssl;
        server_name         <your domain, like www.example.com>;
        ssl_certificate     <your certificate>;
        ssl_certificate_key <path to your private key>;
        ssl_protocols       TLSv1.2 TLSv1.3;
        ssl_ciphers         HIGH:!aNULL:!MD5;

        root /var/www/html;

        # Endpoint WebFinger for ActivityPub
        location = /.well-known/webfinger {
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header Host $http_host;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_set_header Upgrade $http_upgrade;
                proxy_redirect off;
                proxy_buffering off;

                # pass the request to the inner server
                proxy_pass http://127.0.0.1:8000;
        }

        location /api/ws {

                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Prefix /api;
                proxy_read_timeout 86400;
                proxy_pass http://127.0.0.1:8000/ws;

        }

        location /api/ {

            proxy_set_header X-Real-IP $remote_addr;

            proxy_set_header Host $http_host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Upgrade $http_upgrade;
            proxy_redirect off;
            proxy_buffering off;
            proxy_set_header X-Forwarded-Prefix /api;

            proxy_pass http://127.0.0.1:8000/;

        }


        location / {
                charset utf-8;
                try_files $uri $uri.html $uri/ =404;
        }

}        


'''

Edit this file to suit your needs, put it into
/etc/nginx/sites-available and restart nginx. It should work.

The explanation of this file is this.

The important thing to note is that there are three fixed endpoints
(the location in nginx terms) which need to be present.

    /.well-known/webfinger is needed by ActivityPub

    /api/ is the endpoint used by adelphos to pass messages between
the adelphos instances.

    /api/ws is the websocket used to connect to the adelphos daemon
useing the web interface (the chat).

    The most important part is the line:

    proxy_set_header X-Forwarded-Prefix /api;

    nginx will forward this prefix and it must be the same that you
have written in the file adelphos_ap_$instance.yaml. Adelphos,
actuall, the Starlette framework on which adelphos is written, will
purge this path to call the correct handler.


