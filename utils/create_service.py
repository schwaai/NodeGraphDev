import os
import sys
import subprocess
import unittest


def install_missing_packages(packages):
    """Install missing Python packages."""
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def install_shell_script_as_service(script_path):
    service_name = os.path.splitext(os.path.basename(script_path))[0]
    service_path = '/etc/init.d/{}'.format(service_name)
    with open(service_path, 'w') as service_file:
        service_file.write('#!/bin/bash\n')
        service_file.write('### BEGIN INIT INFO\n')
        service_file.write('# Provides:          {}\n'.format(service_name))
        service_file.write('# Required-Start:    $remote_fs $syslog\n')
        service_file.write('# Required-Stop:     $remote_fs $syslog\n')
        service_file.write('# Default-Start:     2 3 4 5\n')
        service_file.write('# Default-Stop:      0 1 6\n')
        service_file.write('# Short-Description: {}\n'.format(service_name))
        service_file.write('# Description:       {}\n'.format(service_name))
        service_file.write('### END INIT INFO\n')
        service_file.write('\n')
        service_file.write('case "$1" in\n')
        service_file.write('start)\n')
        service_file.write('\t{} &> /var/log/{}.log &\n'.format(script_path, service_name))
        service_file.write('\t;;\n')
        service_file.write('stop)\n')
        service_file.write('\tpkill -f "{}"\n'.format(script_path))
        service_file.write('\t;;\n')
        service_file.write('restart)\n')
        service_file.write('\t$0 stop\n')
        service_file.write('\t$0 start\n')
        service_file.write('\t;;\n')
        service_file.write('*)\n')
        service_file.write('\techo "Usage: $0 {start|stop|restart}" >&2\n')
        service_file.write('\texit 1\n')
        service_file.write('\t;;\n')
        service_file.write('esac\n')
    os.chmod(service_path, 0o755)
    os.system('update-rc.d {} defaults'.format(service_name))
    print('Service {} installed successfully.'.format(service_name))


class TestCreateService(unittest.TestCase):
    def test_create_service(self):
        if os.geteuid() != 0:
            print('This script must be run as root or with sudo.')
            return

        script_path = os.path.abspath('start.sh')
        packages = ['package1', 'package2']  # Add any missing packages here
        install_missing_packages(packages)
        install_shell_script_as_service(script_path)
        self.assertTrue(os.path.exists('/etc/init.d/start'))
        os.system('service start stop')
        os.system('update-rc.d -f start remove')
        os.remove('/etc/init.d/start')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        script_path = os.path.abspath(sys.argv[1])
        packages = ['numpy', 'moviepy']  # Add any missing packages here
        install_missing_packages(packages)
        install_shell_script_as_service(script_path)
    else:
        unittest.main(argv=[sys.argv[0]])
