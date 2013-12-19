STDOUT = -2 # same value in subprocess and gevent.subprocess

def Popen(use_gevent=False, *args, **kwargs):
    """Provide gevent support for subprocess.Popen"""
    if use_gevent:
        from gevent import subprocess
    else:
        import subprocess
    return subprocess.Popen(*args, **kwargs)
