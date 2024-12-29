import random 
import os 

def random_num(low:int, high:int)->int:
    '''
    Generate a random number between low and high
    '''
    return random.randint(low, high)

def is_folder(path:str)->bool:
    '''
    Check if the path is a folder
    '''
    return os.path.isdir(path)

def is_file(path:str)->bool:
    '''
    Check if the path is a file
    '''
    return os.path.isfile(path)

def rand_port()->int:
    '''
    Generate a random port number
    '''
    return random_num(30000, 65535)

def rand_string(length:int)->str:
    '''
    Generate a random string of a given length from a-zA-Z0-9
    '''
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=length))

def rand_tmp_file()->str:
    '''
    Generate a random temporary file name
    '''
    return f'/tmp/{rand_string(10)}'