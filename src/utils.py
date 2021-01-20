import os, sys
import numpy as np

class Schema:
    point_label_col = 'PointLabel'
    ahu_col = 'UpstreamAHU'
    zone_col = 'ZoneName'
    vav_col = 'VAVName'
    brick_class_col = 'BrickClass'
    temp_col = '_'
    col_list = [point_label_col, ahu_col, zone_col, vav_col, brick_class_col]
    ahu_prefix = 'AHU_'
    vav_prefix = 'VAV_'

def random_idx(n):
    return np.random.randint(0, n)

metadata = {
    "name": "Brick Reconciliation Service",
    "defaultTypes": [
        {"id": "EquipmentClass", "name": "EquipmentClass"},
        {"id": "PointClass", "name": "PointClass"}
    ]
}

inf = brickschema.inference.TagInferenceSession(approximate=True)


def flatten(lol):
    """flatten a list of lists"""
    return [x for sl in lol for x in sl]


def resolve(q):
    """
    q has fields:
    - query: string of the label that needs to be converted to a Brick type
    - type: optional list of 'types' (e.g. "PointClass" above)
    - limit: optional limit on # of returned candidates (default to 10)
    - properties: optional map of property idents to values
    - type_strict: [any, all, should] for strictness on the types returned
    """
    limit = int(q.get('limit', 10))
    # break query up into potential tags
    tags = map(str.lower, re.split(r'[.:\-_ ]', q.get('query', '')))
    tags = list(tags)
    brick_tags = flatten([tagmap.get(tag.lower(), [tag]) for tag in tags])

    if q.get('type') == 'PointClass':
        brick_tags += ['Point']
    elif q.get('type') == 'EquipmentClass':
        brick_tags += ['Equipment']

    res = []
    most_likely, leftover = inf.most_likely_tagsets(brick_tags, limit)
    for ml in most_likely:
        res.append({
            'id': q['query'],
            'name': ml,
            'score': (len(brick_tags) - len(leftover)) / len(brick_tags),
            'match': len(leftover) == 0,
            'type': [{"id": "PointClass", "name": "PointClass"}],
        })
    print('returning', res)
    return res

def recon_api_inference():
    """
    TODO!!
    """
    pass

def clean_extra_contents():
    os.system('rm -rf src/building_depot data plot logs ./config/sensor_uuids.json')


