import urllib
import os
import time
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('pronom-xml-export.cfg')

max_fmt = config.getint('puids', 'fmt')
max_xfmt = config.getint('puids', 'xfmt')

max_cmp = config.getint('puids', 'fmt')
max_xcmp = config.getint('puids', 'xfmt')

max_chr = config.getint('puids', 'fmt')
max_xchr = config.getint('puids', 'xfmt')

max_sfw = config.getint('puids', 'fmt')
max_xsfw = config.getint('puids', 'xfmt')

def set_puid_no(puid_type):

	puid_no = 0

	if puid_type == 'fmt':
		puid_no = max_fmt
	elif puid_type == 'x-fmt':
		puid_no = max_xfmt
	elif puid_type == 'cmp':
		puid_no = max_cmp
	elif puid_type == 'x-cmp':
		puid_no = max_xcmp
	elif puid_type == 'chr':
		puid_no = max_chr
	elif puid_type == 'x-chr':
		puid_no = max_xfmt
	elif puid_type == 'sfw':
		puid_no = max_sfw
	elif puid_type == 'x-sfw':
		puid_no = max_xsfw
	else:
		puid_no = 0
		
	return puid_no

# BOF strings we expect to see under normal and error conditions
error_string = '<!DOCTYPE html'
good_string = '<?xml version='

#url through which to access Pronom data...
base_url = 'http://www.nationalarchives.gov.uk/PRONOM/'

puid_type_list = ['x-fmt', 'fmt', 'x-cmp', 'cmp', 'x-chr', 'chr', 'x-sfw', 'sfw']

def export_data():
	for x in puid_type_list:
		puid_type_url = base_url + x + '/'
		current_dir = os.getcwd()
		new_dir = os.getcwd() + '//pronom_export//' + x + '//'
		
		try:
			os.makedirs(new_dir)
		except OSError as (errno, strerror):
			print "OS error({0}): {1}".format(errno, strerror)

		#change to expor directory to store xml...
		os.chdir(new_dir)
		
		#urlib code here...
		puid_no = set_puid_no(x)

		for i in range(1,puid_no+1):
			filename = x + str(i) + '.xml'
			puid_url = puid_type_url + str(i) + '.xml'
			
			url = urllib.urlopen(puid_url)
			test_string = url.read(14)
			if(check_record(test_string)):
				urllib.urlretrieve(puid_url, filename)

		#revert back to original directory...
		os.chdir(current_dir)		


def check_record(test_string):
	return_val = 0;
	
	#print 'testing ' + test_string

	if test_string == error_string:
		return_val = 0
	elif test_string == good_string:
		return_val = 1
	else:
		#some other value discovered, do not allow...
		return_val = 0
		
	return return_val

#time script execution time roughly...
t0 = time.clock()

export_data()

#print script execution time...
print 'Execution time: ' + str(time.clock() - t0) + ' seconds.'