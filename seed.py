"""Seed script: 20 games × 3 types × 2-3 renditions each."""
import os
import shutil
import sqlite3
import random
from PIL import Image, ImageDraw

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'creatives.db')
UPLOADS = os.path.join(BASE_DIR, 'uploads')
THUMBS = os.path.join(BASE_DIR, 'thumbnails')

GAMES = [
    ('7448', 'Car Crash Simulator', 'CarCrash'),
    ('8901', 'Merge Kingdom', 'MergeKingdom'),
    ('6523', 'Tower Defense Pro', 'TowerDef'),
    ('3310', 'Zombie Survival', 'ZombieSurv'),
    ('4215', 'Candy Blast', 'CandyBlast'),
    ('5572', 'Idle Factory', 'IdleFactory'),
    ('6680', 'Sniper Elite 3D', 'Sniper3D'),
    ('7791', 'Dragon Tamer', 'DragonTamer'),
    ('2204', 'Word Puzzle Master', 'WordPuzzle'),
    ('1133', 'Racing Fever', 'RacingFever'),
    ('8845', 'Farm & Harvest', 'FarmHarvest'),
    ('9902', 'Space Commander', 'SpaceCmd'),
    ('3056', 'Block Builder', 'BlockBuild'),
    ('4478', 'Pirate Legends', 'PirateLeg'),
    ('5591', 'Cooking Dash', 'CookDash'),
    ('6617', 'Stickman Warriors', 'StickWar'),
    ('7730', 'Bubble Pop Mania', 'BubblePop'),
    ('8844', 'Tank Battle Royale', 'TankBR'),
    ('9951', 'Pet Hospital', 'PetHosp'),
    ('1029', 'Archery King', 'ArcheryKing'),
]

COLORS = [
    (88, 166, 255), (63, 185, 80), (248, 81, 73), (188, 140, 255),
    (240, 136, 62), (57, 210, 192), (210, 153, 34), (255, 123, 160),
    (100, 200, 150), (180, 100, 220), (255, 180, 50), (50, 180, 220),
    (220, 80, 80), (80, 220, 140), (140, 80, 220), (220, 180, 80),
    (80, 140, 220), (220, 100, 180), (100, 220, 200), (200, 220, 80),
]

VIDEO_RENDITIONS = [
    (1920, 1080, 30), (1080, 1920, 30), (1280, 720, 15),
]
BANNER_RENDITIONS = [
    (1020, 500), (300, 250), (728, 90),
]
ALL_TAGS = ['gameplay', 'mislead', 'UGC', 'seasonal']
STATUSES = ['Draft', 'Ready', 'Active', 'Active', 'Archived']


def make_image(path, w, h, color, label):
    img = Image.new('RGB', (w, h), color=color)
    ImageDraw.Draw(img).text((10, 10), label, fill=(255, 255, 255))
    img.save(path)


def make_thumb(src, dst):
    with Image.open(src) as img:
        img.thumbnail((400, 400))
        img.save(dst)


def concept_name(ctype, seq, code, short):
    n = str(seq).zfill(3)
    if ctype == 'Video':
        return f'V{n}_{code}_{short}'
    if ctype == 'Banner':
        return f'B{n}_{code}_{short}'
    return f'PLAY_{n}_{code}_{short}'


def rendition_name(cname, ctype, w=None, h=None, dur=None):
    if ctype == 'Video':
        return f'{cname}_{w}x{h}_{dur}s' if w else cname
    if ctype == 'Banner':
        return f'{cname}_{w}x{h}' if w else cname
    return cname


