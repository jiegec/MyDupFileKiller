from mydupfilekiller import *
from hashlib import md5
def Testfunc1():
    find(())
    
def Testfunc2():
    find({})
    
def Testfunc3():
    find([])
    
def Testfunc4():
    find('')

def Testfunc5():
    find('...')

def Testfunc6():
    result = find('.')
    m = md5()
    empty = m.hexdigest()
    assert empty  not in result[1]
    m.update(b'abc')
    # hash for 'abc'
    assert len(result[1][m.hexdigest()]) == 3 
    result = find('.', skip_empty_files=False)
    assert empty  in result[1]
