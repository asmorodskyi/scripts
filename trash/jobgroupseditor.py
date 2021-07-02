#!/usr/bin/python3
from myutils import TaskHelper
from ruamel.yaml import YAML

class JobGroupYAML(TaskHelper):

    files_to_change = [
        "/home/asmorodskyi/source/qac-openqa-yaml/publiccloud/updates/12sp4.yaml",
        "/home/asmorodskyi/source/qac-openqa-yaml/publiccloud/updates/12sp5.yaml",
        "/home/asmorodskyi/source/qac-openqa-yaml/publiccloud/updates/15sp1.yaml",
        "/home/asmorodskyi/source/qac-openqa-yaml/publiccloud/updates/15sp2.yaml",
        "/home/asmorodskyi/source/qac-openqa-yaml/publiccloud/updates/15sp3.yaml"
    ]

    # valuesYaml['defaults']['x86_64']['settings']

    def modify(self, filepath):
        with open(filepath, 'r') as f:
            yaml = YAML(typ='safe')
            valuesYaml = yaml.load(f)
            for flavor_testsuite in valuesYaml['scenarios']['x86_64']:
                for test in valuesYaml['scenarios']['x86_64'][flavor_testsuite]:
                    if 'qem_publiccloud_img_proof' in test:
                        test['publiccloud_img_proof'] = test.pop('qem_publiccloud_img_proof')
        with open(filepath, "w") as f:
            yaml.dump(valuesYaml, f)

    def run(self):
        for fl in JobGroupYAML.files_to_change:
            self.modify(fl)


def main():
    editor = JobGroupYAML('jobgroupeditor')
    editor.run()


if __name__ == "__main__":
    main()
