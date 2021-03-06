import os
import yaml

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


def load_config(os_typeype):
    CWD = os.path.dirname(os.path.realpath(__file__))
    try:
        with open(os.path.join(CWD, 'config.yml'), 'r') as f:
            return yaml.load(f)[os_typeype]
    except IOError:
        abort('The config file config.yml in directory %s does not exist' % (
            CWD,))
    except:
        abort('Error while loading config file')


def get_os_type():
    os_type = run('uname')
    if os_type == 'Linux':
        if not run('where apt-get').failed:
            os_type = 'Debian'
        elif not run('where aptitude').failed:
            os_type = 'Ubuntu'
        elif not run('where yum').failed:
            os_type = 'RedHat'

    return os_type


def fill_env(**kwargs):
    for key, value in kwargs.items():
        if value is not None:
            setattr(env, key, value)


@task
def install_python(user=None, password=None, sudo=False):
    """install python interpreter on the remote server"""

    fill_env(user=user, password=password)

    os_type = get_os_type()
    if os_type in SUPPORTED_OS:
        run('%s %s' % (CMD[os_type]['install'], PACKAGES[os_type]))
    else:
        abort('OS %s is not supported' % (os_type,))


@task
def install_keys(user=None, password=None, sudo=False):
    """Add the salt master ssh key to the authorized_keys list on the
    remote server"""

    fill_env(user=user, password=password)

    # user handling salt ssh key
    remote_user = 'root'
    # master group of remote_user
    remote_group = 'root'
    # salt master ssh public key
    pki_path = '/etc/salt/pki/master/ssh/salt-ssh.rsa.pub'

    os_type = get_os_type()
    if os_type in SUPPORTED_OS:
        config = load_config(os_type)

        # override default values with values in config files
        if 'pki_path' in config:
            pki_path = config['pki_path']
        if 'key_remote_user' in config:
            remote_user = config['key_remote_user']
        if 'key_remote_group' in config:
            remote_group = config['key_remote_group']

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
