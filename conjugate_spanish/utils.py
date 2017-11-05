def cs_debug(*args):
    print("conjugate_spanish::", end="")
    print(*args)
    pass

def cs_error(*args):
    print("ERROR: conjugate_spanish::", end="")
    print(*args)
#     raise Exception(msg_).with_traceback(traceback_)

__all__= [
    'cs_debug'
    ]