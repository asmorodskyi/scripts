#!/usr/bin/python3
from myutils import GitHelper


class GitCreatePR(GitHelper):

    def run(self):
        info = self.remote.push(self.repo.active_branch)[0]
        self.logger.info(info.summary)
        msg = self.repo.head.commit.message

        self.shell_exec(
            f"gh pr create --title '{msg}' --body '{msg}'", log=True)


def main():
    GitCreatePR().run()


if __name__ == "__main__":
    main()
