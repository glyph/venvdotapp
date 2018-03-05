# VEnvDotApp

On a Mac, if you want to access the GUI, or various other mac-specific APIs,
your executable needs to be present in a
[bundle](https://developer.apple.com/library/content/documentation/CoreFoundation/Conceptual/CFBundles/Introduction/Introduction.html).
This can be an "app bundle" or a "framework bundle".  The System python,
python.org python, Homebrew Python, and pyenv python ([with a little
work](https://github.com/pyenv/pyenv/wiki#how-to-build-cpython-with-framework-support-on-os-x))
are all so-called "framework builds" which include such a bundle.

To build a *real* bundle, something that you can distribute to someone else,
you probably want to use [`py2app`](http://py2app.readthedocs.io).  However, if
you just want to `pip install` a tool that somebody else wrote which happens to
want to present some GUI elements, or you want to develop something of your own
in a virtualenv without setting up the requisite `py2app` infrastructure
(including a `setup.py`, etc), this might be the tool for you.

## How to use it

If you're using someone else's code and you just want to make a given
virtualenv bundle-y, just `pip install venvdotapp && venvdotapp`.

For example:

```console
$ mktempenv
...
$ pip install wxpython
...
$ pycrust
This program needs access to the screen. Please run with a
Framework build of python, and only when you are logged in
on the main display of your Mac.
$ pip install venvdotapp
...
$ venvdotapp
.../.virtualenvs/tmp-4337833f3452981/bin/tmp-4337833f3452981.app
$ pycrust
<A GUI Window Pops Up>
```

If you're writing your *own* program which requires an app bundle, you don't
need to use the command-line script, just put the following at the very top of
your main script:

```python
from venvdotapp import require_bundle
require_bundle()
```

Note that this will raise an exception if your base Python is not a framework
build and therefore not capable of displaying a GUI.
