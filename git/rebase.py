#!/usr/bin/python3
import sys

from myutils import GitHelper

class GitRebase(GitHelper):

    def run(self):
        self.remote.fetch()
        self.repo.git.rebase("master")



def main():
    GitRebase().run()


if __name__ == "__main__":
    main()