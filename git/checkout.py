#!/usr/bin/python3
import sys

from myutils import GitHelper


class GitCheckout(GitHelper):

    def run(self, checkout_type, branch_name):
        if checkout_type == 'n':
            self.repo.git.checkout('HEAD', b=branch_name)
            self.repo.git.push('--set-upstream', self.remote, branch_name)
        elif checkout_type == 'b':
            self.remote.fetch()
            self.repo.create_head(branch_name, self.remote.refs[branch_name])
            self.repo.heads[branch_name].set_tracking_branch(
                self.remote.refs[branch_name])
            self.repo.heads[branch_name].checkout()
        elif checkout_type == 'm':
            self.repo.git.checkout(self.master)
            self.repo.git.pull()


def main():
    helper = GitCheckout()
    if len(sys.argv) != 3:
        helper.logger.error("Must pass branch name!")
        sys.exit(1)
    helper.run(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
