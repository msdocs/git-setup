from pybitbucket.auth import BasicAuthenticator
from argparse import RawTextHelpFormatter, ArgumentParser
from pybitbucket.bitbucket import Client
from pybitbucket.repository import Repository
from functools import wraps
from contextlib import contextmanager
from pathlib import Path
import concurrent.futures
import git

# TODO List
# TODO: Make a util library
# TODO: Create an Abstract Class and Methods to build clients / Query Repos / Clone
# TODO: Have a Bitbucket Subclasses
# TODO: Have a Github Subclasses




def build_arg_parser(description: str= '') -> ArgumentParser:
    parser = ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
    parser.add_argument('--user', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--email', required=True)
    parser.add_argument('--target', required=True)
    return parser


@contextmanager
def user_patch(client: Client, value: str = ''):
    original = client.get_username
    client.get_username = lambda: value
    yield
    client.get_username = original


def patch_user(fn):
    @wraps(fn)
    def wrapper(client, *args, **kwargs):
        with user_patch(client):
            return fn(client, *args, **kwargs)

    return wrapper


def clone_repo(path: Path, repo_url: str):
    return git.Git(path).clone(repo_url)



@patch_user
def clone_repos(client: Client,path: Path):
    repos = Repository.find_repositories_by_owner_and_role(client=client, role="member")

    path.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_repo = {executor.submit(clone_repo, path, repo.clone['https']): repo for repo in repos}

        for future in concurrent.futures.as_completed(future_to_repo):
            repo: str = future_to_repo[future]
            try:
                data = future.result()
                print(f'Cloned: {repo.name} ')
            except Exception as exc:
                if exc.status == 128:
                    print(f'{repo.name} already exists')
            else:
                print(data)


parser=build_arg_parser()
args = parser.parse_args()
bit_bucket = Client(BasicAuthenticator(password=args.password,
                                       username=args.user,
                                       client_email=args.email))

clone_repos(client=bit_bucket, path=Path(args.target))
