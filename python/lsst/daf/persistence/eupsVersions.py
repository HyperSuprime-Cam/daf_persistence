#!/usr/bin/env python

import os, re
import eups
import subprocess
import difflib

class EupsVersions(object):
    """A class to contain EUPS version information.  The only purpose of this is to provide
    a container for the butler to load/write to/from in order to verify that different
    processes which run in the same rerun have the same EUPS versions for all packages setup.
    This is very much akin to the way in which config objects are verified to be unchanged
    before writing to a given rerun.
    """

    
    def __init__(self, versionFile=None):
        """Create an EupsVersions object.  If we're given a filename, then use it to load the
        EUPS version info.  If not, get it from eups directly.
        """

        # a dict of the version (as strings)
        self.versions = {}
        # a dict of other relevant info ... a path, or git info for working copies (as strings)
        self.info     = {}

        # we're given a version file, load that, otherwise, get get what's setup.
        if versionFile:
            # load the versionFile
            lines = []
            with open(versionFile) as fp:
                lines = fp.readlines()
            for line in lines:
                fields = line.split()
                product = fields[0]
                version = fields[1]
                info    = " ".join(fields[2:])
                self.versions[product] = version
                self.info[product]     = info.strip()

        else:
            # get any versions which are currently setup
            pipeSetups    = {}
            eupsObj = eups.Eups()
            for p in eupsObj.findProducts(tags=["setup"]):
                gitinfo = ""
                gitdir = os.path.join(p.dir, ".git")

                # The string 'LOCAL' in the version name indicates uninstalled code
                # get some git info, if we can
                if re.search("LOCAL", p.version) and os.path.exists(gitdir):
                    
                    # get the git revision and an indication if the working copy is clean
                    gitrevCmd = ["git", "--git-dir=%s"%(gitdir), "--work-tree=%s"%(p.dir),
                                 "rev-parse", "HEAD"]
                    gitdifCmd = ["git", "--git-dir=%s"%(gitdir), "--work-tree=%s"%(p.dir),
                                 "diff", "--shortstat"]
                    try:
                        gitrev = subprocess.check_output(gitrevCmd)
                        gitinfo += " rev:" + gitrev[0:8]
                        clean  = subprocess.check_output(gitdifCmd)
                        if len(clean.strip()) == 0:
                            clean = "clean-working-copy"
                        gitinfo += " " + clean
                    except:
                        gitinfo = "no-git-info"

                if len(gitinfo.split()):
                    info = " ".join(gitinfo.split())
                else:
                    info = p.dir
                        
                self.versions[p.name] = p.version
                self.info[p.name]     = info.strip()
            

    def asList(self):
        """Turn the products into a list of strings, sorted by product name
        """
        s = []
        for key in sorted(self.versions.keys()):
            version = self.versions.get(key, "none")
            info    = self.info.get(key, "none")
            if key and version and info:
                s.append("%-30s %-16s %s" % (key, version, info))
        return s
        
    def write(self, versionFile):
        """Write this set of EupsVersions to a file.

        @param versionFile   The filename to write to
        """
        with open(versionFile, "w") as fp:
            self.writeToStream(fp)

    def writeToStream(self, stream):
        """Write the eups versions to a stream"""
        for s in self.asList():
            stream.write(s+"\n")

    def diff(self, other):
        """Compare this EupsVersions to another one and return a diff-like string

        @param other         The other EupsVersions object to be compared to
        """
        
        diff = "\n".join(list(difflib.unified_diff(self.asList(), other.asList(), n=0, lineterm='')))
        return diff
