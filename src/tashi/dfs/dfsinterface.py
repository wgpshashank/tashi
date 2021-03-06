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

class DfsInterface:
	def __init__(self, config):
		if self.__class__ is DfsInterface:
			raise NotImplementedError
		self.config = config
	
	def copyTo(self, localSrc, dst):
		raise NotImplementedError
	
	def copyFrom(self, src, localDst):
		raise NotImplementedError
	
	def list(self, path):
		raise NotImplementedError
	
	def stat(self, path):
		raise NotImplementedError
	
	def move(self, src, dst):
		raise NotImplementedError
	
	def copy(self, src, dst):
		raise NotImplementedError
	
	def mkdir(self, path):
		raise NotImplementedError
	
	def unlink(self, path):
		raise NotImplementedError
	
	def rmdir(self, path):
		raise NotImplementedError
	
	def open(self, path, perm):
		raise NotImplementedError
	
	def getLocalHandle(self, path):
		raise NotImplementedError
