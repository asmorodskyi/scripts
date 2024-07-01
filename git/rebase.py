#!/usr/bin/python3.11
from myutils import GitHelper


class GitRebase(GitHelper):

    def run(self):
        self.remote.fetch()
        self.repo.git.rebase(self.master)


def main():
    GitRebase().run()


if __name__ == "__main__":
    main()
