from fabric.api import run, env, abort, task

SUPPORTED_OS = ['FreeBSD', 'Linux']
CMD = {
    'FreeBSD': {
        'install': 'pkg install'
    },
    'Debian': {
        'install': 'apt-get install'
    },
    'Ubuntu': {
        'install': 'aptitude install'
    },
    'Redhat': {
        'install': 'yum install'
    }
}
PACKAGES = {
    'FreeBSD': 'python27',
    'Debian': 'python2.7',
    'Ubuntu': 'python2.7',
    'Redhat': 'python2.7'
}


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

    os = get_os_type()
    if os in SUPPORTED_OS:
        run('%s %s' % (CMD[os], PACKAGES[os]))
    else:
        abort('OS %s is not supported' % (os,))
