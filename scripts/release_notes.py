#!/usr/bin/env python
import xmlrpclib
import pysvn
import getpass
import sys
import re

username = None
password = None

def userpass(realm, u, may_save):
    global username
    global password
    if not username:
        print "Username:",
        sys.stdout.flush()
        username = raw_input()
        password = getpass.getpass()
    return True, username, password, False

################################################################################

def rev(n):
    return pysvn.Revision(pysvn.opt_revision_kind.number, n)

client = pysvn.Client()
client.callback_get_login = userpass

version_start = 1832
version_end = 1858
release_name = "1.5.1"
logs = client.log('https://vistrails.sci.utah.edu/svn',
                  revision_end=rev(version_start))

##############################################################################

def release_changed(path):
    if path.startswith('trunk/vistrails'):
        return 'trunk'
    elif path.startswith('branches/v1.2'):
        return '1.2'
    elif path.startswith('branches/v1.3'):
        return '1.3'
    else:
        return 'other'

def print_changes(release):
    if release not in release_changes:
        return
    print "Changes in '%s': " % release
    for (v, log, diff_summaries) in release_changes[release]:
        print "version %s:" % v
        print "  Affected files:"
        for summary in diff_summaries:
            if release_changed(summary.path) == release:
                print "    %s - %s" % (str(summary.summarize_kind)[0].upper(),
                                       summary.path)

re_ticket = re.compile(r'<ticket>(.*?)</ticket>', re.M | re.S)
re_bugfix = re.compile(r'<bugfix>(.*?)</bugfix>', re.M | re.S)
re_feature = re.compile(r'<feature>(.*?)</feature>', re.M | re.S)
re_skip = re.compile(r'<skip>(.*?)</skip>', re.M | re.S)

def build_release_notes(release):
    global username
    global password

    def check_inside_skip(skip_list, message):
        found = False
        for s in skip_list:
            if s.find(message) != -1:
                found = True
                break
        return found
            
    #populate dictionaries
    bugfixes = {}
    tickets = {}
    features = {}
    changes = {}
    ticket_info = {}
    if release not in release_changes:
        return
    for (v, log, diff_summaries) in release_changes[release]:
        ls = re_skip.findall(log.message)
        lf = re_feature.findall(log.message)
        lt = re_ticket.findall(log.message)
        lb = re_bugfix.findall(log.message)
        if len(ls) > 0:
            changes[v] = []
            for s in ls:
                changes[v].append(s)
        if len(lf) > 0:
            features[v] = []
            for f in lf:
                if not check_inside_skip(ls,f):
                    features[v].append(f)
        if len(lt) > 0:
            tickets[v] = []
            for t in lt:
                if not check_inside_skip(ls,t):
                    tickets[v].append(t)
        if len(lb) > 0:
            bugfixes[v] = []
            for b in lb:
                if not check_inside_skip(ls,b):
                    bugfixes[v].append(b)
        if len(ls) == 0 and len(lf) == 0 and len(lt) == 0 and len(lb) == 0:
            if not changes.has_key(v):
                changes[v] = []
            changes[v].append(log.message)
                

    #get ticket summaries from xmlrpc plugin installed on vistrails trac
    print "Will connect to VisTrails Trac with authentication..."
    if not username:
        print "Username:",
        sys.stdout.flush()
        username = raw_input()
        password = getpass.getpass()

    url = "https://%s:%s@vistrails.sci.utah.edu/login/xmlrpc"%(username,
                                                               password)
    server = xmlrpclib.ServerProxy(url)
    for (r,tl) in tickets.iteritems():
        for t in tl:
            if not ticket_info.has_key(t):
                try:
                    tid = int(t[1:])
                    ticket_info[t] = server.ticket.get(tid)
                except Exception, e:
                    tickets[r].remove(t)
                    print "revision %s: Could not get info for ticket %s"%(r,t)

    #place tickets on bugfixes or enhancements
    for (r,tlist) in tickets.iteritems():
        for t in tlist:
            txt = "Ticket %s: %s"%(t,ticket_info[t][3]['summary'])
            if ticket_info[t][3]['type'] == 'enhancement':
                if features.has_key(r):
                    features[r].insert(0,txt)
                else:
                    features[r] = [txt]
            elif ticket_info[t][3]['type'] == 'defect':
                if bugfixes.has_key(r):
                    bugfixes[r].insert(0,txt)
                else:
                    bugfixes[r] = [txt]
            else:
                #put the rest as changes
                if changes.has_key(r):
                    changes[r].insert(0,txt)
                else:
                    changes[r] = [txt]
    print
    print
    print "Release Name: v%s build %s"%(release_name,version_end)
    print 
    print "Enhancements: "
    revisions = sorted(features.keys())
    revisions.reverse()
    for r in revisions:
        rfeats = features[r]
        for f in rfeats:
            print " - %s (r%s)" %(f,r)
    
    print
    print "Bug fixes: "
    revisions = sorted(bugfixes.keys())
    revisions.reverse()
    for r in revisions:
        rbugs = bugfixes[r]
        for b in rbugs:
            print " - %s (r%s)" %(b,r)
    print
    print "Other changes: "
    revisions = sorted(changes.keys())
    revisions.reverse()
    for r in revisions:
        print "(r%s): "%r
        for c in changes[r]:
            print "  - %s... "%c[0:100]

def get_features(release):
    if release not in release_changes:
        return
    print "New features in '%s': " % release
    for (v, log, diff_summaries) in release_changes[release]:
        s = re_feature.search(log.message)
        if s:
            print " - %s (r%s)" % (s.groups()[0],v)
            
def get_ticket_closes(release):
    if release not in release_changes:
        return
    print "Ticket closes in '%s': " % release
    for (v, log, diff_summaries) in release_changes[release]:
        s = re_ticket.search(log.message)
        if s:
            print "revision %s closed ticket %s" % (v, s.groups()[0])
            
def get_bugfixes(release):
    if release not in release_changes:
        return
    print "Bugfixes in '%s': " % release
    for (v, log, diff_summaries) in release_changes[release]:
        s = re_bugfix.search(log.message)
        if s:
            print " - %s (r%s)" % (s.groups()[0], v)
    
################################################################################
# collect all changes

change_sets = []

for version in xrange(version_start, version_end):
    ds = client.diff_summarize('https://vistrails.sci.utah.edu/svn',
                               rev(version),
                               'https://vistrails.sci.utah.edu/svn',
                               rev(version+1))
    log = client.log('https://vistrails.sci.utah.edu/svn',
                     rev(version),
                     rev(version))[0]
    change_sets.append((version, log, ds))
    print version, "/", version_end

release_changes = {}

for (v, log, diff_summaries) in change_sets:
    which_releases = set()
    for diff in diff_summaries:
        which = release_changed(diff.path)
        which_releases.add(which)
    for which in which_releases:
        release_changes.setdefault(which, []).append((v, log, diff_summaries))

build_release_notes('trunk')
#print_change_summaries('trunk')
#get_features('trunk')
#get_ticket_closes('trunk')
#get_bugfixes('trunk')


