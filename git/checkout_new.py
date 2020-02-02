#!/usr/bin/python3
import sys

sys.path.append('/scripts/')
from myutils import GitHelper

# git checkout -b $1
# git push -u asmorodskyi $1


class GitCheckoutNew(GitHelper):

    def run(self, branch_name):
        try:
            self.repo.git.checkout('HEAD', b=branch_name)
        except Exception as e:
            self.handle_error()


def main():
    helper = GitCheckoutNew()
    if len(sys.argv) != 2:
        helper.logger.error("Must pass branch name!")
        sys.exit(1)
    helper.run(sys.argv[1])


if __name__ == "__main__":
    main()
