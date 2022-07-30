import yaml
import json


def loadcfg_from_file(path: str, filetype: str = 'yml', encoding='utf-8'):
    cfg = None
    try:
        with open(path, encoding=encoding) as filecfg:
            if filetype.lower() in ['yml', 'yaml']:
                cfg = yaml.safe_load(filecfg)
            elif filetype.lower() in ['json']:
                cfg = json.load(filecfg)
        return cfg
    except Exception as e:
        print(e)


def w_cfg_to_file(content, path: str, filetype: str = 'yml', encoding='utf-8'):
    try:
        with open(path, encoding=encoding) as filecfg:
            if filetype.lower() in ['yml', 'yaml']:
                yaml.dump(content, filecfg, allow_unicode=True)
            elif filetype.lower() in ['json']:
                json.dump(content, filecfg, allow_unicode=True)
        return True
    except Exception as e:
        print(e)
        return False
