import time
import functools
import numpy as np
import shutil
from datetime import datetime
from collections.abc import Iterable   
import os
import smtplib, ssl


class myDecorators:
    '''
    a set of convenient decorators, with global and local controls for logging / saving 
    '''
    
    def __init__(self,**kwargs):
        # set paths
        self.initialize_paths(**kwargs)
            
    # quick set for paths
    def initialize_paths(self,**kwargs):
        # set file location
        self.file_location = os.getcwd() + '/'
        if 'file_location' in kwargs:
            self.file_location = kwargs['file_location']
        
        if len(self.file_location[-1]) > 0:
            if self.file_location[-1] != '/':
                self.file_location += '/'
            
        # set file name
        self.file_name = 'test_file.txt'
        if 'file_name' in kwargs:
            self.file_name = kwargs['file_name']
            
        # set log name
        self.log_name = 'test_log.txt'
        if 'log_name' in kwargs:
            self.log_name = kwargs['log_name']
       
        # set bucket location 
        self.bucket_location = ''
        if 'bucket_location' in kwargs:
            self.bucket_location = kwargs['bucket_location']
            if len(self.bucket_location) > 0:
                if self.bucket_location[-1] != '/':
                    self.bucket_location += '/'
                
        self.reset_paths()

    def reset_files(self):
        '''
        clear files
        '''
        if os.path.exists(self.logpath):
            os.remove(self.logpath)
        if os.path.exists(self.filepath):
            os.remove(self.filepath)            
                    
    def reset_paths(self):
        '''
        reset paths to file, log, and bucket versions of both
        '''
        self.filepath = self.file_location + self.file_name
        self.logpath = self.file_location + self.log_name
        self.bucket_filepath = self.bucket_location + self.file_name
        self.bucket_logpath = self.bucket_location + self.log_name
            
            
    def try_it(self,func):
        '''
        try execution of function 'func'
        '''
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                message = 'FAILURE: function "' + func.__name__ + '" failed, EXECPTION: ' + str(e)
                return message
        return wrapper


    def time_it(self,func):
        '''
        time execution of input function 'func'
        '''
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            t0 = time.time()
            try_func = self.try_it(func)
            result = try_func(*args, **kwargs)
            t1 = time.time()
            print('total execution time',np.round(t1-t0,3),'seconds')
            return result
        return wrapper


    def just_log(self,message):
        # log start of execution
        dateTimeObj = datetime.now().replace(microsecond=0)
        print(dateTimeObj,message,file=open(self.logpath, "a"))
        
        
    def log_it(self,**log_info):
        '''
        convinent time-based logging execution of input function 'func'
        '''
        def log_decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                ### reset paths if desired ###
                if 'file_location' in log_info:
                    self.file_location = log_info['file_location']
                    if len(self.file_location) > 0:
                        if self.file_location[-1] != '/':
                            self.file_location += '/'
                        
                if 'log_name' in log_info:
                    self.log_name = log_info['log_name']
                        
                # reset paths
                self.reset_paths()

                # include custom message in log?
                custom_message = 'function "' + func.__name__ + '"'
                if 'custom_message' in log_info:
                    custom_message = log_info['custom_message']
                
                # reset log?
                reset_log=False
                if 'reset_log' in log_info:
                    reset_log = log_info['reset_log']
                    
                if reset_log == True:
                    if os.path.exists(self.logpath):
                        os.remove(self.logpath)

                # log start of execution
                dateTimeObj = datetime.now().replace(microsecond=0)
                message = custom_message + ' starting execution'
                print(dateTimeObj,'START:',message,file=open(self.logpath, "a"))

                # execute
                try_func = self.try_it(func)
                result = try_func(*args, **kwargs)

                # log failure response
                if isinstance(result,str):
                    if result[:7] == 'FAILURE':
                        dateTimeObj = datetime.now().replace(microsecond=0)
                        print(dateTimeObj,result,file=open(self.logpath, "a"))    
                        return result

                # log success      
                dateTimeObj = datetime.now().replace(microsecond=0)
                message = custom_message + ' executed properly'
                print(dateTimeObj,'SUCCESS:',message,file=open(self.logpath, "a"))
                return result
            return wrapper
        return log_decorator


    def save_it(self,**save_info):
        '''
        save output from execution of function 'func' to file
        '''
        def save_decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                ### reset paths if desired ###
                if 'file_location' in save_info:
                    self.file_location = save_info['file_location']
                    if len(self.file_location) > 0:
                        if self.file_location[-1] != '/':
                            self.file_location += '/'

                # define file_name
                if 'file_name' in save_info:
                    self.file_name = save_info['file_name']

                # log_name
                if 'log_name' in save_info:
                    self.log_name = save_info['log_name']
                    
                # reset paths
                self.reset_paths()
                    
                # reset log?
                reset_log=False
                if 'reset_log' in save_info:
                    reset_log = save_info['reset_log']

                # reset save file?
                reset_file = False
                if 'reset_file' in save_info:
                    reset_file = save_info['reset_file']

                if reset_file == True:
                    if os.path.exists(self.filepath):
                        os.remove(self.filepath)
                
                ### wrap function in logger - then execute ###
                log_func = self.log_it(file_location=self.file_location,reset_log=reset_log,log_name=self.log_name)(func)
                result = log_func(*args, **kwargs)
                
                # return instance of failure response
                if isinstance(result,str):
                    if result[:7] == 'FAILURE':   
                        return result
                        
                # otherwise - save result
                def save_data(result):
                    with open(self.filepath, 'a') as the_file:
                        the_file.write(str(result) + '\n')
                    return 1
                        
                # wrap saver in logger - then execute
                custom_message = '"save" of function "' + func.__name__ + '"'
                save_data = self.log_it(file_location=self.file_location,custom_message=custom_message,reset_log=reset_log,log_name=self.log_name)(save_data)

                # execute save
                save_data(result)
                
                # return result
                return result
            return wrapper
        return save_decorator

    
    def load_it(self,loadpath):
        # read in data
        file = open(loadpath, 'r') 
        lines = file.readlines() 
        lines = [eval(v) for v in lines]
        return lines


    def sync_it(self,**sync_info):
        '''
        sync the return value of a function to an s3 bucket, automatically calls save_it
        variables
        '''
        def sync_decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                ### reset paths if desired ###
                if 'file_location' in sync_info:
                    self.file_location = sync_info['file_location']
                    if len(self.file_location) > 0:
                        if self.file_location[-1] != '/':
                            self.file_location += '/'

                # define file_name
                if 'file_name' in sync_info:
                    self.file_name = sync_info['file_name']

                # log_name
                if 'log_name' in sync_info:
                    self.log_name = sync_info['log_name']
                    
                # reset log?
                reset_log = False
                if 'reset_log' in sync_info:
                    reset_log = sync_info['reset_log']

                # define bucket location
                if 'bucket_location' in sync_info:
                    self.bucket_location = sync_info['bucket_location']  
                    if len(self.bucket_location) > 0:
                        if self.bucket_location[-1] != '/':
                            self.bucket_location += '/'
                        
                # reset paths
                self.reset_paths()

                ### wrap function in save_it - then execute ###
                save_func = self.save_it(**sync_info)(func)
                result = save_func(*args, **kwargs)

                # sync functionality
                def sync():
                    # sync file
                    sync_command = 'aws s3 cp ' + self.filepath + ' ' + self.bucket_filepath
                    os.system(sync_command)
                    
                    # sync log
                    sync_command = 'aws s3 cp ' + self.logpath + ' ' + self.bucket_logpath
                    os.system(sync_command)                    
                    return 1
                    
                ### wrap saver in logger - and execute ###
                custom_message = '"sync" of data at ' + self.filepath + ' and log at ' + self.logpath
                sync = self.log_it(file_location=self.file_location,custom_message=custom_message,reset_log=reset_log,log_name=self.log_name)(sync)
                
                # run sync
                sync()
                             
                # return result
                return result
            return wrapper
        return sync_decorator
    
    
    def set_email_params(self,sender_email,receiver_email,password):
        '''
        store email params
        '''
        self.sender_email = sender_email
        self.receiver_email = receiver_email
        self.email_psswd = password
        
    def email_it(self,func):
        # email sender - just define the message
        def send_email(message):
            # Create secure connection with server and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.sender_email, self.email_psswd)
                server.sendmail(
                    sender_email, self.receiver_email, message
                )

        # wrap input function    
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            email_message = func.__name__

            try: # sucess
                # run function
                result = func(*args, **kwargs)

                # compose message to send
                message = 'Subject: SUCCESS: function "' + email_message    + '" completed!'
                message += '\n\n'
                message += 'SUCCESS: function "' + email_message    + '" completed!'
                send_email(message)
            except:
                # compose message to send
                message = 'Subject: FAILED: function "' + email_message    + '" failed!'
                message += '\n\n'         
                message = 'FAILED: function "' + email_message    + '" failed!'
                send_email(message)
        return wrapper
