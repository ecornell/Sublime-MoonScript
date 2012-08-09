import sublime, sublime_plugin

import subprocess, re, os, threading, tempfile, datetime, uuid
from subprocess import Popen, PIPE


try:
    STARTUP_INFO = subprocess.STARTUPINFO()
    STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    STARTUP_INFO.wShowWindow = subprocess.SW_HIDE
except (AttributeError):
    STARTUP_INFO = None





def runcmd(args, input=None, stdout=PIPE, stderr=PIPE, shell=False):

    out = ""
    err = ""
    exc = None

    #old_env = os.environ.copy()
    #os.environ.update(env())
    try:
        p = Popen(args, stdout=stdout, stderr=stderr, stdin=PIPE,
            startupinfo=STARTUP_INFO, shell=shell)
        if isinstance(input, unicode):
            input = input.encode('utf-8')
        out, err = p.communicate(input=input)
        out = out.decode('utf-8') if out else ''
        err = err.decode('utf-8') if err else ''
    except (Exception) as e:
        # err = u'Error while running %s: %s' % (args[0], e)
        print e
        exc = e
    #os.environ.update(old_env)
    return (out, err, exc)




        




