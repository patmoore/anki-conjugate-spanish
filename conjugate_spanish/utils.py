def cs_debug(*args):
    # print("conjugate_spanish::", end="")
    # print(*args)
    pass

def cs_error(*args):
    print("ERROR: conjugate_spanish::", end="")
    print(*args)
    raise Exception()

__all__= [
    'cs_debug'
    ]