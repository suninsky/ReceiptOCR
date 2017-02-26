#!/usr/bin/env python

from __future__ import print_function
import commands  # execute tools
import sys       # get os
import argparse  # command line
import time      # sleep
import os        # check for root/sudo

# testing w/o actually running the update command
global_run = True


def isRoot():
	"""
	Am I root/sudo?
	out: True/False
	"""
	if os.geteuid() != 0:
		print('Root: False')
		return False
	else:
		print('Root: True')
		return True


def cmd(str, print_ret=False, usr_pwd=None, run=True):
	"""
	Executes a command and throws an exception on error.
	in:
		str - command
		print_ret - print command return
		usr_pwd - execute command as another user (user_name, password)
		run - really execute command?
	out:
		returns the command output
	"""
	if usr_pwd:
		str = 'echo {} | sudo -u {} {} '.format(usr_pwd[1], usr_pwd[0], str)

	print('  [>] {}'.format(str))

	if run:
		err, ret = commands.getstatusoutput(str)
	else:
		err = None
		ret = None

	if err:
		print('  [x] {}'.format(ret))
		raise Exception(ret)
	if ret and print_ret:
		lines = ret.split('\n')
		for line in lines:
			print('  [<] {}'.format(line))
	return ret


def getPackages(plist):
	"""
	Cleans up input from the command line tool and returns a list of package
	names
	"""
	nlist = plist.split('\n')
	pkgs = []
	for i in nlist:
		if i.find('===') > 0: continue
		pkg = i.split()[0]
		if pkg   == 'Warning:': continue
		elif pkg == 'Could': continue
		elif pkg == 'Some': continue
		elif pkg == 'You': continue
		elif not pkg: continue
		pkgs.append(pkg)

	print('  >> Found', len(pkgs), 'packages')

	return pkgs


def pip(usr_pswd=None):
	"""
	This updates one package at a time.

	Could do all at once:
		pip list --outdated | cut -d' ' -f1 | xargs pip install --upgrade
	"""
	# see if pip is installed
	try: cmd('which pip')
	except:
		return

	print('-[pip]----------')
	p = cmd('pip list --outdated')
	if not p: return
	pkgs = getPackages(p)

	# update pip and setuptools first
	for i, p in enumerate(pkgs):
		if p in ['pip', 'setuptools']:
			cmd('pip install -U ' + p, usr_pwd=usr_pswd, run=global_run)
			pkgs.pop(i)

	# update the rest of them
	for p in pkgs:
		cmd('pip install -U ' + p, usr_pwd=usr_pswd, run=global_run)


def brew(clean=False):
	"""
	Handle homebrew on macOS
	"""
	# see if homebrew is installed
	try: cmd('which brew')
	except:
		return

	print('-[brew]----------')
	cmd('brew update')
	p = cmd('brew outdated')
	if not p: return
	pkgs = getPackages(p)
	for p in pkgs:
		cmd('brew upgrade {}'.format(p), run=global_run)

	if clean:
		print(' > brew prune old sym links and cleanup')
		cmd('brew prune')
		cmd('brew cleanup')


def kernel():
	"""
	Handle linux kernel update
	"""
	print('================================')
	print('  WARNING: upgrading the kernel')
	print('================================')
	time.sleep(5)

	print('-[kernel]----------')
	cmd('rpi-update', True)
	print(' >> You MUST reboot to load the new kernel <<')


def aptget(clean=False):
	"""
	Handle linux apt-get updates
	"""
	print('-[apt-get]----------')
	cmd('apt-get update')
	cmd('apt-get -y -q upgrade ')
	if clean:
		cmd('apt-get autoremove')


def npm(usr_pwd=None, clean=False):
	"""
	Handle npm for Node.js
	"""
	# see if node is installed
	try: cmd('which npm')
	except:
		return

	print('-[npm]----------')
	# awk, ignore 1st line and grab 1st word
	p = cmd("npm outdated -g | awk 'NR>1 {print $1}'")
	if not p: return
	pkgs = getPackages(p)

	for p in pkgs:
		cmd('{} {}'.format('npm update -g ', p), usr_pwd=usr_pwd, run=global_run)


def getArgs():
	parser = argparse.ArgumentParser('A simple automation tool to update your system.')
	parser.add_argument('-k', '--kernel', help='update linux kernel, default is not too', action='store_true')
	parser.add_argument('-c', '--cleanup', help='cleanup after updates', action='store_true')
	args = vars(parser.parse_args())

	return args


def main():
	# get command line
	args = getArgs()

	system = sys.platform
	if system == 'darwin':
		print('OS: macOS')

		if isRoot(): raise Exception('Do not use root on macOS!')
		pip()
		brew(args['cleanup'])
		npm()

	elif system in ['linux', 'linux2']:
		print('OS: Linux')

		if not isRoot():
			raise Exception('You need to be root/sudo for linux ... exiting')

		pi = ('pi', 'raspberry')
		pip(pi)
		aptget(args['cleanup'])
		npm(pi)
		if args['kernel']: kernel()

	else:
		print('Your OS is not supported')


if __name__ == "__main__":
	main()
	# try:
	# 	ans = cmd('which npm')
	# 	print(ans)
	# 	ans = cmd('which abc')
	# 	print(ans)
	# except:
	# 	print('oops')
