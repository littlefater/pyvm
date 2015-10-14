#!/usr/bin/env python
"""
VMWare control tool Python wrapper
""" 

import os
import time
import subprocess

class VMControl:
    
    def __init__(self, vmrun_path, vm_path, guest_user = 'admin', guest_pass = 'admin', debug = False):
        '''Init VMWare Control class'''

        self.vmrun_path = vmrun_path
        self.vm_path = vm_path
        self.guest_user = guest_user
        self.guest_pass = guest_pass
        self.debug = debug

        self.debug_print('VMPath: ' + self.vm_path)
        self.debug_print('User: ' + self.guest_user)
        self.debug_print('Pass: ' + self.guest_pass)
        self.debug_print('VMRun: ' + self.vmrun_path)

    def exec_command(self, command):
        '''Execute command'''

        self.debug_print('Execute: ' + ' '.join(command))
        
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        output = proc.stdout.read()
        if output != '':
            self.debug_print('Output: ' + output)
        return output

    def revert_snapshot(self, vm_snapshot):
        '''Revert snapshot'''

        self.debug_print('Revert VM: "' + self.vm_path + '" to snapshot ' + vm_snapshot)
        output = self.exec_command([self.vmrun_path, '-T', 'ws', 'revertToSnapshot', self.vm_path, vm_snapshot])
        if output != '':
            self.debug_print('Revert snapshot fail.')
            return False
        
        self.debug_print('Start VM: ' + self.vm_path)
        output = self.exec_command([self.vmrun_path, '-T', 'ws', 'start', self.vm_path])
        if output != '':
            self.debug_print('Start VM fail.')
            return False
        
        return True

    def upload_file(self, file_src, file_dest):
        '''Upload file to Guest machine'''
        
        if os.path.isfile(file_src):
            self.debug_print('Copy host file ' + file_src + ' to VM path ' + file_dest)
            
            output = self.exec_command([self.vmrun_path, '-T', 'ws', '-gu', self.guest_user, '-gp', self.guest_pass, 'copyFileFromHostToGuest', self.vm_path, file_src, file_dest])
            if output != '':
                self.debug_print('Copy file from host to VM fail.')
                return False
        else:
            self.debug_print('Invalid host file!')
            return False
        
        return True

    def download_file(self, file_src, file_dest):
        '''Download file from Guest machine'''
        
        if self.file_exists(file_src):
            self.debug_print('Copy VM file ' + file_src + ' to host path ' + file_dest)
            
            output = self.exec_command([self.vmrun_path, '-T', 'ws', '-gu', self.guest_user, '-gp', self.guest_pass, 'copyFileFromGuestToHost', self.vm_path, file_src, file_dest])
            if output != '':
                self.debug_print('Copy file from VM to host fail.')
                return False
        else:
            return False
        
        return True

    def create_dir(self, dir):
        '''Create directory in Guest machine'''

        self.debug_print('Create directory in VM: ' + dir)
        
        output = self.exec_command([self.vmrun_path, '-T', 'ws', '-gu', self.guest_user, '-gp', self.guest_pass, 'createDirectoryInGuest', self.vm_path, dir])
        if output != '':
            self.debug_print('Create directory in VM fail.')
            return False
        
        return True
    
    def suspend(self):
        '''Suspend Guest machine'''

        self.debug_print('Suspend VM: ' + self.vm_path)
        
        output = self.exec_command([self.vmrun_path, '-T', 'ws', 'suspend', self.vm_path])
        if output != '':
            self.debug_print('Suspend VM fail.')
            return False
        
        return True

    def file_exists(self, filename):
        '''Check file existence in Guest machine'''

        self.debug_print('Check file: ' + filename)
        
        output = self.exec_command([self.vmrun_path, '-T', 'ws', '-gu', self.guest_user, '-gp', self.guest_pass, 'fileExistsInGuest', self.vm_path, filename])
        if -1 != output.find('The file exists.'):
            return True
        
        return False

    def execute_process(self, program, arguments = None, mode = '-noWait', show = False):
        '''Create process in Guest machine'''
        
        if arguments is not None:
            self.debug_print('Execute ' + program + ' in VM with arguments: ' + arguments)

            if show:
                output = self.exec_command([self.vmrun_path, '-T', 'ws', '-gu', self.guest_user, '-gp', self.guest_pass, 'runProgramInGuest', self.vm_path, mode, '-activeWindow', program, arguments])
            else:
                output = self.exec_command([self.vmrun_path, '-T', 'ws', '-gu', self.guest_user, '-gp', self.guest_pass, 'runProgramInGuest', self.vm_path, mode, program, arguments])
        else:
            self.debug_print('Execute ' + program + ' in VM.')

            if show:
                output = self.exec_command([self.vmrun_path, '-T', 'ws', '-gu', self.guest_user, '-gp', self.guest_pass, 'runProgramInGuest', self.vm_path, '-activeWindow', mode, program])
            else:
                output = self.exec_command([self.vmrun_path, '-T', 'ws', '-gu', self.guest_user, '-gp', self.guest_pass, 'runProgramInGuest', self.vm_path, mode, program])

        if mode == '-noWait' and output != '':
            return False

        if mode != '-noWait' and -1 == output.find('exit code: 1'):
            return False
            
        return True

    def debug_print(self, msg):
        if self.debug:
            print '\r\n[*] ' + msg


        