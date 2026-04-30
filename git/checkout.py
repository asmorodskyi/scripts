#!/usr/bin/python3
import sys

from myutils import GitHelper


class GitCheckout(GitHelper):
    def run(self, checkout_type, branch_name):
        # gcon alias
        if checkout_type == "n":
            self.repo.git.checkout("HEAD", b=branch_name)
            self.repo.git.push("--set-upstream", self.user_remote, branch_name)
        # gcob alias. checkout remote branch which not exists locally
        elif checkout_type == "b":
            self.user_remote.fetch()
            self.repo.create_head(branch_name, self.user_remote.refs[branch_name])
            self.repo.heads[branch_name].set_tracking_branch(
                self.user_remote.refs[branch_name]
            )
            self.repo.heads[branch_name].checkout()
        # gcom alias. fetch remote master and check it out
        elif checkout_type == "m":
            self.orig_remote.fetch()
            self.repo.git.checkout(self.master)


def main():
    helper = GitCheckout()
    if len(sys.argv) != 3:
        helper.logger.error("Must pass branch name!")
        sys.exit(1)
    helper.run(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
