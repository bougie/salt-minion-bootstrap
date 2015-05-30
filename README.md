salt-minion-bootstrap
=====================

**salt-minion-bootstrap** is a fabric script use to deploy usefull requirements
for installing a salt minion.  
Currently, it can do:

* install python 2.7
* copy salt master ssh key

Next, you can just do a salt states to install salt-minion via salt-ssh command.

INSTALL
-------

    # pip install -r requirements.txt

HOWTO
-----

Before using fabric script, the remote ssh server have to authorize root login with password (PermitRootLogin yes in sshd_config).  
Just remove this workaround with a salt states after bootstraping salt-minion.

All command accept these options:

* **user**: user used to connect to the remote server
* **password**: password of user used to connect to the remote server

To specify a host, use **-H** option of the fab command.

An example:

    # fab -H localhost install_python:user=toto,password=tata

### install_python

Install python interpreter.

### install_keys

Install salt master ssh key.
