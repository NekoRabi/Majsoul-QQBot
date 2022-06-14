import yaml
import json

def loadcfg_from_file(path:str,filetype:str='yml',encoding='utf-8'):
    cfg = None
    with open(path,encoding=encoding) as filecfg:
        if filetype.lower() in ['yml','yaml']:
            cfg = yaml.safe_load(filecfg)
        elif filetype.lower() in ['json']:
            cfg = json.load(filecfg)
    return cfg