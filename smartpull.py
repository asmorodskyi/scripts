#!/usr/bin/python3.11
from git import Repo
from git.exc import GitCommandError
import logging

logger = logging.getLogger('SmartPull')
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

def main():
    file = open('/smart_pull_repos', 'r')
    lines = file.readlines()
    for line in lines:
        repo_path=line.strip()
        try:
            repo = Repo(repo_path)
            initial_commit = repo.commit()
            if 'master' in repo.remote().refs:
                master_branch = 'master'
            else:
                master_branch = 'main'
            if repo.is_dirty():
                logger.warning(f"{repo_path} HEAD is dirty, will only fetch")
                repo.remote().fetch()
            elif str(repo.active_branch) != master_branch:
                logger.warning(f"{repo_path} HEAD pointing to {repo.active_branch}, will only fetch")
                repo.remote().fetch()
            else:
                logger.info(f"{repo_path} HEAD is clean, will pull")
                repo.remote().pull(master_branch)
                if initial_commit != repo.commit():
                    logger.warning("master branch updated")
        except GitCommandError as err:
            logger.error(err)

if __name__ == "__main__":
    main()
