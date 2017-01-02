from .ref import Ref, refjoin

PUBLIC_LIST = 'book/public_list'

def contents_ref(ref):
    return refjoin(ref, 'contents')
