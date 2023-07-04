#!/usr/bin/python3
from myutils import GitHelper


class GitCreatePR(GitHelper):

    def run(self):
        info = self.remote.push(self.repo.active_branch)[0]
        self.logger.info(info.summary)
        msg = self.repo.head.commit.message
        msg_arr = msg.partition('\n')
        if len(msg_arr) >1:
            body = ''.join(msg_arr[1:])
            self.shell_exec(f"gh pr create --title '{msg_arr[0]}' --body '{body}'", log=True)
        else:
            self.shell_exec(f"gh pr create --title '{msg}' --body '{msg}'", log=True)


def main():
    GitCreatePR().run()


if __name__ == "__main__":
    main()
