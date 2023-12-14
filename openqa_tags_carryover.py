#!/usr/bin/python3

from myutils import openQAHelper
import urllib3
import requests
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TagCarryOver(openQAHelper):

    def __init__(self):
        super(TagCarryOver, self).__init__('tagscarryover', load_cache=False)

    def get_latest_comment(self, groupid, parent_group: bool):
        if parent_group:
            groupurl = 'parent_groups'
        else:
            groupurl = 'groups'
        comments = self.osd_get(f'api/v1/{groupurl}/{groupid}/comments')
        if 'error' in comments:
            raise RuntimeError(comments)
        latest_comment = None
        tag_comment = re.compile(r'''tag\:((\d+)(-SP\d-[\d\.]+)?)\:important\:([\d\w]+)''')
        match_result = None
        for comment in comments:
            if not comment['bugrefs']:
                m = tag_comment.search(comment['text'])
                if m:
                    if latest_comment:
                        if latest_comment['id'] < comment['id']:
                            latest_comment = comment
                            match_result = m
                    else:
                        latest_comment = comment
                        match_result = m
        return {'build': match_result.group(1), 'text': match_result.group(4)}

    def copy_tag(self, dest_groupid, source_comment):
        target_comment = self.get_latest_comment(dest_groupid, False)
        if source_comment == target_comment['text']:
            self.logger.info('No need to copy for groupid={}. Tag "{}" already applied to {} build '.format(
                dest_groupid, target_comment['text'], target_comment['build']))
            return
        else:
            latest_build = self.get_latest_build(dest_groupid)
            comment_text = 'tag:{}:important:{}'.format(latest_build, source_comment)
            self.logger.info('Add a comment to group {} with reference {}'.format(dest_groupid, comment_text))
            cmd = 'openqa-cli api --host {} -X POST groups/{}/comments text=\'{}\''.format(
                self.OPENQA_URL_BASE, dest_groupid, comment_text)
            self.shell_exec(cmd, log=True)

    def run(self):
        source_comment = self.get_latest_comment('15', True)
        self.logger.info('Source group {}, with latest tag "{}"'.format('15', source_comment['text']))
        self.copy_tag('219', source_comment['text'])
        self.copy_tag('274', source_comment['text'])
        self.copy_tag('275', source_comment['text'])


def main():
    tagcarryover = TagCarryOver()
    tagcarryover.run()


if __name__ == "__main__":
    main()
