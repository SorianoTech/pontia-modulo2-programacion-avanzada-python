from slowapi import Limiter
from slowapi.util import get_remote_address

# Definimos una única instancia del limiter para toda la app
limiter = Limiter(key_func=get_remote_address)
