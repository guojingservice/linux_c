#!/usr/bin/python


"""
example: 
    t = tail.Tail('file')
    t.register_callback(callback);


"""

import os
import sys
import time
import stat

class Tail(object):
    def __init__(self, tailed_file):

        self.check_file_validate(tailed_file);
        self.tailed_file = tailed_file
        self.callback = sys.stdout.write
        self.key_arr = []
        self.last_inode = 0
        file_stats = os.stat(self.tailed_file)
        self.last_file_size = file_stats.st_size

    def update_file_records(self):
        ret = self.validate_file(self.tailed_file)
        if(1==ret):
            return
        try:
            file_stats = os.stat(self.tailed_file)
            #这里如果发生 logrotate 需要处理这种情况
            #实际上, 这里st_size的更新只能变大，不能变小,logrotate 发生在这里就保留上次文件大小，废弃本次更改
            if self.last_file_size > file_stats.st_size:
                pass
            else:         
                self.last_inode = file_stats.st_ino
                self.last_file_size = file_stats.st_size
        except OSError, e:
            time.sleep(1)
            return


    def follow(self, s=1, is_new=False):
        fail_count=0
        file_stats = os.stat(self.tailed_file)
        current_inode = file_stats.st_ino
        current_file_size = file_stats.st_size
        
        with open(self.tailed_file) as file_:
            if(current_file_size < self.last_file_size):
                file_.seek(0)
            else:
                file_.seek(self.last_file_size)
            while True:
                curr_position = file_.tell()
                line = file_.readline()
                if not line:
                    file_.seek(curr_position)
                    fail_count +=1
                    #with propriate method to detect logrotate, temperily use this
                    if(fail_count > 10):
                        time.sleep(0.1)
                        break
                else:
                    self.handle_line(line)
                    self.update_file_records()
                    fail_count=0
                
        return 1
    
    def validate_file(self, file_):
        if not os.access(file_, os.F_OK):
            return 1
        if not os.access(file_, os.R_OK):
            return 1
        if os.path.isdir(file_):
            return 1
        return 0
    
    def routine(self):
        while True:
            if( 1 == self.validate_file(self.tailed_file)):
                time.sleep(1)
                continue
            ret = self.follow()

    def handle_line(self, line):
        if(len(self.key_arr) > 0):
            for key_str in self.key_arr:
                if line.find(key_str) != -1:
                    self.callback(line)
                    return 
        else:
            self.callback(line)

    def register_calllback(self, func):
        self.callback = func

    def check_file_validate(self, file_):
        if not os.access(file_, os.F_OK):
            raise TailError("File '%s' do not exist" %(file_));
        if not os.access(file_, os.R_OK):
            raise TailError("File '%s' not readable"%(file_));
        if os.path.isdir(file_):
            raise TailError("File '%s', is a directory"%(file_));

    def set_key_string(self, str_arr=[]):
        self.key_arr=str_arr
        
class TailError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message
