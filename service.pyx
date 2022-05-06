#!/usr/bin/env python
import subprocess
import os
import signal
import threading

< include utils.pyx >

CLASS_NAME="Service"
ROOT=utils.get_root_directory(CLASS_NAME)

NAMES,FLAGS,FUNCTION=utils.extract_arguments()

TEMPDIR=utils.TEMPDIR

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
    
def Shell(*args, **kwargs):
    return utils.shell_command(*args, **kwargs)


ServiceDoesNotExist=utils.DoesNotExist
    
class Service:
    def __init__(self,_name,_flags=None,_function=None,_env=None):
        self.Class = utils.Class(self,CLASS_NAME.lower())
        self.Class.class_init(_name,_flags,_function)
        
        self.env=utils.get_value(_env,f"export SERVICE_NAME={self.name}")
    
    #Functions to be used in *service.py
    def Run(self,command="",pipe=False):
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
            return Shell(f"{self.env}; {command}",stdout=stdout,stderr=stderr,arbitrary=True)
    
    def Ps(self,process="auxiliary"):
        
        #Find main process
        if process=="main":
            return self.Class.get_main_process()
            
        #Find processes running under main Start script
        elif process=="auxiliary":
            processes=Shell(["ps","auwwe"]).splitlines()
            processes=[_.split()[1] for _ in processes if f"SERVICE_NAME={self.name}" in _]
            return list(map(int,processes))

    
    def Env(self,*args, **kwargs):
        self.env=utils.add_environment_variable_to_string(self.env,*args, **kwargs)
    
    def Container(self,_container=None):
        #Convience --- if conainer name is not specified, it will assume that the container is the same name as the service
        
        if not _container:
            _container=self.name
            
        self.Down(f"container stop {_container}; sleep 1")
        self.Run(f"container start {_container}")
        
        #Wait 2 seconds before beginning
        self.Wait(2)
        with open(f"{TEMPDIR}/service_{self.name}.log","a+") as f:
            Shell(["tail","-f","-n","+1",f"{TEMPDIR}/container_{_container}.log"],stdout=f,block=False)
    
    def Down(self,func):
        #Yes, this decorator stuff is absolutely neccessary, anything else will not work
    
        if isinstance(func,str):
            #So func won't be overwritten
            func_str=func
            def func():
                Shell(func_str,arbitrary=True)
        def decorator_Exit(exit_func):
            def new_Exit(*args, **kwargs):
                #So exit() is the last function run
                func()
                exit_func(*args, **kwargs)
            return new_Exit
        self.Exit=decorator_Exit(self.Exit)
        signal.signal(signal.SIGTERM,self.Exit)
        
    def Loop(self,command,delay=60):
        if isinstance(command,str):
            def func():
                while True:
                    Run(command)
                    self.Wait(delay)
        else:
            def func():
                while True:  
                    command()
                    self.Wait(delay)
        threading.Thread(target=func).start()

    def Wait(self,*args, **kwargs):
        utils.wait(*args, **kwargs)
    
    def Exit(self,signum,frame):
        exit()
        
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
            #Open a lock file so I can find it with lsof later
            signal.signal(signal.SIGTERM,self.Exit)
            lock_file=open(f"{TEMPDIR}/service_{self.name}.lock","w+")
            
            #Run *service.py
            with open(f"{ROOT}/{self.name}/{service_file}") as f:
                code=f.read()
            exec(code,globals(),locals())
            
            #Don't exit script yet.
            self.Wait()
            exit()
       
    def Stop(self):
        output=[self.Class.stop()]
        self.Class.cleanup_after_stop()
        return output
        
    def Restart(self):
        return self.Class.restart()
    
    
    def List(self):
        return self.Class.list()

    def Init(self):
        os.makedirs(f"{ROOT}/{self.self.name}",exist_ok=True)
        os.chdir(f"{ROOT}/{self.self.name}")
        os.makedirs("data",exist_ok=True)
        with open(f".{self.name}.py",'a'):
            pass
        
        if '--no-edit' not in self.flags:
            self.self.Edit()

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
        self.Class.stop()
    
    def Watch(self):
        self.Class.watch()


NAMES=list_services(NAMES)
for name in NAMES: 
    try:
        service=Service(name,FLAGS)
    except ServiceDoesNotExist:
        print(f"Service {name} does not exist")
        continue
    
    utils.export_methods_globally(CLASS_NAME.lower())
    
    result=utils.execute_class_method(eval(f"{CLASS_NAME.lower()}"),FUNCTION)
    print_result(result)
        

    
