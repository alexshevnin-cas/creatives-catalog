"""Export DB + thumbnails to a static site for GitHub Pages."""
import json, os, shutil, sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, 'creatives.db')
OUT = os.path.join(BASE, '_site')
THUMBS_SRC = os.path.join(BASE, 'thumbnails')

def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    games = [dict(r) for r in conn.execute('SELECT * FROM games ORDER BY short_name').fetchall()]

    rows = conn.execute(
        'SELECT c.id AS c_id, c.game_id, c.type, c.seq_number, c.seasonal_tag, '
        'c.concept_name, c.status, c.networks, '
        'g.code_1c, g.name AS game_name, g.short_name, '
        'r.id AS r_id, r.width, r.height, r.duration_sec, '
        'r.file_path, r.thumbnail_path, r.generated_name AS r_name, r.file_size_mb '
        'FROM creatives c '
        'JOIN games g ON c.game_id = g.id '
        'LEFT JOIN renditions r ON r.creative_id = c.id '
        "ORDER BY CASE g.short_name WHEN 'CarCrash' THEN 0 ELSE 1 END, g.short_name, "
        "CASE c.type WHEN 'Video' THEN 0 WHEN 'Banner' THEN 1 WHEN 'Playable' THEN 2 ELSE 3 END, "
        'c.seq_number DESC, r.width DESC'
    ).fetchall()

    from collections import OrderedDict
    tree = OrderedDict()
    concepts_idx = {}
    for r in rows:
        gkey = r['game_name']
        if gkey not in tree:
            tree[gkey] = {
                'game_id': r['game_id'], 'code_1c': r['code_1c'],
                'short_name': r['short_name'], 'types': OrderedDict(),
            }
        tkey = r['type']
        if tkey not in tree[gkey]['types']:
            tree[gkey]['types'][tkey] = []
        c_id = r['c_id']
        if c_id not in concepts_idx:
            concept = {
                'id': c_id, 'seq_number': r['seq_number'],
                'seasonal_tag': r['seasonal_tag'], 'concept_name': r['concept_name'],
                'status': r['status'],
                'networks': [n for n in (r['networks'] or '').split(',') if n],
                'renditions': [],
            }
            tree[gkey]['types'][tkey].append(concept)
            concepts_idx[c_id] = concept
        if r['r_id']:
            concepts_idx[c_id]['renditions'].append({
                'width': r['width'], 'height': r['height'],
                'duration_sec': r['duration_sec'],
                'thumbnail_path': r['thumbnail_path'],
                'generated_name': r['r_name'],
                'file_size_mb': r['file_size_mb'],
            })

    # Convert OrderedDicts to lists for JSON
    tree_list = []
    for gname, gdata in tree.items():
        types_list = []
        for tname, concepts in gdata['types'].items():
            types_list.append({'type': tname, 'concepts': concepts})
        tree_list.append({
            'game_name': gname, 'game_id': gdata['game_id'],
            'code_1c': gdata['code_1c'], 'short_name': gdata['short_name'],
            'types': types_list,
        })

    data = {'games': games, 'tree': tree_list}
    with open(os.path.join(OUT, 'data.json'), 'w') as f:
        json.dump(data, f)

    # Copy thumbnails
    thumbs_dst = os.path.join(OUT, 'thumbnails')
    if os.path.exists(THUMBS_SRC):
        shutil.copytree(THUMBS_SRC, thumbs_dst)

    # Copy index.html
    shutil.copy(os.path.join(BASE, 'static_index.html'), os.path.join(OUT, 'index.html'))

    conn.close()
    print(f'Static site built in _site/ ({len(tree_list)} games)')

if __name__ == '__main__':
    main()
