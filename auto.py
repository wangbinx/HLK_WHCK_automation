#!/usr/bin/python
# -*- coding: UTF-8 -*-
#This script for Microsoft Windows Hardware Lab Kit tool automation.
#Windows Hardware Lab Kit: https://docs.microsoft.com/en-us/windows-hardware/test/hlk/what-s-new-in-the-hardware-lab-kit
#Detail document for HLK automation: https://docs.microsoft.com/en-us/windows-hardware/test/hlk/user/hlk-automation-tool
#
import os
import sys
import re
import platform
import subprocess
import xml.etree.ElementTree as xmlet
from optparse import OptionParser


root =os.getcwd()

#call powershell
def powershell(command):
	args = ['Powershell',command]
	out = subprocess.Popen(args, shell=True,stdout=subprocess.PIPE)
	output = out.stdout.read()
	print "Output:%s"%output
	return output

def install_path():
	arch_dir={"AMD64":'"Program Files (x86)"',"X86":'"Program Files (x86)"'}
	system_info = platform.uname()
	plat = system_info[0]
	plat_ver = system_info[2]
	version = system_info[3]
	arch = system_info[4]
	if plat == "Windows":
		print "System info:%s%s,%s,%s"%(plat,plat_ver,version,arch)
		server_install_dir = os.path.join("C:\\",arch_dir[arch],'"Windows Kits"',plat_ver,'"Hardware Lab Kit"',"Studio")
		return server_install_dir
	else:
		print "Unkonwn install path"

#check HLK install
class create_task(object):

	def __init__(self,Machine_Pool):
		self.PDEF_dir = os.path.join(root, 'PDEF')
		self.Machine_Pool = Machine_Pool
		if not os.path.isdir(self.PDEF_dir):
			os.makedirs(self.PDEF_dir)
		# Create ProjectDefinition File
		ProjectDefinitionFile_exe = 'New-HwCertProjectDefinitionFile'
		self.ProjectDefinitionFile_path = os.path.join(self.PDEF_dir, 'PDEF_File.xml')
		self.ProjectDefinitionFile_command = '%s -MachinePool "%s" -PdefFilePath %s -ProjectName "HLKTEST" -RunSystemTest' % (
			ProjectDefinitionFile_exe, self.Machine_Pool, self.ProjectDefinitionFile_path)
		# Create TestCollection File
		self.TestCollection_exe = 'New-HwCertTestCollection'
		self.TestCollectionFile_path = os.path.join(self.PDEF_dir, 'all_test_playlist.xml')
		self.TestPassIdentifier = "hlktest"
		# TestCollectionStatusLocation
		self.TestCollectionStatusLocation_path = os.path.join(self.PDEF_dir, 'TestCollectionStatusLocation.xml')
		# Run task command
		Run_exe = os.path.join(install_path(), 'hckexecutionengine.exe')
		self.Run_command = '%s /Project "%s" /RunCollection' % (Run_exe, self.ProjectDefinitionFile_path)
		self.debugPreference = '$DebugPreference="Continue"'

	def set_debug_preference(self):
		print "Set debugPreference to Continue"
		return powershell(self.debugPreference)

	def project_definition_file(self):
		print "Create Project Definition File"
		result = powershell(self.ProjectDefinitionFile_command)
		if os.path.isfile(self.ProjectDefinitionFile_path):
			print "Create Project Definition File Finish"
			return 1

	def test_collection_file(self):
		print "Create Test Collection File"
		self.TestCollection_command = '%s -ProjectDefinitionFile %s|Export-HwCertTestCollectionToXml -Output %s -TestPassIdentifier "%s"' % (
			self.TestCollection_exe, self.ProjectDefinitionFile_path, self.TestCollectionFile_path, self.TestPassIdentifier)
		result = powershell(self.TestCollection_command)
		if not self.no_machine_can_use(result):
			if self.remove_not_use_machine(result):
				powershell(self.TestCollection_command)
			if os.path.isfile(self.TestCollectionFile_path):
				print "Create Test Collection File Finish"
				return True

	def remove_not_use_machine(self,text):
		print "Remove the can't be used machine"
		not_used_machine_re = re.compile(r'Failed to find machine (\S+) in pool')
		machine = not_used_machine_re.findall(text)
		if machine:
			machine = list(set(machine))
			print "Find machine can't use in %s:%s, remove it from XML file" %(self.Machine_Pool,str(machine))
			tree = xmlet.parse(self.ProjectDefinitionFile_path)
			root = tree.getroot()
			for name in machine:
				for pro in root.iter("Product"):
					for Mac in pro.iter('Machine'):
						if Mac.attrib["Name"] == name:
							pro.remove(Mac)
							tree.write(self.ProjectDefinitionFile_path)
			print "Remove machine form XML finish"
			return True
		return False

	def no_machine_can_use(self,text):
		print "Check if have machine can be used"
		no_machine_re = re.compile(r'No matching system under test found in machine pool')
		result = no_machine_re.search(text)
		if result:
			print 'Machine Pool %s no machine under test, please check the machine status is "Ready"'
			sys.exit()
		else:
			return False

	def run(self):
		return subprocess.check_call(self.Run_command,shell=True)

class XML(create_task):

	def __init__(self,Machine_Pool):
		super(XML,self).__init__(Machine_Pool)

	#Add playlist to Project Definition File
	def addplaylist(self):
		print "Add playlist to Project Definition File"
		tree = xmlet.parse(self.ProjectDefinitionFile_path)
		root = tree.getroot()
		for Pro in root.iter("Project"):
			Pro.attrib["TestCollectionReadLocation"] = self.TestCollectionFile_path
			Pro.attrib["TestCollectionStatusLocation"] = self.TestCollectionStatusLocation_path
			tree.write(self.ProjectDefinitionFile_path)
			print "Add playlist to Project Definition File Finish"
			return 1

class runtest(XML):

	def __init__(self,pool):
		self.machinepool = pool
		super(runtest,self).__init__(self.machinepool)

	def run_all_test(self):
		print "Run all system test"
		if self.project_definition_file():
			self.TestCollectionFile_path = os.path.join(self.PDEF_dir, 'all_test_playlist.xml')
			if self.test_collection_file():
				if self.addplaylist():
					print "Running"
					#self.run()

	def run_custom_test(self,playlist):
		print "Run playlist file:%s"%playlist
		if self.project_definition_file():
			self.TestCollectionFile_path = os.path.join(self.PDEF_dir, 'tmp.xml')
			if self.test_collection_file():
				os.remove(self.TestCollectionFile_path)
				self.TestCollectionFile_path = playlist
				if self.addplaylist():
					print "Running"


def main():
	usage = 'Script.py -m <Machine Pool>'
	parser = OptionParser(usage)
	parser.add_option('-m', '--machinepool', metavar = 'Machine Pool name', dest = 'pool', default = 'Default Pool' ,help = 'The Machine Pool name which test machine in, eg:"Default Pool"' )
	(options, args) = parser.parse_args()
	if options.pool == 'Default Pool':
		raw_input('No Machine Pool input, default pool is "Default Pool", press Enter to continue')
	Machine_Pool = options.pool
	Run = runtest(Machine_Pool)
	task = raw_input("Please select task:\n1.Run all test(All system task)\n2.Run custom task(use custom playlist)\n")
	if task == "1":
		Run.run_all_test()
	elif task == "2":
		playlist = os.path.abspath(raw_input("Please input Test Collection File:\n"))
		Run.run_custom_test(playlist)

if __name__=='__main__':
	main()