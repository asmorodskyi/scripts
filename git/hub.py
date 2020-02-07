#!/usr/bin/python3
import sys

from myutils import GitHelper


class GitCreatePR(GitHelper):

    def run(self):
        info = self.remote.push(self.repo.active_branch)[0]
        self.logger.info(info.summary)
        self.shell_exec(
            "hub pull-request -m '{}'".format(self.repo.head.commit.message), log=True)


def main():
    GitCreatePR().run()


if __name__ == "__main__":
    main()
