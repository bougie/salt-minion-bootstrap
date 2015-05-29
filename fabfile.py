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


@task
def install_python(user=None, password=None, sudo=False):
    if user is not None:
        env.user = user
    if password is not None:
        env.password = password

    os_t = get_os_type()
    if os_t in SUPPORTED_OS:
        run('%s %s' % (CMD[os_t]['install'], PACKAGES[os_t]))
    else:
        abort('OS %s is not supported' % (os_t,))
