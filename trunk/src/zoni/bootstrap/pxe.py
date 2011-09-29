# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.    
#
#  $Id$
#

import os 
import sys
import string
import datetime
import subprocess
import MySQLdb
import traceback
import logging

from zoni.extra.util import normalizeMac
from zoni.bootstrap.bootstrapinterface import BootStrapInterface

class Pxe(BootStrapInterface):
	def __init__(self, config, data, verbose=None):
		self.verbose  = verbose
		self.host = config['dbHost']
		self.user = config['dbUser']
		self.passwd = config['dbPassword']
		self.db = config['dbInst']
		
		self.tftpRootDir = config['tftpRootDir']
		self.tftpImageDir = config['tftpImageDir']
		self.tftpBootOptionsDir = config['tftpBootOptionsDir']
		self.tftpUpdateFile = config['tftpUpdateFile']
		self.tftpBaseFile = config['tftpBaseFile']
		self.tftpBaseMenuFile = config['tftpBaseMenuFile']
		self.initrdRoot = config['initrdRoot']
		self.kernelRoot = config['kernelRoot']

		self.log = logging.getLogger(os.path.basename(__file__))


		if config['dbPort'] == "":
			config['dbPort'] = 3306

		self.port = config['dbPort']

		self.vlan_max = config['vlanMax']
		
		self.data = data
		#self.vlan_reserved = config['vlanReserved']
		
		#data = instantiateImplementation("zoni.data.resourcequerysql.ResourceQuerySql", configs, options.verbosity)
		#  Connect to DB
		#self.conn = MySQLdb.connect(host = self.ho st, port = self.port, user = self.user, passwd = self.passwd, db = self.db)

		#cursor.execute ("SELECT VERSION()")
		#print "server version:", row[0]
		#mysql -Dirp-cluster -hrodimus -u reader -e "select * from hostinfo;"


		

	'''  This will create the update file tftpUpdateFile used to generate all the pxe boot files
		 pass in a list of available images	
	'''
	def createPxeUpdateFile (self, images):
		try: 
			f = open(self.tftpUpdateFile, "w")
		except Exception:
			traceback.print_exc(sys.exc_info())

		dadate = datetime.datetime.now().strftime("%Y%m%d.%H%M.%S")
		val = "#  Generated by ZONI  " + dadate
		f.write(val)
		for image in images:
			val = "\n#  IMAGE " + image + "\n"
			f.write(val)
			base = "cat " + self.tftpBaseFile + " | sed 's/MAGIC1/" + image + "/' > " + self.tftpBootOptionsDir + "/" + image + "\n"
			basemenu= "cat " + self.tftpBaseMenuFile + " | sed 's/LABEL " + image + "$/LABEL " + image + "\\n\\tMENU DEFAULT/' > " + self.tftpBootOptionsDir + "/" + image + "-menu\n" 
			f.write(base)
			f.write(basemenu)
		f.close()
		

	def updatePxe(self):
		cmd = "chmod 755 " + self.tftpUpdateFile
		try:
			os.system(cmd)
		except Exception:
			traceback.print_exc(sys.exc_info())

		cmd = self.tftpUpdateFile
		try:
			os.system(cmd)
		except Exception:
			traceback.print_exc(sys.exc_info())

	def generateBootOptions(self, image):
		name = self.tftpBootOptionsDir + "/" + image
		tftpdir = os.path.basename(self.tftpImageDir)
		bootdir = os.path.basename(self.tftpBootOptionsDir)
		imagedir = os.path.join(tftpdir, bootdir, image)

		#  Write out boot image file
		val = "DISPLAY boot-screens/boot.txt\n"
		val += "DEFAULT vesamenu.c32\n"
		val += "MENU BACKGROUND boot-screens/zoni_pxe.jpg\n"
		val += "PROMPT 0\n"
		
		val += "MENU COLOR border 49;37 #00FFFFFF #00FFFFFF none\n"
		val += "MENU INCLUDE %s-menu\n" % imagedir
		f = open(name, "w")
		f.write(val)
		f.close()

		
		#  Write out the menu file
		#  Eventually iterate over all images this machine should be able to select from
		name = self.tftpBootOptionsDir + "/" + image + "-menu"
		kOpt= self.data.getKernelOptions(image)
		kernelPath = os.path.join(self.kernelRoot, kOpt['kernel_arch'], kOpt['kernel_name'])
		initrdPath = os.path.join(self.initrdRoot, kOpt['kernel_arch'], kOpt['initrd_name'])
		val = "DISPLAY boot-screens/boot.txt\n\n"
		val += "LABEL %s\n" % kOpt['image_name']
		val += "	MENU DEFAULT\n"
		val += "	kernel %s\n" % kernelPath
		val += "	append initrd=%s %s\n" % (initrdPath, kOpt['initrd_options'])

		f = open(name, "w")
		f.write(val)
		f.close()

		

	def setBootImage(self, mac, image):
		mac_addr = "01-" + string.replace(normalizeMac(mac), ":", "-")
		maclink = self.tftpImageDir + "/" + mac_addr
		self.generateBootOptions(image)
		#  Check if it exists first
		if os.path.exists(maclink):
			try:
				os.unlink(maclink)
			except Exception, e:
				traceback.print_exc(sys.exc_info())
				if OSError:
					print OSError, e
					mesg = "ERROR : %s\n" % e
					self.log.error(mesg)
					return 1
				return 1
		#  Create the boot option file
		#  Relink
		newlink = os.path.basename(self.tftpBootOptionsDir) + "/" + image
		try:
			os.symlink(newlink, maclink)
			mesg = "Image assignment Successful %s -> %s " % (mac, image)
			self.log.info(mesg)
		except Exception, e:
			if OSError:
				#mesg = "Cannot modify file.  Please use sudo\n"
				mesg = "ERROR : %s\n" % e
				self.log.info(mesg)
				return 1
			return 1

		
