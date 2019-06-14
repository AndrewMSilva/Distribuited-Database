import Settings.Function as Function
import Modules.Validator as Validator
import Modules.Communicator as Communicator
import Modules.Database as Database

def Execute(cmd):
	cmd = Validator.Read(cmd)

	if(isinstance(cmd,list)):
		if cmd[0] == Function.Include:
			Communicator.Include(cmd[1])
		elif cmd[0] == Function.ShowGroup:
			Communicator.ShowGroup()
		elif cmd[0] == Function.QuitGroup:
			Communicator.QuitGroup()
		elif cmd[0] == Function.CreateTable:
			CreateTable(cmd[1:])
		elif cmd[0] == Function.InsertInto:
			InsertInto(cmd[1:])
		elif cmd[0] == Function.DeleteFrom:
			DeleteFrom(cmd[1:])
		elif cmd[0] == Function.Select:
			Select(cmd[1:])
		elif cmd[0] == Function.ShowTable:
			ShowTable(cmd[1:])

def CreateTable(cmd):
	Database.CreateTable(cmd)

def InsertInto(cmd):
	Database.InsertInto(cmd)

def DeleteFrom(cmd):
	Database.DeleteFrom(cmd)

def Select(cmd):
	Database.Select(cmd)

def ShowTable(cmd):
	Database.ShowTable(cmd)