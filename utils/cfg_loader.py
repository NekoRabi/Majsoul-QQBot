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
    except Exception as e:
        print(e)
    return cfg


def w_cfg_to_file(content, path: str, filetype: str = 'yml', encoding='utf-8', allow_unicode=True):
    try:
        with open(path, 'w', encoding=encoding) as filecfg:
            if filetype.lower() in ['yml', 'yaml']:
                yaml.dump(content, filecfg, allow_unicode=allow_unicode)
            elif filetype.lower() in ['json']:
                json.dump(content, filecfg, allow_unicode=allow_unicode)
        return True
    except Exception as e:
        print(e)
        return False
