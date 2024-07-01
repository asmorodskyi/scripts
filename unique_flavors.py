#!/usr/bin/python3.11

from pathlib import Path
import yaml


def main():
    collected_flavors = set()
    for yaml_file in Path('/home/asmorodskyi/source/metadata/bot-ng/').glob('pub*.yml'):
        contents = yaml.safe_load(Path(yaml_file).read_text(encoding="utf-8"))
        if 'aggregate' in contents:
            collected_flavors.add(contents['aggregate']['FLAVOR'])
        if 'incidents' in contents:
            for field in contents['incidents']['FLAVOR']:
                collected_flavors.add(field)
    print(collected_flavors)


if __name__ == "__main__":
    main()