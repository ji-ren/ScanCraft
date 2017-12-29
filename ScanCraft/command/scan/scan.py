#!/usr/bin/env python3
import numpy,copy,math
# from .data_type import scalar,matrix
from ..read.readline import ReadLine
from ..color_print import Error,Caution
from ..read.readSLHA import ReadSLHAFile
from .free_parameter import independent_scalar,follower
from ..format.parameter_type import scalar

class scan():
    def __init__(self,method='mcmc'):
        self.variable_list={}
        self.scalar_list={}
        self.matrix_list={}
        self.follower_list={}
        self.block_list={}
        self.method=method.lower()

        # if self.method=='mcmc':
        #     self.Add=self.AddMcmcScalar
        #     self.AddMatrix=self.AddMcmcMatrix
        #     self.GetNewPoint=self.GetNewPoint_mcmc

    def AddToList(self,par):
        if par.name in self.variable_list.keys():
            Caution("parameter '%s' overridden"%name)
        self.variable_list.update({par.name:par})

        if type(par) is independent_scalar:
            self.scalar_list.update({par.name:par})
        elif type(par) is follower:
            self.follower_list.update({par.name:par})

        if par.block not in self.block_list.keys():
            self.block_list.update({par.block:{}})
        block_i=self.block_list[par.block]
        block_i.update({par.code:par})

    def AddScalar(self,name,block,code
                ,minimum=None,maximum=None,value=None
                ,prior_distribution=None
                ,**args
                ):
        if prior_distribution==None:
            prior_distribution={#defult prior
            'random':'uniform','mcmc':'normal'
            }[self.method]

        scl=independent_scalar(
            name,block,code,minimum,maximum
            ,strategy=self.method
            ,prior_distribution=prior_distribution
            ,**args)
        self.AddToList(scl)

    def AddFollower(self,name,block,code,target):
        if type(target) is str:
            try:
                target=self.variable_list[target]
            except KeyError:
                Error('variable %s do not exist'%target)
        while isinstance(target,(follower)):
            target=target.target
        flw=follower(name,block,code,target)
        self.AddToList(flw)
    
    def AddMatrix(self,name,block):
        pass

    def Sample(self):
        for p in self.scalar_list.values():
            p.Generate()
        for p in self.follower_list.values():
            p.Generate()
    #========================
    
    def AddMcmcMatrix(self,name,block,shape,free_element={},minimum=None,maximum=None,pace='normal',step_width=None,element_list={}):
        block=block.upper()
        # set one matrix
        mtx=matrix(name,block,shape,element_list={})
        
        if type(free_element) is dict:
            mtx.element_list.update(free_element)
        elif type(free_element) is list or type(free_element) is tuple:
            if all( type(coords) is tuple for coords in free_element ):
                mtx.element_list.update(dict.fromkeys(free_element))

        mtx.minimum=minimum
        mtx.maximum=maximum
        mtx.pace=pace
        if step_width:
            mtx.step_width=step_width
        else:
            try:
                mtx.step_width=(mtx.maximum-mtx.minimum)/100.
            except TypeError:
                Caution(
                    "  Both maximum and minimum of '%s' should be given with pace='%s'"%(name,pace[0])
                +   " if step width is not specified. Later, step width will be 1% of its initial value")

        # add matrix into lists
        if name in self.variable_list.keys():
            Caution("parameter '%s' overridden"%name)
        self.variable_list[name]=mtx
        self.matrix_list[name]=mtx

        if block in self.block_list.keys():
            Caution("matrix '%s' overridden"%name)
        self.block_list[block]=mtx

    def GetNewPoint_mcmc(self,step_factor=1.):
        new_point=copy.deepcopy(self)
        for name in self.scalar_list.keys():
            old=self.scalar_list[name]
            v=getattr(Random,old.pace)(old.value , old.minimum , old.maximum ,step_factor)
            new_point.scalar_list[name].value=v
        for name in self.follower_list.keys():
            par=new_point.follower_list[name]
            par.value=new_point.variable_list[par.follow].value
        for name in self.matrix_list.keys():
            old=self.matrix_list[name]
            for coords in old.element_list.keys():
                v=getattr(Random,old.pace)(old.element_list[coords] , old.minimum , old.maximum ,step_factor)
                new_point.matrix_list[name].element_list[coords]=v
        return new_point
    
    def Print(self):
        for name in self.scalar_list.keys():
            print('\t',name,self.scalar_list[name].value)
        for name in self.follower_list.keys():
            print('\t',name,self.follower_list[name].value)
        for name in self.matrix_list.keys():
            print('\t',name,self.matrix_list[name].element_list)
            

    def GetValue(self,file_name):
        target=ReadSLHAFile(file_name)
        #print(target.LAMN);exit()
        for name in self.scalar_list.keys():
            par=self.scalar_list[name]
            par.value=getattr(target,par.block)[par.code]
        for name in self.follower_list.keys():
            par=self.follower_list[name]
            par.value=par.target.value
        for name in self.matrix_list.keys():
            par=self.matrix_list[name]
            for coords in par.element_list.keys():
                par.element_list[coords]=getattr(target,par.block[:])[coords]
