
"""
Transform a virtual environment into a valid `.app` so that it can do .app-y
things on OS X, such as displaying notifications.

Thanks to http://blog.gmc.uy/2015/08/mac-os-notifications-python-pyobjc.html
for the clues on how to do this.
"""

__version__ = '19.7.1'

import ctypes
import os
import sys
import sysconfig
import plistlib

class NotAVirtualEnv(Exception):
    """
    Not a virtual environment.
    """


class NotAFrameworkPython(Exception):
    """
    This Python wasn't built with the ability to run GUI stuff, so creating a
    virtual bundle might not help anyway.
    """


class AlreadyTried(Exception):
    """
    We already tried to appify this virtual environment and it failed for some
    reason.
    """


def _current_virtual_env():
    """
    Determine the directory name of the current virtual environment, raising an
    exception if the current interpreter is not part of a virtual environment.
    """
    bindir = os.path.dirname(sys.executable)
    if os.path.basename(bindir) != 'bin':
        raise NotAVirtualEnv("Executable {} was not in a 'bin' directory."
                             .format(sys.executable))
    for expected_file in ['activate', 'python', 'pip']:
        if not os.path.exists(os.path.join(bindir, expected_file)):
            raise NotAVirtualEnv("Did not find expected {} in {}".format(
                expected_file, bindir
            ))
    venvdir = os.path.dirname(bindir)
    for expected_file in ['include', 'lib']:
        if not os.path.exists(os.path.join(venvdir, expected_file)):
            raise NotAVirtualEnv("Did not find expected {} in {}".format(
                expected_file, venvdir
            ))
    return venvdir


def _appify_env(envdir, bundle_id=None):
    envname = os.path.basename(envdir)
    appdir = os.path.join(envdir, 'bin', envname + '.app', 'Contents')
    appbin = os.path.join(appdir, 'MacOS')
    apppy = os.path.join(appbin, 'python')
    if os.path.exists(apppy):
        return apppy
    plistloc = os.path.join(appdir, 'Info.plist')
    fakepython = os.path.abspath(os.path.join(envdir, 'bin', 'python'))
    realpython = os.path.realpath(fakepython)
    if os.path.dirname(realpython) != os.path.dirname(fakepython):
        raise NotAVirtualEnv(
            "Refusing to overwrite a Python outside the virtualenv {}"
            .format(realpython)
        )
    os.makedirs(appbin)
    if bundle_id is None:
        bundle_id = 'org.python.virtualenv.' + envname

    with open(plistloc, 'wb') as f:
        plistlib.writePlist(dict(
            CFBundleExecutable='python',
            NSUserNotificationAlertStyle='alert',
            CFBundleIdentifier=bundle_id,
            CFBundleName=envname,
            CFBundlePackageType='APPL',
            NSAppleScriptEnabled=True,
            CFBundleInfoDictionaryVersion="6.0",
            NSHighResolutionCapable=True,
            CFBundleDevelopmentRegion="English",
            NSRequiresAquaSystemAppearance=False,
        ), f)

    os.symlink(realpython, apppy)
    return apppy


def _looks_bundleish(path):
    """
    Does this path looks like it resides in a bundle?
    """
    if '.framework/' in path or '.app/' in path:
        return True
    real_path = os.path.realpath(path)
    if real_path != path:
        return _looks_bundleish(real_path)
    return False


_already_tried_var = 'ALREADY_TRIED_APPIFY'

def _ultra_real_argv():
    """
    Get ALL the command-line arguments to the interpreter.
    """
    if sys.version_info.major == 2:
        chtype = ctypes.c_char_p
    else:
        chtype = ctypes.c_wchar_p
    argv = ctypes.POINTER(chtype)()
    argc = ctypes.c_int()
    ctypes.pythonapi.Py_GetArgcArgv(ctypes.byref(argc), ctypes.byref(argv))
    hlargv = []
    for idx in range(argc.value):
        hlargv.append(argv[idx])
    return hlargv


def _prepare_bundle(bundle_id):
    """
    Prepare a bundle, returning a boolean indicating whether re-executing is
    necessary.
    """
    if _looks_bundleish(sys.executable):
        # Already probably in a bundle, we're good!
        return
    if os.environ.get(_already_tried_var):
        # Already tried to run appify below, something went super wrong!
        raise AlreadyTried()
    if not sysconfig.get_config_var("WITH_NEXT_FRAMEWORK"):
        raise NotAFrameworkPython(
            "Sorry, your Python wasn't built with --enable-framework."
        )
    virtual_env = _current_virtual_env()
    return _appify_env(virtual_env, bundle_id)


def _restart(exe):
    """
    Re-start the interpreter, with the new interpreter.
    """
    env = os.environ.copy()
    env[_already_tried_var] = 'yes'
    argv = _ultra_real_argv()
    os.execve(exe, [exe] + argv[1:], env)


def require_bundle(bundle_id=None):
    """
    If this Python doesn't appear to be running in the context of a bundle,
    bundle-ify its virtual environment and attempt to re-launch.
    """
    exe = _prepare_bundle(bundle_id)
    if exe is None:
        return
    _restart(exe)


def _install_pth_file():
    """
    Install a .pth file into the current virtual environment that.
    """
    with open(os.path.join(os.path.dirname(__file__),
                           'venvdotapp.pth'), 'w') as f:
        f.write("import venvdotapp; venvdotapp.require_bundle()")


def _main():
    require_bundle()
    _install_pth_file()
    print(sys.executable.rsplit('.app', 1)[0] + '.app')

if __name__ == '__main__':
    _main()
