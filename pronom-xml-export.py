"""Script to export PRONOM XML from PRONOM."""
import configparser as ConfigParser
import os
import time
import sys
import urllib.request as urllib2

puid_type_list = ['x-fmt', 'fmt', 'x-cmp', 'cmp', 'x-chr', 'chr', 'x-sfw', 'sfw']

config = ConfigParser.RawConfigParser()
config.read('pronom-xml-export.cfg')

puid_dict = {}

for type in puid_type_list:
   tmpint = config.getint('puids', type)
   if tmpint > 0:
      puid_dict[type] = tmpint

good_string=config.get('doctypes', 'good-string')

#url through which to access Pronom data...
base_url=config.get('urls', 'base-url')

def export_data():

   proxy = ''
   
   # Uncomment this to enable use of a proxy, and ensure that the port
   # number can resolve to an integer, e.g. 'dummy@host:2313'
   #
   # proxy = urllib2.ProxyHandler({'http': 'dummy@host:port'})

   for puid_type in puid_dict.keys():
      puid_type_url = base_url + puid_type + '/'
      current_dir = os.getcwd()
      new_dir = os.getcwd() + '//' + config.get('locations', 'export') + '//' + puid_type + '//'
      
      try:
         os.makedirs(new_dir)
      except OSError as err:
         print(err, file=sys.stderr)

      #change to expor directory to store xml...
      os.chdir(new_dir)
      
      #urlib code here...
      puid_no = puid_dict[puid_type]

      for i in range(1, puid_no + 1):
         filename = puid_type + str(i) + '.xml'
         puid_url = puid_type_url + str(i) + '.xml'
         
         request = urllib2.Request(puid_url)
         
         if proxy != '':
            opener = urllib2.build_opener(proxy)
         else:
            opener = urllib2.build_opener()
         
         request.add_header('User-Agent', 'exponentialDK-PRONOM-Export/0.0.0')
         
         print(puid_url, file=sys.stderr)

         url = opener.open(request)
         
         test_string = url.read(14)
         
         if check_record(test_string):
            f = open(filename, 'wb')
            f.write(test_string + url.read())
            f.close()
         else:
            print("Not writing record: {}".format(test_string), file=sys.stderr)

      #revert back to original directory...
      os.chdir(current_dir)		


def check_record(test_string):
   """Ensure that a test_string doesn't equal an error string.

   :param test_string:  A snippet of string to compare against an error
         string.
   :return: True or False (Boolean)
   """
   if test_string.decode("utf8") == good_string:
      return True
   return False

#time script execution time roughly...
t0 = time.perf_counter()

export_data()

#print script execution time...
print('Execution time: ' + str(time.perf_counter() - t0) + ' seconds.', file=sys.stderr)
