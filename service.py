#!/usr/bin/env python
import subprocess
import os
import signal
import threading

# < include utils.py >

import utils

CLASS_NAME="Service"
utils.ROOT=ROOT=utils.get_root_directory(CLASS_NAME)
utils.TEMPDIR=TEMPDIR=utils.get_tempdir()

NAMES,FLAGS,FUNCTION=utils.extract_arguments()

utils.NAMES=NAMES
utils.ROOT=ROOT
utils.GLOBALS=globals()

SHELL=os.getenv('SHELL','bash')
SHELL_CWD=os.environ.get("PWD")

def list_services(*args, **kwargs):
    return utils.list_items_in_root(*args, FLAGS,CLASS_NAME,**kwargs)    

def flatten(*args, **kwargs):
    return utils.flatten_list(*args, **kwargs)

def print_result(*args, **kwargs):
    return utils.print_list(*args, **kwargs)

def split_by_char(*args, **kwargs):
    return utils.split_by_char(*args, **kwargs)


ServiceDoesNotExist=utils.DoesNotExist
    
class Service:
    def __init__(self,_name,_flags=None,_function=None,_env=None,_workdir='.'):
        self.Class = utils.Class(self,CLASS_NAME.lower())
        self.Class.class_init(_name,_flags,_function,_workdir)
        
        self.env=utils.get_value(_env,f"export SERVICE_NAME={self.name}")
        
        self.temp_services=[]
    
    #Functions to be used in *service.py
    def Run(self,command="",pipe=False,track=True):
        with open(f"{TEMPDIR}/service_{self.name}.log","a+") as log_file:
            log_file.write(f"Command: {command}\n")
            log_file.flush()

            #Pipe output to variable
            if pipe:
                stdout=subprocess.PIPE
                stderr=subprocess.DEVNULL
            #Print output to file
            else:
                stdout=log_file
                stderr=subprocess.STDOUT
            return utils.shell_command(f"{self.env if track else 'true'}; cd {self.workdir}; {command}",stdout=stdout,stderr=stderr,arbitrary=True)
    
    def Ps(self,process=None):
        
        #Find main process
        if process=="main" or ("--main" in self.flags):
            return self.Class.get_main_process()
            
        #Find processes running under main Start script
        elif process=="auxiliary" or ("--auxiliary" in self.flags):
            processes=utils.shell_command(["ps","auxwwe"]).splitlines()
            processes=[_.split()[1] for _ in processes if f"SERVICE_NAME={self.name}" in _]
            return list(map(int,processes))

    
    def Env(self,*args, **kwargs):
        self.env=utils.add_environment_variable_to_string(self.env,*args, **kwargs)
    
    def Container(self,_container=None):
        #Convience --- if conainer name is not specified, it will assume that the container is the same name as the service
        
        if not _container:
            _container=self.name
            
        self.Down(f"container stop {_container}")
        self.Run(f"container start {_container}",track=False)
        
        
        with open(f"{TEMPDIR}/service_{self.name}.log","a+") as f:
            utils.shell_command(["tail","-f","-n","+1",f"{TEMPDIR}/container_{_container}.log"],stdout=f,block=False,env=os.environ.copy().update({"SERVICE_NAME":self.name}))
        
        container_main_pid=utils.shell_command(["container","ps","--main",_container],stdout=subprocess.PIPE)
        
        #Wait until container ends
        try:
            container_main_pid=int(container_main_pid)
            utils.wait_until_pid_exits(container_main_pid)
        except ValueError:
            pass
    
    def Down(self,func):
        #Yes, this decorator stuff is absolutely neccessary, anything else will not work
    
        if isinstance(func,str):
            #So func won't be overwritten
            func_str=func
            def func():
                utils.shell_command(func_str,arbitrary=True)
        def decorator_Exit(exit_func,func):
            def new_Exit(*args, **kwargs):
                exit_func(*args, **kwargs)
                func()
            return new_Exit
        self.Exit=decorator_Exit(self.Exit,func)
        
        #Kill all auxiliary processes when exiting
        def Exit_add_on():
            for pid in self.Ps("auxiliary"):
                utils.kill_process_gracefully(pid)
            exit()
        signal.signal(signal.SIGTERM,decorator_Exit(self.Exit,Exit_add_on))
        
    def Loop(self,*args, **kwargs):
        self.Class.loop(*args, **kwargs)
        #Run(f'(while true; do "{command}"; sleep {delay}; done)')

    def Wait(self,*args, **kwargs):
        utils.wait(*args, **kwargs)
    
    def Exit(self,signum,frame):
        pass
    
    def Dependency(self,service):
        if "Stopped" in utils.shell_command(["service","status",service]):
            #self.temp_services.append(service)
            #Kill service when stopping
            self.Down(lambda : utils.shell_command(["service","stop",service]))
            #utils.shell_command(["service","start",service])
            self.Run(f"service start {service}",track=False)
    #Commands      
    def Start(self):
        
        if "Started" in self.Status():
            return f"Service {self.name} is already started"
        
        if os.path.exists("data"):
            os.chdir("data")
        
        if "Enabled" in self.Status():
            service_file="service.py"
        else:
            service_file=".service.py"
        
        #Fork process, so it can run in the background
        pid=os.fork()
        
        #If child, run code, then exit 
        if pid==0:
            
            #Have a lambda that does nothing to make sure the SIGTERM handler is added right
            self.Down(lambda : None)
            
            #Open a lock file so I can find it with lsof later
            lock_file=open(f"{TEMPDIR}/service_{self.name}.lock","w+")
            
            #Run *service.py
            with open(f"{ROOT}/{self.name}/{service_file}") as f:
                code=f.read()
            exec(code,globals(),locals())
            
            #Don't exit script yet.
            self.Wait()
            exit()
       
    def Stop(self):
        return [self.Class.stop()]
        
    def Restart(self):
        return self.Class.restart()
    
    
    def List(self):
        return self.Class.list()
    
    def Workdir(self,work_dir):
        self.Class.workdir(work_dir)

    def Init(self):
        os.makedirs(f"{ROOT}/{self.name}",exist_ok=True)
        os.chdir(f"{ROOT}/{self.name}")
        os.makedirs("data",exist_ok=True)
        with open(f".{CLASS_NAME.lower()}.py",'a'):
            pass
        
        if '--no-edit' not in self.flags:
            self.Edit()

    def Edit(self):
        self.Class.edit()
    def Status(self):
        return self.Class.status()
    
    def Enable(self):
        return self.Class.enable()

            
    def Disable(self):
        return self.Class.disable()

    def Log(self):
        self.Class.log()
    
    def Delete(self):
        self.Class.delete()
    
    def Watch(self):
        self.Class.watch()


NAMES=list_services(NAMES)
for name in NAMES: 
    try:
        service=Service(name,FLAGS,FUNCTION)
    except ServiceDoesNotExist:
        print(f"Service {name} does not exist")
        continue
    
    utils.export_methods_globally(CLASS_NAME)
    
    result=utils.execute_class_method(eval(f"{CLASS_NAME.lower()}"),FUNCTION)
    print_result(result)
        

    
