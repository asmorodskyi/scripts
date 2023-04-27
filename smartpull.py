#!/usr/bin/python3
from git import Repo
from myutils import TaskHelper


class SmartPull(TaskHelper):

    def run(self, repo_path):
        try:
            self.logger.info("#### START processing repo %s", repo_path)
            repo = Repo(repo_path)
            self.logger.info("Current branch is %s with commit %s",
                             repo.active_branch, repo.commit())
            was_dirty = False
            if repo.is_dirty():
                self.logger.info("HEAD is dirty, trying to stash changes")
                repo.git.stash('save')
                was_dirty = True
            if 'master' in repo.remote().refs:
                master_branch = 'master'
            else:
                master_branch = 'main'
            old_branch = master_branch
            if str(repo.active_branch) != master_branch:
                self.logger.info(
                    "HEAD pointing to %s,trying switch to %s", repo.active_branch, master_branch)
                old_branch = repo.active_branch
                repo.git.checkout(master_branch)
            repo.remote().pull(master_branch)
            self.logger.info(
                "After pulling changes head pointing to %s", repo.commit())
            if old_branch != master_branch:
                self.logger.info(
                    "HEAD was at %s, switching it back", old_branch)
                repo.git.checkout(old_branch)
            if was_dirty:
                self.logger.info("%s was dirty, so reapplying changes", master_branch)
                repo.git.stash('apply')
        except Exception:
            self.handle_error()
        finally:
            self.logger.info("#### End processing repo %s", repo_path)


def main():
    file = open('/smart_pull_repos', 'r')
    lines = file.readlines()
    solver = SmartPull('smartpull')
    for line in lines:
        solver.run(line.strip())


if __name__ == "__main__":
    main()
