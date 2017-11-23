
"""
Transform a virtual environment into a valid `.app` so that it can do .app-y
things on OS X, such as displaying notifications.

Thanks to http://blog.gmc.uy/2015/08/mac-os-notifications-python-pyobjc.html
for the clues on how to do this.
"""

__version__ = '0.0.2'

import os
import sys
import plistlib

def appify_env(envdir):
    envname = os.path.basename(envdir)
    appdir = os.path.join(envdir, 'bin', envname + '.app', 'Contents')
    appbin = os.path.join(appdir, 'MacOS')
    apppy = os.path.join(appbin, 'python')
    plistloc = os.path.join(appdir, 'Info.plist')
    pylink = os.path.join(envdir, 'bin', 'python')
    realpython = os.path.realpath(pylink)

    print("plistloc", plistloc)
    print("apppy", apppy)
    print("realpython", realpython)
    os.makedirs(appbin)


    with open(plistloc, 'wb') as f:
        plistlib.writePlist(dict(
            CFBundleExecutable='python',
            NSUserNotificationAlertStyle='alert',
            CFBundleIdentifier='org.python.virtualenv.' + envname,
            CFBundleName=envname,
            CFBundlePackageType='APPL',
            NSAppleScriptEnabled=True,
            CFBundleInfoDictionaryVersion="6.0",
            NSHighResolutionCapable=True,
            CFBundleDevelopmentRegion="English",
        ), f)

    script_text = """\
    #!/bin/bash
    exec '{}' "$@";
    """.format(apppy)

    os.symlink(realpython, apppy)
    os.remove(pylink)
    with open(pylink, 'w') as f:
        f.write(script_text)
    os.chmod(pylink, 0o777)


def main():
    envdir = os.path.dirname(os.path.dirname(sys.executable))
    appify_env(envdir)

if __name__ == '__main__':
    main()
