#!/usr/bin/python3
import sys

sys.path.append('/scripts/')
from myutils import GitHelper


class GitCreatePR(GitHelper):

    def run(self):
        try:
            info = self.remote.push(self.repo.active_branch)[0]
            self.logger.info(info.summary)
            self.shell_exec(
                "hub pull-request -m '{}'".format(self.repo.head.commit.message), log=True)
        except Exception as e:
            self.handle_error()


def main():
    GitCreatePR().run()


if __name__ == "__main__":
    main()
