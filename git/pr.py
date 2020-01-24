#!/usr/bin/python3
import sys
from git import Repo
import os

sys.path.append('/scripts/')
from myutils import TaskHelper


#target="${target:- asmorodskyi}"
# git push $target && git show --no-patch --format=%B | hub pull-request -F -


class GitCreatePR(TaskHelper):

    def run(self, params_dict):
        try:
            repo = Repo(os.getcwd())
            remote = None
            try:
                if repo.remotes.asmorodskyi.exists():
                    remote = repo.remotes.asmorodskyi
            except Exception:
                remote = repo.remotes.origin
            info = remote.push(repo.active_branch)[0]
            self.logger.info(info.summary)
            self.shell_exec(
                "hub pull-request -m {}".format(repo.head.commit.message))
        except Exception as e:
            self.handle_error()


def main():
    solver = GitCreatePR('gitcreatepr', log_to_file=False)
    solver.run({})


if __name__ == "__main__":
    main()
