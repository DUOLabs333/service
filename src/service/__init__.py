#!/usr/bin/env python
import subprocess
import os

import utils

class Service(utils.Class):
    def __init__(self,name,flags=None,**kwargs):
        
        self.env=kwargs.get("env",[f"SERVICE_NAME={name}"])
        
        self.temp_services=[]
        
        super().__init__(name,flags,kwargs)
        
        try:
            self.workdir
        except:
            self.workdir=self.directory
        
        self.Workdir("data")
    
    def _get_config(self):
        if "Enabled" in self.Status():
            service_file="service.py"
        else:
            service_file=".service.py"
        
        return [open(os.path.join(self.directory,service_file)).read()]
        
    def get_auxiliary_processes(self):
        processes=utils.shell_command(["ps","auxwwe"]).splitlines()
        processes=[_.split()[1] for _ in processes if f"SERVICE_NAME={self.name}" in _]
        return list(map(int,processes))
        
    #Functions to be used in *service.py
    def Run(self,command="",**kwargs):
        command_string=f"{utils.env_list_to_string(self.env) if kwargs.get('track',True) else 'true'}; cd {self.workdir}; {command}"
        super().Run(command_string,display_command=command,shell=True,**kwargs)
        
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
        
        with open(self.logfile,"a+") as f:
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

    def command_Init(self):
        os.makedirs(self.directory,exist_ok=True)
        os.chdir(self.directory)
        os.makedirs("data",exist_ok=True)
        with open(f".service.py",'a'):
            pass
        
        if 'no-edit' not in self.flags:
            self.Edit()

    def command_Edit(self):
        if "Enabled" in self.Status():
            utils.shell_command([os.getenv("EDITOR","vi"),os.path.join(self.directory,"service.py")],stdout=None)
        else:
            utils.shell_command([os.getenv("EDITOR","vi"),os.path.join(self.directory,".service.py")],stdout=None)
            
    def command_Status(self):
        return super().command_Status() + ["Enabled" if os.path.exists(os.path.join(self.directory,"service.py")) else "Disabled"]
    
    def command_Enable(self):
        if "Enabled" in self.Status():
            return [f"Service {self.name} is already enabled"]
        else:
            os.rename(os.path.join(self.directory,".service.py"),os.path.join(self.directory,"service.py"))
        
        if 'now' in self.flags:
            return [self.Start()]

            
    def command_Disable(self):
        if "Disabled" in self.Status():
            return [f"Service {self.name} is already disabled"]
        else:
            os.rename(os.path.join(self.directory,"service.py"),os.path.join(self.directory,".service.py"))
        
        if 'now' in self.flags:
            return [self.Stop()]

def main():
    utils.parse_and_call_and_return(Service)
        

    
