import os

from fabric.api import run, env, abort, task, local

SUPPORTED_OS = ['FreeBSD', 'Debian', 'Ubuntu', 'RedHat']
CMD = {
    'FreeBSD': {
        'install': 'pkg install -y'
    },
    'Debian': {
        'install': 'apt-get install -y'
    },
    'Ubuntu': {
        'install': 'aptitude install -y'
    },
    'RedHat': {
        'install': 'yum install -y'
    }
}
PACKAGES = {
    'FreeBSD': 'python27',
    'Debian': 'python2.7',
    'Ubuntu': 'python2.7',
    'RedHat': 'python2.7'
}

env.shell = '/bin/sh -c'


def get_os_type():
    os_t = run('uname')
    if os_t == 'Linux':
        if not run('where apt-get').failed:
            os_t = 'Debian'
        elif not run('where aptitude').failed:
            os_t = 'Ubuntu'
        elif not run('where apt-get').failed:
            os_t = 'RedHat'

    return os_t


def fill_env(**kwargs):
    for key, value in kwargs.items():
        setattr(env, key, value)


@task
def install_python(user=None, password=None, sudo=False):
    """install python interpreter on the remote server"""

    fill_env(user=user, password=password)

    os_t = get_os_type()
    if os_t in SUPPORTED_OS:
        run('%s %s' % (CMD[os_t]['install'], PACKAGES[os_t]))
    else:
        abort('OS %s is not supported' % (os_t,))


@task
def install_keys(user=None, password=None, sudo=False):
    """Add the salt master ssh key to the authorized_keys list on the
    remote server"""

    fill_env(user=user, password=password)

    # user handling salt ssh key
    remote_user = 'root'
    # master group of remote_user
    remote_group = 'root'

    os_t = get_os_type()
    if os_t in SUPPORTED_OS:
        if os_t == 'FreeBSD':
            pki_path = '/usr/local/etc/salt/pki/master/ssh/salt-ssh.rsa.pub'
            remote_group = 'wheel'
        else:
            pki_path = '/etc/salt/pki/master/ssh/salt-ssh.rsa.pub'

        if remote_user == 'root':
            home_dir = os.path.join('/', remote_user)
        else:
            home_dir = os.path.join('/', 'home', remote_user)

        ssh_dir = os.path.join(home_dir, '.ssh')
        auth_file = os.path.join(ssh_dir, 'authorized_keys')

        if run('[ ! -d %s ] && echo 1 || echo 0' % (ssh_dir,)) == '1':
            run('mkdir %s' % (ssh_dir,))
            run('chmod 700 %s' % (ssh_dir,))
            run('chown %s:%s %s' % (remote_user, remote_group, ssh_dir))

        pub_key = local('cat %s' % (pki_path,), capture=True)
        if pub_key.succeeded:
            if run('[ ! -f %s ] && echo 1 || echo 0' % (auth_file,)) == '0':
                if run('grep "%s" %s' % (pub_key, auth_file),
                       shell=False, warn_only=True).return_code == 1:
                    run('echo "%s" >> %s' % (pub_key, auth_file), shell=False)
            else:
                run('echo "%s" > %s' % (pub_key, auth_file), shell=False)
            run('chown %s:%s %s' % (remote_user, remote_group, auth_file))
            run('chmod 600 %s' % (auth_file,))
        else:
            abort('%s key file does not exist' % (pki_path,))
    else:
        abort('OS %s is not supported' % (os,))
