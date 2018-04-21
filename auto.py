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


root =os.getcwd()
PDEF_dir = os.path.join(root,'PDEF')
#Create ProjectDefinition File and TestCollection File
ProjectDefinitionFile_exe = 'New-HwCertProjectDefinitionFile'
ProjectDefinitionFile_dir = os.path.join(PDEF_dir,'PDEF.xml')
TestCollection_exe = 'New-HwCertTestCollection'
TestCollectionFile_dir = os.path.join(PDEF_dir,'playlist.xml')
TestPassIdentifier = "hlktest"
ProjectDefinitionFile_command = '%s -MachinePool "Default Pool" -PdefFilePath %s -TestCollectionFilePath %s -ProjectName "HLKTEST" -RunSystemTest'%(ProjectDefinitionFile_exe,ProjectDefinitionFile_dir,TestCollectionFile_dir)
TestCollection_command = '-ProjectDefinitionFile %s|Export-HwCertTestCollectionToXml -Output %s -TestPassIdentifier "%s"'%(ProjectDefinitionFile_dir,TestCollectionFile_dir,TestPassIdentifier)

#call powershell
def powershell(command):
	args = ['Powershell',command]
	out = subprocess.Popen(args, shell=True,stdout=subprocess.PIPE)
	output = out.stdout.read()
	print output
	return output

def install_path():
	arch_dir={"AMD64":"Program Files","X86":"Program Files (x86)"}
	system_info = platform.uname()
	plat = system_info[0]
	plat_ver = system_info[2]
	version = system_info[3]
	arch = system_info[4]
	if plat == "Windows":
		server_install_dir = os.path.join("C:\\",arch_dir[arch],"Windows Kits",plat_ver,"Hardware Lab Kit","Studio")
		return server_install_dir
	else:
		print "Unkonwn install path"

#check HLK install
class create_task(object):
	PDEF_dir = os.path.join(root, 'PDEF')
	# Create ProjectDefinition File
	ProjectDefinitionFile_exe = 'New-HwCertProjectDefinitionFile'
	ProjectDefinitionFile_dir = os.path.join(PDEF_dir, 'PDEF.xml')
	ProjectDefinitionFile_command = '%s -MachinePool "Default Pool" -PdefFilePath %s -ProjectName "HLKTEST" -RunSystemTest' % (
	ProjectDefinitionFile_exe, ProjectDefinitionFile_dir)
	# Create TestCollection File
	TestCollection_exe = 'New-HwCertTestCollection'
	TestCollectionFile_dir = os.path.join(PDEF_dir, 'playlist.xml')
	TestPassIdentifier = "hlktest"
	TestCollection_command = '-ProjectDefinitionFile %s|Export-HwCertTestCollectionToXml -Output %s -TestPassIdentifier "%s"' % (
	ProjectDefinitionFile_dir, TestCollectionFile_dir, TestPassIdentifier)

	def __init__(self):
		self.debugPreference = '$DebugPreference="Continue"'

	def set_debugPreference(self):
		return powershell(self.debugPreference)

	def projectdefinitionfile(self):
		result = powershell(self.ProjectDefinitionFile_command)
		if result:
			return 1

	def testcollectionfile(self):
		result = powershell(self.TestCollection_command)
		if result:
			return 1


class XML(create_task):

	def __init__(self):
		super(create_task,self).__init__()

	def projectdefinition(self):
		self.projectdefinitionfile()

#Run task command
Run_exe = os.path.join(install_path(),'hckexecutionengine.exe')
Run_command = '%s /Project "%s" /RunCollection'%(Run_exe,ProjectDefinitionFile_dir)


if __name__=='__main__':
	#main()
	xml=XML()