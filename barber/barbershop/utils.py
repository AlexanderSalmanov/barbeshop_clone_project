import random
import string

def suffix_generator(seq):
    """
    Simple utility function for generating unique slugs
    """
    suffix = ''.join([random.choice(string.ascii_lowercase + string.digits) for _ in range(6)])
    return seq + suffix
