#!/usr/bin/python3
import sys

from myutils import GitHelper


class GitHardFetch(GitHelper):

    def run(self):
        self.remote.fetch()
        self.repo.git.rebase(self.master)


def main():
    GitHardFetch().run()


if __name__ == "__main__":
    main()
