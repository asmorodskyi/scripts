#!/usr/bin/python3
from git import Repo
from myutils import TaskSolver


class SmartPull(TaskSolver):

    def solve(self, params_dict):
        try:
            self.logger.info("#### START processing repo %s",
                             params_dict['repo_path'])
            repo = Repo(params_dict['repo_path'])
            self.logger.info("Current branch is %s with commit %s",
                             repo.active_branch, repo.commit())
            was_dirty = False
            if repo.is_dirty():
                self.logger.info("HEAD is dirty, trying to stash changes")
                repo.git.stash('save')
                was_dirty = True
            old_branch = 'master'
            if str(repo.active_branch) != "master":
                self.logger.info(
                    "HEAD pointing to %s,trying switch to master", repo.active_branch)
                old_branch = repo.active_branch
                repo.git.checkout('master')
            repo.remote().pull('master')
            self.logger.info(
                "After pulling changes head pointing to %s", repo.commit())
            if old_branch != "master":
                self.logger.info(
                    "HEAD was at %s, switching it back", old_branch)
                repo.git.checkout(old_branch)
            if was_dirty:
                self.logger.info("master was dirty, so reapplying changes")
                repo.git.stash('apply')
        except Exception:
            self.handle_error()
        finally:
            self.logger.info("#### End processing repo %s",
                             params_dict['repo_path'])


def main():
    file = open('/smart_pull_repos', 'r')
    lines = file.readlines()
    solver = SmartPull('smartpull')
    for line in lines:
        solver.solve({'repo_path': line.strip()})


if __name__ == "__main__":
    main()