def main():
    # Clean up
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    for d in (UPLOADS, THUMBS):
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)

    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.executescript('''
        CREATE TABLE games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_1c TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            short_name TEXT NOT NULL,
            platform TEXT DEFAULT 'Both'
        );
        CREATE TABLE creatives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL REFERENCES games(id),
            type TEXT NOT NULL,
            seq_number INTEGER NOT NULL,
            concept_name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Draft',
            networks TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(game_id, type, seq_number)
        );
        CREATE TABLE renditions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creative_id INTEGER NOT NULL REFERENCES creatives(id) ON DELETE CASCADE,
            width INTEGER,
            height INTEGER,
            duration_sec INTEGER,
            file_path TEXT,
            thumbnail_path TEXT,
            generated_name TEXT NOT NULL,
            original_filename TEXT,
            file_size_mb REAL
        );
    ''')

    for code, name, short in GAMES:
        cur.execute(
            'INSERT INTO games (code_1c, name, short_name, platform) VALUES (?,?,?,?)',
            (code, name, short, random.choice(['Android', 'iOS', 'Both'])),
        )
    conn.commit()

    games = cur.execute('SELECT id, code_1c, short_name FROM games').fetchall()

    total_concepts = 0
    total_renditions = 0

    for idx, (gid, code, short) in enumerate(games):
        color = COLORS[idx % len(COLORS)]

        num_concepts = 12 if idx < 5 else 1

        for ctype in ('Video', 'Banner', 'Playable'):
          for seq in range(1, num_concepts + 1):
            status = random.choice(STATUSES)
            tags = ','.join(random.sample(ALL_TAGS, k=random.randint(0, 3)))
            cname = concept_name(ctype, seq, code, short)

            cur.execute(
                'INSERT INTO creatives (game_id,type,seq_number,concept_name,description,status,tags) '
                'VALUES (?,?,?,?,?,?,?)',
                (gid, ctype, seq, cname, f'{short} {ctype} concept {seq}', status, tags),
            )
            cid = cur.lastrowid
            total_concepts += 1

            # Create renditions
            if ctype == 'Video':
                rends = VIDEO_RENDITIONS[:random.randint(2, 3)]
                for w, h, dur in rends:
                    rname = rendition_name(cname, ctype, w, h, dur)
                    fname = f'{rname}.mp4'
                    fpath = os.path.join(UPLOADS, fname)
                    with open(fpath, 'wb') as f:
                        f.write(b'\x00' * 1024)
                    cur.execute(
                        'INSERT INTO renditions (creative_id,width,height,duration_sec,'
                        'file_path,generated_name,original_filename,file_size_mb) VALUES (?,?,?,?,?,?,?,?)',
                        (cid, w, h, dur, fname, rname, fname, 0.0),
                    )
                    total_renditions += 1

            elif ctype == 'Banner':
                rends = BANNER_RENDITIONS[:random.randint(2, 3)]
                for w, h in rends:
                    rname = rendition_name(cname, ctype, w, h)
                    fname = f'{rname}.png'
                    fpath = os.path.join(UPLOADS, fname)
                    label = f'{short} / B#{seq} / {w}x{h}'
                    make_image(fpath, w, h, color, label)
                    thumb_name = f'thumb_{rname}.png'
                    make_thumb(fpath, os.path.join(THUMBS, thumb_name))
                    size_mb = round(os.path.getsize(fpath) / (1024 * 1024), 2)
                    cur.execute(
                        'INSERT INTO renditions (creative_id,width,height,'
                        'file_path,thumbnail_path,generated_name,original_filename,file_size_mb) '
                        'VALUES (?,?,?,?,?,?,?,?)',
                        (cid, w, h, fname, thumb_name, rname, fname, size_mb),
                    )
                    total_renditions += 1

            elif ctype == 'Playable':
                rname = rendition_name(cname, ctype)
                fname = f'{rname}.html'
                fpath = os.path.join(UPLOADS, fname)
                with open(fpath, 'w') as f:
                    f.write(f'<html><body><h1>{short} Playable</h1></body></html>')
                cur.execute(
                    'INSERT INTO renditions (creative_id,'
                    'file_path,generated_name,original_filename,file_size_mb) '
                    'VALUES (?,?,?,?,?)',
                    (cid, fname, rname, fname, 0.0),
                )
                total_renditions += 1

    conn.commit()
    conn.close()
    print(f'Done: {len(GAMES)} games, {total_concepts} concepts, {total_renditions} renditions')


if __name__ == '__main__':
    main()
