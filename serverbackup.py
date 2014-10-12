#!/usr/bin/python

import os
import time
import datetime

backup_dir = ""
prefix = "server_"
compressor = '/bin/tar -cvpzf '
query = compressor + "%(loc)s %(exclude)s %(target)s"
exclude = ['/mnt', '/proc', '/lost+found', '/media', '/sys', '/home', backup_dir]
targets = ['/bin', '/boot', '/dev', '/etc', '/initrd', '/img', '/lib', '/lib32', '/lib64', '/libx32', '/opt', '/root', '/run', '/sbin', '/srv',  '/usr', '/var', '/vmlinuz'] 
user_dir_backup = ['backups']
maximum = 5

def get_current_time() :
	return datetime.datetime.now().strftime("%Y-%m-%d %I:%M%p")

def report_error(msg):
	error.write(get_current_time()+": "+msg+"\n")

def give_log(msg):
	log.write(get_current_time()+": "+msg+"\n")

def check_valid_dir():
	if not os.path.isdir(backup_dir) :
		print "error: " + backup_dir+ "No such directory"
		exit(-1)

def check_permission():
	if not os.access(backup_dir, os.X_OK|os.R_OK|os.W_OK) :
		print "error: tried to use " + backup_dir+ " Permission Denied"
		exit(-1)

def check_exclude_cmd():
    global exclude
    
    arg = ""

    for ex in exclude :
        if ex[0] != '/':
            report_error("error: "+ex+" should be absolute path. delte this entry")
        elif not os.path.exists(ex):
            report_error("error: "+ex+" is not available")

        else :
            arg += " --exclude " + ex

    return arg

def get_status() :
    backups = filter(lambda x: ".tar.gz" in x, os.listdir(backup_dir))
    backups.sort()
    return (len(backups), backups[0] )

def check_maximum():
    (cur, old) = get_status()

    if cur > maximum : os.system("rm -rf " + old)

def make_target():
    global targets
    
    arg = ""

    users = os.listdir('/home')

    for user in users :
        for priv in user_dir_backup :
            tmp = os.path.join('/home/', user, priv)
            if os.path.exists(tmp) :
                for entry  in os.listdir(tmp) :
                    entry = os.path.join(tmp, entry)
                    if not os.path.islink(entry) :
                        targets.append(entry) 
                    else : 
                        targets.append(os.path.join(tmp, os.readlink(entry)))


    for target in targets :
        if target[0] != '/':
            report_error("error: "+target+" should be absolute path. delte this entry")
        elif not os.path.exists(target):
            report_error("error: "+target+" is not available")

        else :
            arg += " " + target

    return arg

def do_backup():
    global cur
    give_log("Start server backup for " + backup_file)
    arg = check_exclude_cmd()

    target = make_target()
    give_log("Targets: " + target)
    give_log("Excludes: " + arg)

    cmd = query % {'loc':backup_file, 'target':target, 'exclude':arg}
    os.system(cmd)
    
    end = int(time.time())
    filesize = os.path.getsize(backup_file) / ( 1024.0 ** 3)
    give_log("End server backup for " + backup_file+ ". Takes %d seconds & file size is %.2f GB" % (end-cur, filesize)) 


if __name__ == '__main__':
	global cur, log, error, backup_file

	cur = int(time.time())
	check_valid_dir()
	check_permission()

	error = open(backup_dir+"/backup.error", "a")
	log = open(backup_dir+"/backup.log", "a")


	try :
		os.chdir(backup_dir)
		backup_file = prefix+str(cur)+".tar.gz"
		do_backup()

	except Exception, e :
		give_log("There was an error for handling " + backup_file)
		report_error(backup_file + ": error occured: " + str(e))
	
        check_maximum()
	error.close()
	log.write("\n")
	log.close()

