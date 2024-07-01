#!/usr/bin/python3.11
from git import Repo
from git.exc import GitCommandError
from myutils import TaskHelper


class SmartPull(TaskHelper):

    def run(self, repo_path):
        try:
            repo = Repo(repo_path)
            initial_commit = repo.commit()
            if 'master' in repo.remote().refs:
                master_branch = 'master'
            else:
                master_branch = 'main'
            if repo.is_dirty():
                self.logger.warning(f"{repo_path} HEAD is dirty, will only fetch")
                repo.remote().fetch()
            elif str(repo.active_branch) != master_branch:
                self.logger.warning(f"{repo_path} HEAD pointing to {repo.active_branch}, will only fetch")
                repo.remote().fetch()
            else:
                self.logger.info(f"{repo_path} HEAD is clean, will pull")
                repo.remote().pull(master_branch)
                if initial_commit != repo.commit():
                    self.logger.warning("master branch updated")
        except GitCommandError as err:
            self.logger.error(err)
        except Exception:
            self.handle_error()


def main():
    file = open('/smart_pull_repos', 'r')
    lines = file.readlines()
    solver = SmartPull('smartpull')
    for line in lines:
        solver.run(line.strip())


if __name__ == "__main__":
    main()
