#!/usr/bin/python

import os
import time
import datetime

backup_dir = ""
prefix = "mysql_"
db_pw = ''
query = "/usr/bin/mysqldump -u root -p" + db_pw +" --all-databases > %(loc)s"
compressor = '/bin/gzip'

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

def do_backup():
	give_log("Start mysql backup for " + dump_file)
	cmd = query % {'loc':dump_file}
	os.system(cmd)
	cmd = compressor + " " + dump_file
	os.system(cmd)
	give_log("End mysql backup for " + dump_file) 


if __name__ == '__main__':
	global cur, log, error, dump_file

	cur = int(time.time())
	check_valid_dir()
	check_permission()

	error = open(backup_dir+"/dump.error", "a")
	log = open(backup_dir+"/dump.log", "a")


	try :
		os.chdir(backup_dir)
		dump_file = prefix+str(cur)+".sql"
		do_backup()

	except Exception, e :
		give_log("There was an error for handling " + dump_file)
		report_error(dump_file + ": error occured: " + str(e))
	

	error.close()
	log.write("\n")
	log.close()

