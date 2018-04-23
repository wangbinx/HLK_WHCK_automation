#!/usr/bin/python
# -*- coding: UTF-8 -*-
#This script for Microsoft Windows Hardware Lab Kit tool automation.
#Windows Hardware Lab Kit: https://docs.microsoft.com/en-us/windows-hardware/test/hlk/what-s-new-in-the-hardware-lab-kit
#Detail document for HLK automation: https://docs.microsoft.com/en-us/windows-hardware/test/hlk/user/hlk-automation-tool
#
import os
import re
import platform
import subprocess
import xml.etree.ElementTree as xmlet


root =os.getcwd()

#call powershell
def powershell(command):
	args = ['Powershell',command]
	out = subprocess.Popen(args, shell=True,stdout=subprocess.PIPE)
	output = out.stdout.read()
	print "Output:%s"%output
	return output

def install_path():
	arch_dir={"AMD64":"Program Files (x86)","X86":"Program Files (x86)"}
	system_info = platform.uname()
	plat = system_info[0]
	plat_ver = system_info[2]
	version = system_info[3]
	arch = system_info[4]
	if plat == "Windows":
		print "System info:%s%s,%s,%s"%(plat,plat_ver,version,arch)
		server_install_dir = os.path.join("C:\\",arch_dir[arch],"Windows Kits",plat_ver,"Hardware Lab Kit","Studio")
		return server_install_dir
	else:
		print "Unkonwn install path"

#check HLK install
class create_task(object):
	PDEF_dir = os.path.join(root, 'PDEF')
	if not os.path.isdir(PDEF_dir):
		os.makedirs(PDEF_dir)
	# Create ProjectDefinition File
	ProjectDefinitionFile_exe = 'New-HwCertProjectDefinitionFile'
	ProjectDefinitionFile_path = os.path.join(PDEF_dir, 'PDEF.xml')
	ProjectDefinitionFile_command = '%s -MachinePool "Default Pool" -PdefFilePath %s -ProjectName "HLKTEST" -RunSystemTest' % (
	ProjectDefinitionFile_exe, ProjectDefinitionFile_path)
	# Create TestCollection File
	TestCollection_exe = 'New-HwCertTestCollection'
	TestCollectionFile_path = os.path.join(PDEF_dir, 'playlist.xml')
	TestPassIdentifier = "hlktest"
	TestCollection_command = '%s -ProjectDefinitionFile %s|Export-HwCertTestCollectionToXml -Output %s -TestPassIdentifier "%s"' % (
		TestCollection_exe,ProjectDefinitionFile_path, TestCollectionFile_path, TestPassIdentifier)
	#TestCollectionStatusLocation
	TestCollectionStatusLocation_path = os.path.join(PDEF_dir,'TestCollectionStatusLocation.xml')
	#Run task command
	Run_exe = os.path.join(install_path(),'hckexecutionengine.exe')
	Run_command = '%s /Project "%s" /RunCollection'%(Run_exe,ProjectDefinitionFile_path)

	def __init__(self):
		self.debugPreference = '$DebugPreference="Continue"'

	def set_debugPreference(self):
		print "Set debugPreference to Continue"
		return powershell(self.debugPreference)

	def projectdefinitionfile(self):
		print "Create Project Definition File"
		result = powershell(self.ProjectDefinitionFile_command)
		if os.path.isfile(self.ProjectDefinitionFile_path):
			return 1

	def testcollectionfile(self):
		print "Cre"
		result = powershell(self.TestCollection_command)
		self.not_use(result)
		if os.path.isfile(self.TestCollectionFile_path):
			return 1

	def not_use(self,result):
		not_used_machine_re = re.compile(r'Failed to find machine (\S+) in pool')
		not_used = not_used_machine_re.findall(result)
		if not_used:
			not_used = list(set(not_used))
			print "Find machine can't use in Default Pool:%s, remove it from XML file" %str(not_used)
			tree = xmlet.parse(self.ProjectDefinitionFile_path)
			root = tree.getroot()
			for notusemac in not_used:
				for pro in root.iter("Product"):
					for Mac in pro.iter('Machine'):
						if Mac.attrib["Name"] == notusemac:
							pro.remove(Mac)
							tree.write(self.ProjectDefinitionFile_path)
			result = powershell(self.TestCollection_command)

	def run(self):
		return self.Run_command

class XML(create_task):

	def __init__(self):
		super(XML,self).__init__()

	def addplaylist(self):
		tree = xmlet.parse(self.ProjectDefinitionFile_path)
		root = tree.getroot()
		for Pro in root.iter("Project"):
			Pro.attrib["TestCollectionReadLocation"] = self.TestCollectionFile_path
			Pro.attrib["TestCollectionStatusLocation"] = self.TestCollectionStatusLocation_path
			tree.write(self.ProjectDefinitionFile_path)
			return 1


def main():
	xml = XML()
	xml.set_debugPreference()
	definition = xml.projectdefinitionfile()
	if definition:
		collection = xml.testcollectionfile()
		if collection:
			add = xml.addplaylist()
			if add:
				print "Running"
				#task.run()

if __name__=='__main__':
	main()