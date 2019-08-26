#!/usr/bin/env python3

from collections import OrderedDict#,ChainMap
from .SLHA_line import GetBlockName,GetDecayCode
from ...operators.iterable import FlatToList
from ...operators.object import lazyprogerty
from .SLHA_block import SLHA_block,ReadBlock
from .SLHA_decay import SLHA_decay


class SplitText(lazyprogerty):
    def __get__(self,instance,cls):
        if instance is None:
            return self
        else:
            # instance.SplitText()
            instance.block_text=OrderedDict()
            instance.decay_text=OrderedDict()
            target=instance.block_text.setdefault('head',[])
            for line in instance.text:
                start=line[:5].upper()
                if 'BLOCK' == start:
                    target=instance.block_text.setdefault(GetBlockName(line),[])
                elif 'DECAY' == start:
                    target=instance.decay_text.setdefault(GetDecayCode(line),[])
                target.append(line)
            return getattr(instance,self.func.__name__)

class SLHA_text:
    '''extracted messages from SLHA file'''
    def __init__(self,text,block_format=ReadBlock):
        self.text=text
        self.block_format=block_format
    @SplitText
    def block_text(self): pass
    @SplitText
    def decay_text(self): pass
    @lazyprogerty
    def DECAY(self):
        return SLHA_decay(self.decay_text)
    @lazyprogerty
    def BLOCK(self):
        return SLHA_block(self.block_text,block_format=self.block_format)
    def __call__(self,name,*code):
        name=name.upper()
        if name in self.block_text.keys():
            data_dict=getattr(self.BLOCK,name)
            try:
                return data_dict[code[0]]
            except KeyError:
                print(f'data with code:{code} not found in text:\n{data_dict}')
                raise
        elif name=='DECAY':
            data_dict=self.DECAY[code[0]]
            try:
                return data_dict[code[1]]
            except KeyError:
                print(f'data with code:{code} not found in text:\n{data_dict}')
                raise
        elif name=='WIDTH':
            return self.DECAY[code[0]]['WIDTH']


class SLHA_document(SLHA_text):
    def __init__(self,SLHA_document,block_format=ReadBlock):
        self.path=SLHA_document
        self.block_format=ReadBlock
    @lazyprogerty
    def text(self):
        # print(f'Getting text from {self.path}')
        with open(self.path,'r') as SLHA:
            return SLHA.readlines()
