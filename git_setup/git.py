import git
from pybitbucket.bitbucket import Client
from pybitbucket.repository import Repository
from functools import wraps
from contextlib import contextmanager


class Git_Setup:
    pass


class Bitbucket(Git_Setup):

    @contextmanager
    def user_patch(self, client: Client, value: str = ''):
        original = client.get_username
        client.get_username = lambda: value
        yield
        client.get_username = original

    def patch_user(self, fn):
        @wraps(fn)
        def wrapper(client, *args, **kwargs):
            with user_patch(client):
                return fn(client, *args, **kwargs)

        return wrapper

    bit_bucket = Client(BasicAuthenticator(password=args.password,
                                           username=args.user,
                                           client_email=args.email))
    pass
