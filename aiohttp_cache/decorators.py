class cache(object):
    def __init__(self, expires: int = 3600, unless: bool = False):
        self.expires = expires
        self.unless = unless
    
    def __call__(self, f):
        f.cache_enable = True
        f.cache_expires = self.expires
        f.cache_unless = self.unless
        
        return f
    
    
__all__ = ("cache", )
