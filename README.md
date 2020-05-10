## Running bitwarden_rs on a shared hosting service

This is not a common configuration, and not recommended compared to running
on a VPS or similar, but sometimes an organization only has access to a
shared hosting service and only wants to use that. This repo contains an
example of how that can be accomplished on
[DreamHost](https://www.dreamhost.com/) specifically, though with minor
changes, it can probably be applied to many other shared hosting services.

Shared hosting is generally geared towards running PHP apps. Many hosts also
support Ruby, Python, and/or Node.js apps, but there is generally no direct
support for reverse proxying to an arbitrary backend service. The example
provided here uses a small Python
[WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) app to
proxy to the bitwarden_rs backend.

This document assumes basic familiarity with Linux (knowing how to SSH into a
host, copy files to the host, make and change into directories, etc.).

## Prerequisites

In the DreamHost admin panel, create a new subdomain (e.g., `bw.example.org`)
and enable HTTPS and [Passenger](https://www.phusionpassenger.com/).

For more details, see [How do I enable Passenger on my domain?](https://help.dreamhost.com/hc/en-us/articles/216385637-How-do-I-enable-Passenger-on-my-domain-)

## Clone this repo

SSH into your subdomain account. From your home directory, run

    $ git clone https://github.com/jjlin/bitwardenrs-shared-hosting.git bwrs

This makes a copy of this repo in a directory called `bwrs`. You can use a
different directory name if you prefer, but you'll have to modify the value
of `BITWARDENRS_HOME` in `passenger_wsgi.py` accordingly.

If the `git` command above isn't available for some reason, you can also just
download a zip file of the repo and extract it:

    $ wget https://github.com/jjlin/bitwardenrs-shared-hosting/archive/master.zip
    $ unzip master.zip
    $ mv bitwardenrs-shared-hosting-master bwrs

Stay logged in via SSH, as the rest of the steps below will need SSH as well.

## Install Python dependencies

Run this command:

    $ pip3 install WebOb WSGIProxy2

The output should look like:

    Collecting WebOb
      Using cached https://files.pythonhosted.org/packages/18/3c/de37900faff3c95c7d55dd557aa71bd77477950048983dcd4b53f96fde40/WebOb-1.8.6-py2.py3-none-any.whl
    Collecting WSGIProxy2
      Using cached https://files.pythonhosted.org/packages/2d/a5/3afac2542081b890de83e0089a0057cfb7dc9ad877ccc5594e6c6e1976b8/WSGIProxy2-0.4.6-py3-none-any.whl
    Collecting six (from WSGIProxy2)
      Using cached https://files.pythonhosted.org/packages/65/eb/1f97cb97bfc2390a276969c6fae16075da282f5058082d4cb10c6c5c1dba/six-1.14.0-py2.py3-none-any.whl
    Installing collected packages: WebOb, six, WSGIProxy2
    Successfully installed WSGIProxy2-0.4.6 WebOb-1.8.6 six-1.14.0

## Enable the Python WSGI proxy app

Copy the `passenger_wsgi.py` file in this repo into your
`/home/<user>/<subdomain>` directory.

Note that Passenger starts a persistent Python process that loads the
`passenger_wsgi.py` script. If you need to modify the script, you'll need to
kill the Python process (e.g., `pkill python3`) to force it to reload the
modified script.

For more details, see [Passenger and Python WSGI](https://help.dreamhost.com/hc/en-us/articles/215769548-Passenger-and-Python-WSGI).

If you visit your subdomain now (e.g., `https://bw.example.org`), you should
see a `502 Bad Gateway` message. This is because the bitwarden_rs backend is
not yet running.

## Start the bitwarden_rs backend

Make sure you're in the `bwrs` directory for the steps below.

### Download the bitwarden_rs server and web vault

Run this command:

    $ ./docker-image-extract bitwardenrs/server:alpine

The output should look like the following (the layer IDs will likely all be different) :

    Downloading layer aad63a9339440e7c3e1fff2b988991b9bfb81280042fa7f39a5e327023056819...
    Extracting layer...
    Downloading layer a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4...
    Extracting layer...
    Downloading layer 0f458b6db0345357230896b9cd22b399aa68a78d5254ad9b2784259b90ddab00...
    Extracting layer...
    Downloading layer 42081820ca1e17eb55a7aa32bc418d89f6c0c17f9e7e5ce6856645775dc1d511...
    Extracting layer...
    Downloading layer a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4...
    Extracting layer...
    Downloading layer 1bff0b7ce7a73c1c8f22c15d6bda1611e7632a43289f2d505413c5642d37f4bc...
    Extracting layer...
    Downloading layer 1a54fac88f79558a1d0abd20a893927a7a81c88433720768b5f1cbb553fd1fd0...
    Extracting layer...
    Downloading layer 432c8ddf745d70f0a48161afdbe691e2a7f8e9be5054ba19a198c2af40571e65...
    Extracting layer...
    Downloading layer d3516535ece61f38172bb6c2c537fd7b9324f4be4fde22e9eee4dbce349da231...
    Extracting layer...
    Downloading layer a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4...
    Extracting layer...
    Image contents extracted into ./output.

This pulls the latest bitwarden_rs server Docker image and extracts its files
into a directory called `output`. Move the server binary and web vault files
into your `bwrs` directory. The other files in `output` aren't needed, so you
can delete the directory afterwards.

    $ mv output/bitwarden_rs output/web-vault .
    $ rm -rf output

### Configure bitwarden_rs

For purposes of this tutorial, start by copying `config.json.template` to
`config.json` and editing it as described below.

    $ cp data/config.json.template data/config.json
    $ # Now edit data/config.json with your preferred editor.

The initial `config.json` looks like
```json
{
  "domain": "https://bw.example.org",
  "admin_token": "<output of 'openssl rand -hex 32'>"
}
```

Do the following:

* Change the value of `domain` to the subdomain URL you selected.
* Run `openssl rand -hex 32` to generate a random 32-byte (256-bit) hex
  string, and change the value of `admin_token` to this hex string.  You'll
  use this admin token to log into the admin page to perform further
  configuration.

### Run the bitwarden_rs backend server

Run this command:

    $ ./start.sh

This script runs the `bitwarden_rs` executable in the background, with logs
saved in `bitwarden_rs.log`.

After this, visiting https://bw.example.org should show the Bitwarden web
vault interface, and https://bw.example.org/admin should lead to the admin
page (after you input the admin token).

You can re-run this command to restart the backend server if needed.

### Install the healthcheck script

This step is technically optional, but especially if your shared host only
allows a process to run for a certain amount of time or use a certain amount
of CPU, you'll want to set up a cron job that periodically checks that the
server process is still alive, and restarts it automatically if not.

Run this command:

    $ crontab -e

Paste the contents of the `crontab` file in this repo into the editor and
save it. If you cloned this repo into a directory not named `bwrs`, make sure
to adjust the path in the crontab directive accordingly.

### Next steps

You'll probably want to lock down your settings a bit, and set up email
service. From the admin page, you should review at least the following
settings:

* General settings
  * `Allow new signups` -- you might want to disable this so random users
    can't create accounts on your server.
  * `Require email verification on signups`
* SMTP Email Settings
  * You can use your hosting service's SMTP server, in which case you should
    consult their documentation (e.g.,
    [Email client protocols and port numbers](https://help.dreamhost.com/hc/en-us/articles/215612887-Email-client-protocols-and-port-numbers)
    for DreamHost).
  * Your hosting service's SMTP service may not deliver email promptly. In
    that case, you might consider using an external SMTP service like
    [SendGrid](https://sendgrid.com/) or [MailJet](https://www.mailjet.com/).
    These both provide 100-200 outgoing emails per day on their free tier,
    which is probably enough for small organizations.

There are a lot more things that can be configured in bitwarden_rs, and a
detailed treatment is beyond the scope of this tutorial. For more details,
the best place to start is
https://github.com/dani-garcia/bitwarden_rs/wiki/Configuration-overview.

### Upgrade bitwarden_rs

From time to time, you may want to upgrade bitwarden_rs to access bug fixes
or new features. To do this, change into the `bwrs` directory, stop the
bitwarden_rs server, and delete the existing bitwarden_rs and web vault
files:

    $ pkill bitwarden_rs
    $ rm -rf bitwarden_rs web-vault

Then repeat the steps from
[Download the bitwarden_rs server and web vault](#download-the-bitwarden_rs-server-and-web-vault)
and [Run the bitwarden_rs backend server](#run-the-bitwarden_rs-backend-server).

## Limitations

This configuration currently doesn't support [WebSocket notifications](https://github.com/dani-garcia/bitwarden_rs/wiki/Enabling-WebSocket-notifications), though this isn't essential functionality.
But if you know how to get this to work in the shared host environment, feel free to send a PR.
