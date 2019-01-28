'''
Created on 12.02.2013

@author: ajazdzewski
'''
import sys
import re

from ganeti import utils
from common import env


class RBD(object):
    """exec rbd commands."""

    enviroment = None

    def __init__(self):
        self.enviroment = env.env()

    def isPool(self, pool='rbd'):
        if pool is None:
            sys.stderr.write('no poolname is given')
            return False

        result = utils.RunCmd(["rados", "lspools"])
        if result.failed:
            sys.stderr.write("rados lspools (%s): %s" %
                             (result.fail_reason, result.output))
            return False

        res = re.search('(' + pool + ')', result.output)
        if res is None:
            sys.stderr.write('no result\n')
            return False

        return pool in res.groups()

    def isVol(self, name, pool='rbd'):
        if name is None:
            sys.stderr.write('no devicename is given')
            return False

        if pool is None:
            sys.stderr.write('no poolname is given')
            return False

        if not self.isPool(pool):
            sys.stderr.write('pool not found')
            return False

        result = utils.RunCmd(["rbd", "-p", pool, "ls"])
        if result.failed:
            sys.stderr.write("rbd ls (%s): %s" %
                             (result.fail_reason, result.output))
            return False

        res = re.search('(' + name + ')', result.output)
        if res is None:
            return False
        return name in res.groups()

    def isMapped(self, name, pool='rbd'):
        if name is None:
            sys.stderr.write('no devicename is given')
            return False

        if pool is None:
            sys.stderr.write('no poolname is given')
            return False

        if not self.isPool(pool):
            sys.stderr.write('pool not found')
            return False

        if not self.isVol(name, pool):
            sys.stderr.write('Vol not found')
            return False

        result = utils.RunCmd(["rbd", "showmapped"])
        if result.failed:
            sys.stderr.write("rbd showmapped failed (%s): %s" %
                             (result.fail_reason, result.output))
            return False

        res = re.search(
            '(' + pool + ')[ \t]+(' + name + ')[ \t]+.*[ \t]+(/dev/rbd\d+)', result.output)
        if res is None:
            return False

        return {'pool': res.group(1), 'name': res.group(2), 'dev': res.group(3)}

    def map(self, name, pool='rbd'):
        if name is None:
            sys.stderr.write('no devicename is given')
            return False

        if pool is None:
            sys.stderr.write('no poolname is given')
            return False

        if not self.isPool(pool):
            sys.stderr.write('pool not found')
            return False

        if not self.isVol(name, pool):
            sys.stderr.write('Vol not found')
            return False

        if self.isMapped(name, pool) is False:
            result = utils.RunCmd(
                ["rbd", "map", "-p", "%s" % pool, "%s" % name])
            if result.failed:
                sys.stderr.write("rbd map failed (%s): %s" %
                                 (result.fail_reason, result.output))
                return False
            if self.isMapped(name, pool) is False:
                return False

        sys.stdout.write("%s\nrbd:%s/%s" %
                         (self.isMapped(name, pool)['dev'], pool, name))
        return True

    def unmap(self, name, pool='rbd'):
        if name is None:
            sys.stderr.write('no devicename is given')
            return False

        if pool is None:
            sys.stderr.write('no poolname is given')
            return False

        if not self.isPool(pool):
            sys.stderr.write('pool not found')
            return False

        if not self.isVol(name, pool):
            sys.stderr.write('Vol not found')
            return False

        if self.isMapped(name, pool) is False:
            return True

        result = utils.RunCmd(["rbd", "unmap", "%s" %
                               self.isMapped(name, pool)['dev']])
        if result.failed:
            sys.stderr.write("rbd unmap failed (%s): %s" %
                             (result.fail_reason, result.output))
            return False
        if self.isMapped(name, pool) is False:
            return True
        return False

    def grow(self, name, size, pool='rbd'):
        if name is None:
            sys.stderr.write('no devicename is given')
            return False

        if size is None:
            sys.stderr.write('no size is given')
            return False

        if pool is None:
            sys.stderr.write('no poolname is given')
            return False

        if not self.isPool(pool):
            sys.stderr.write('pool not found')
            return False

        if not self.isVol(name, pool):
            sys.stderr.write('Vol not found')
            return False

        result = utils.RunCmd(["rbd", "resize", "-p", "%s" %
                               pool, "%s" % name, "--size", "%s" % size])
        if result.failed:
            sys.stderr.write('rbd resize failed (%s): %s\n' %
                             (result.fail_reason, result.output))
            return False
        return True

    def rm(self, name, pool='rbd'):
        if name is None:
            sys.stderr.write('no devicename is given')
            return False

        if pool is None:
            sys.stderr.write('no poolname is given')
            return False

        if not self.isPool(pool):
            sys.stderr.write('pool not found')
            return False

        if not self.isVol(name, pool):
            sys.stderr.write('Vol not found')
            return False

        result = utils.RunCmd([
            "rbd",
            "rm",
            "-p",
            "%s" % pool,
            "%s" % name])
        if result.failed:
            sys.stderr.write("Can't remove Image %s from cluster with rbd rm: %s - %s" %
                             (name, result.fail_reason, result.output))
            return False
        return True

    def create(self, name, size, pool='rbd'):
        if name is None:
            sys.stderr.write('no devicename is given')
            return False

        if size is None:
            sys.stderr.write('no size is given')
            return False

        if pool is None:
            sys.stderr.write('no poolname is given')
            return False

        if not self.isPool(pool):
            sys.stderr.write('pool not found')
            return False

        if self.isVol(name, pool):
            sys.stderr.write('Volume already exists')
            return False

        result = utils.RunCmd(["rbd", "create", "-p", "%s" %
                               pool, "%s" % name, "--size", "%s" % size])
        if result.failed:
            sys.stderr.write("Can't create Image %s from cluster with rbd create: %s - %s" %
                             (name, result.fail_reason, result.output))
            return False
        return True

    def clone(self, name, size, origin, originpool='rbd', pool='rbd'):
        if name is None:
            sys.stderr.write('no devicename is given')
            return False

        if size is None:
            sys.stderr.write('no size is given')
            return False

        if pool is None:
            sys.stderr.write('no poolname is given')
            return False

        if not self.isPool(pool):
            sys.stderr.write('pool not found')
            return False

        if self.isVol(name, pool):
            sys.stderr.write('Volume already exists')
            return False

        if not self.isPool(originpool):
            sys.stderr.write('originpool not found')
            return False

        if not self.isVol(origin, originpool):
            sys.stderr.write('origin not exists')
            return False

        result = utils.RunCmd(["rbd", "cp", "--pool", "%s" % originpool,
                               "--dest-pool", "%s" % pool, "%s" % origin, "%s" % name])
        if result.failed:
            sys.stderr.write("Can't clone Image %s from cluster with rbd cp: %s - %s" %
                             (name, result.fail_reason, result.output))
            return False

        result = utils.RunCmd(["rbd", "resize", "-p", "%s" %
                               pool, "%s" % name, "--size", "%s" % size])
        if result.failed:
            sys.stderr.write('rbd resize failed (%s): %s\n' %
                             (result.fail_reason, result.output))
            return False
        return True
