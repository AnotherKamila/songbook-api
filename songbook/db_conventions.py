from .ref import Ref, refjoin

PUBLIC_BOOKS_LIST = 'book/public_books'
PUBLIC_SONGS_LIST = 'book/public_songs'

def contents_ref(ref):
    return refjoin(ref, 'contents')
