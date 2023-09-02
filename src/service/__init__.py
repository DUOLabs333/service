#!/usr/bin/env python
import subprocess
import os
import signal

# < include '../utils/utils.py' >
import utils

import importlib.machinery, shutil

utils.GLOBALS=globals()


def flatten(*args, **kwargs):
    return utils.flatten_list(*args, **kwargs)

def print_result(*args, **kwargs):
    return utils.print_list(*args, **kwargs)

def split_by_char(*args, **kwargs):
    return utils.split_by_char(*args, **kwargs)
    
class Service:
    def __init__(self,name,flags,**kwargs):
        
        self.env=kwargs.get("env",[f"SERVICE_NAME={self.name}"])
        
        self.temp_services=[]
        
        super().__init__(self,name,flags,kwargs)

    #Functions to be used in *service.py
    def Run(self,command="",**kwargs):
        command=f"{utils.env_list_to_string(self.env) if track else 'true'}; cd {self.workdir}; {command}"
        super().Run(command,shell=True,**kwargs)
    
    def get_auxiliary_processes(self):
        processes=utils.shell_command(["ps","auxwwe"]).splitlines()
        processes=[_.split()[1] for _ in processes if f"SERVICE_NAME={self.name}" in _]
        return list(map(int,processes))
    
    
    def Container(self,_container=None):
        #Convinence --- if conainer name is not specified, it will assume that the container is the same name as the service
        if not _container:
            _container=self.name
        
        #_container=container.Container(_container)
        #self.Down(lambda : _container.Stop())
        self.Down(lambda : os.system(f"container stop {_container}"))
        
        #_container.Start()
        self.Run(f"container start {_container}",track=False)
        
        self.Run(f"echo Started container {_container}",track=False)
        
        with open(self.log,"a+") as f:
            utils.shell_command(["container", "watch", _container],stdout=f,block=False,env=os.environ.copy() | {"SERVICE_NAME":self.name})
        
        container_main_pid=utils.shell_command(["container","ps","--main",_container],stdout=subprocess.PIPE)
        
        #Wait until container ends
        try:
            container_main_pid=int(container_main_pid)
            utils.wait_until_pid_exits(container_main_pid)
        except ValueError:
            pass
    
    def Down(self,func):
        if isinstance(func,str):
            #So func won't be overwritten
            func_str=func
            def func():
                self.Run(func_str)
        self.exit_commands.append(func)
        
    def Dependency(self,service):
        if "Stopped" in self.__class__(service).Status():
            #self.temp_services.append(service)
            #Kill service when stopping
            self.Down(self.__class__(service).Stop)
            #utils.shell_command(["service","start",service],stdout=subprocess.DEVNULL)
            self.__class__(service).Start()
    #Commands      
    def Start(self):
        
        if "Started" in self.Status():
            return f"Service {self.name} is already started"
        
        if os.fork()==0:
            if os.fork()==0: #Double fork
                #If child, run code, then exit 
                signal.signal(signal.SIGTERM,self.Exit)
                
                if os.path.exists("data"):
                    self.Workdir("data")
                
                if "Enabled" in self.Status():
                    service_file="service.py"
                else:
                    service_file=".service.py"
                #Open a lock file so I can find it with lsof later
                lock_file=open(self.lock,"w+")
                
                #Run *service.py
                utils.execute(self,open(f"{ROOT}/{self.name}/{service_file}"))
                
                #Don't exit script yet.
                self.Wait()
                exit()
            exit()
    
    
    def Workdir(self,work_dir):
        self.Class.workdir(work_dir)

    def Init(self):
        os.makedirs(f"{ROOT}/{self.name}",exist_ok=True)
        os.chdir(f"{ROOT}/{self.name}")
        os.makedirs("data",exist_ok=True)
        with open(f".service.py",'a'):
            pass
        
        if 'no-edit' not in self.flags:
            self.Edit()

    def Edit(self):
        if "Enabled" in self.Status():
            utils.shell_command([os.getenv("EDITOR","vi"),f"{ROOT}/{self.name}/service.py"],stdout=None)
        else:
            utils.shell_command([os.getenv("EDITOR","vi"),f"{ROOT}/{self.name}/.service.py"],stdout=None)
            
    def Status(self):
        return self.Class.status() + ["Enabled" if os.path.exists(f"{ROOT}/{self.name}/service.py") else "Disabled"]
    
    def Enable(self):
        if "Enabled" in self.Status():
            return [f"Service {self.name} is already enabled"]
        else:
            os.rename(f"{ROOT}/{self.name}/.service.py",f"{ROOT}/{self.name}/service.py")
        
        if 'now' in self.flags:
            return [self.Start()]

            
    def Disable(self):
        if "Disabled" in self.Status():
            return [f"Service {self.name} is already disabled"]
        else:
            os.rename(f"{ROOT}/{self.name}/service.py",f"{ROOT}/{self.name}/.service.py")
        
        if 'now' in self.flags:
            return [self.Stop()]

utils.CLASS=Service
utils.ROOT=ROOT=utils.get_root_directory()
def main():
    
    NAMES,FLAGS,FUNCTION=utils.extract_arguments()
    
    for name in utils.list_items_in_root(NAMES, FLAGS): 
        item=utils.CLASS(name,FLAGS)
        result=utils.execute_class_method(item,FUNCTION)
        print_result(result)
        

    
