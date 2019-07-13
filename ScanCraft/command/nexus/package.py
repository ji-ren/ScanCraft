#!/usr/bin/env python3
import os,subprocess,shutil
try:
    from .nexus.GetPackageDir import GetPackageDir as GetDir
    from .color_print import ColorPrint,UseStyle,Error
except:
    raise


import os
from .GetPackageDir import GetPackageDir

class package(object):
    def __init__(self
                ,package_name=None           #程序包的名字
                ,package_dir=None            #程序包所在的目录
                ,run_dir=None                #可执行文件的目录
                ,main_routine=None           #运行命令
                ,data_dir=None               #保留数据的目录
                ,input_dir=None              #输入文件所在的目录
                ,input_file=None             #输入文件
                ,output_dir=None             #输出文件的目录
                ,output_file=None            #输出文件
                ,record_dir=None             #保留输出文件的目录
                ,**keyword):
        self.package_name=package_name
        if package_dir==None:
            package_dir=GetDir(f'{package_name}')
        self.run_dir=run_dir
        self.command=main_routine
        self.input_dir=input_dir
        self.input_file=input_file
        self.record_dir=record_dir
        self.output_file=output_file
        self.output_dir=output_dir



    def Run(self):
        if self.command:
            run_command=os.path.join(self.command,self.input_file)
            run=subprocess.Popen(run_command
                                    ,cwd=self.run_dir
                                    ,shell=True
                                    ,stdout=subprocess.PIPE
                                    ,stderr=subprocess.PIPE
                                    ,universal_newlines=True)
            run.wait()
            if (run.returncode):
                ColorPrint(0,33,'',run.communicate()[0])
                Error(run.communicate()[1])
        else:
            print('no command')
        pass


    def Record(self,number,record_directory=None):
        if record_directory==None:
            record_directory=self.record_dir
        shutil.move(self.output_dir,os.path.join(record_directory,self.output_file+'.'+str(int(number))))
        pass


    def build(self):
        pass

mh=[125.09, 3., 3.]
from command.format.parameter_type import *
# from command.MicrOMEGAs import MicrOMEGAs
from command.outputfile import *
#print([ i for i in globals().keys() if '__' not in i])
