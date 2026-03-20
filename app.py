import os
import sqlite3
from collections import OrderedDict
from contextlib import contextmanager

from flask import (
    Flask, render_template, request, redirect,
    url_for, jsonify, send_from_directory, flash
)
from werkzeug.utils import secure_filename
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = 'creatives-catalog-dev-key'
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['THUMBNAIL_FOLDER'] = os.path.join(BASE_DIR, 'thumbnails')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB

DATABASE = os.path.join(BASE_DIR, 'creatives.db')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)

CREATIVE_TYPES = ('Video', 'Banner', 'Playable')
STATUSES = ('Draft', 'Ready', 'Active', 'Archived')
PLATFORMS = ('Android', 'iOS', 'Both')
NETWORKS = ('Mintegral', 'FB', 'TikTok', 'Google Ads')
TAGS = ('gameplay', 'mislead', 'UGC', 'seasonal')

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.webm', '.mkv'}


# ── Database ─────────────────────────────────────────────────────────────────

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_db() as db:
        tables = [r[0] for r in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]

        # Migrate: if old schema (no renditions table), drop creatives
        if 'creatives' in tables and 'renditions' not in tables:
            db.execute('DROP TABLE creatives')

        # Migrate: add networks column if missing
        if 'creatives' in tables:
            cols = [r[1] for r in db.execute('PRAGMA table_info(creatives)').fetchall()]
            if 'networks' not in cols:
                db.execute("ALTER TABLE creatives ADD COLUMN networks TEXT DEFAULT ''")
            if 'tags' not in cols:
                db.execute("ALTER TABLE creatives ADD COLUMN tags TEXT DEFAULT ''")

        db.executescript('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_1c TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                short_name TEXT NOT NULL,
                platform TEXT DEFAULT 'Both'
            );

            CREATE TABLE IF NOT EXISTS creatives (
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

            CREATE TABLE IF NOT EXISTS renditions (
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

        count = db.execute('SELECT COUNT(*) FROM games').fetchone()[0]
        if count == 0:
            db.executemany(
                'INSERT INTO games (code_1c, name, short_name, platform) VALUES (?,?,?,?)',
                [
                    ('7448', 'Car Crash Simulator', 'CarCrash', 'Both'),
                    ('8901', 'Merge Kingdom', 'MergeKingdom', 'Both'),
                    ('6523', 'Tower Defense Pro', 'TowerDef', 'Android'),
                ],
            )


# ── Naming convention ────────────────────────────────────────────────────────

def get_next_seq(db, game_id, creative_type):
    row = db.execute(
        'SELECT COALESCE(MAX(seq_number), 0) + 1 FROM creatives '
        'WHERE game_id = ? AND type = ?',
        (game_id, creative_type),
    ).fetchone()
    return row[0]


def make_concept_name(creative_type, seq, code_1c, short_name):
    n = str(seq).zfill(3)
    if creative_type == 'Video':
        return f'V{n}_{code_1c}_{short_name}'
    if creative_type == 'Banner':
        return f'B{n}_{code_1c}_{short_name}'
    if creative_type == 'Playable':
        return f'PLAY_{n}_{code_1c}_{short_name}'
    return f'X{n}_{code_1c}_{short_name}'


def make_rendition_name(concept_name, creative_type, width=None, height=None, duration_sec=None):
    size = f'_{width}x{height}' if width and height else ''
    dur = f'_{duration_sec}s' if duration_sec else ''
    if creative_type == 'Video':
        return f'{concept_name}{size}{dur}'
    if creative_type == 'Banner':
        return f'{concept_name}{size}'
    return concept_name


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_thumbnail(src, dst, size=(400, 400)):
    try:
        with Image.open(src) as img:
            img.thumbnail(size)
            img.save(dst)
            return True
    except Exception:
        return False


def file_kind(ext):
    if ext in IMAGE_EXTENSIONS:
        return 'image'
    if ext in VIDEO_EXTENSIONS:
        return 'video'
    return 'other'


# ── Routes: pages ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('catalog'))


@app.route('/catalog')
def catalog():
    with get_db() as db:
        games_list = db.execute('SELECT * FROM games ORDER BY short_name').fetchall()

        q = (
            'SELECT c.id AS c_id, c.game_id, c.type, c.seq_number, '
            'c.concept_name, c.description, c.status, c.networks, c.tags, '
            'g.code_1c, g.name AS game_name, g.short_name, '
            'r.id AS r_id, r.width, r.height, r.duration_sec, '
            'r.file_path, r.thumbnail_path, r.generated_name AS r_name, r.file_size_mb '
            'FROM creatives c '
            'JOIN games g ON c.game_id = g.id '
            'LEFT JOIN renditions r ON r.creative_id = c.id '
            'WHERE 1=1'
        )
        params = []

        for col, arg in [('c.game_id', 'game'), ('c.type', 'type'),
                         ('c.status', 'status')]:
            val = request.args.get(arg)
            if val:
                q += f' AND {col} = ?'
                params.append(val)

        tag_filter = request.args.get('tag')
        if tag_filter:
            q += " AND (',' || c.tags || ',') LIKE ?"
            params.append(f'%,{tag_filter},%')

        search = request.args.get('search', '').strip()
        if search:
            q += ' AND (c.concept_name LIKE ? OR r.generated_name LIKE ?)'
            params += [f'%{search}%', f'%{search}%']

        q += (" ORDER BY CASE g.short_name WHEN 'CarCrash' THEN 0 ELSE 1 END, g.short_name,"
              " CASE c.type WHEN 'Video' THEN 0 WHEN 'Banner' THEN 1"
              " WHEN 'Playable' THEN 2 ELSE 3 END,"
              " c.seq_number DESC, r.width DESC")
        rows = db.execute(q, params).fetchall()

    # Build tree: game → type → concepts (with renditions list)
    tree = OrderedDict()
    concepts_idx = {}  # c_id → concept dict reference

    for r in rows:
        gkey = r['game_name']
        if gkey not in tree:
            tree[gkey] = {
                'game_id': r['game_id'],
                'code_1c': r['code_1c'], 'short_name': r['short_name'],
                'types': OrderedDict(),
            }

        tkey = r['type']
        if tkey not in tree[gkey]['types']:
            tree[gkey]['types'][tkey] = []

        c_id = r['c_id']
        if c_id not in concepts_idx:
            concept = {
                'id': c_id,
                'seq_number': r['seq_number'],
                'concept_name': r['concept_name'],
                'status': r['status'],
                'networks': [n for n in (r['networks'] or '').split(',') if n],
                'tags': [t for t in (r['tags'] or '').split(',') if t],
                'renditions': [],
            }
            tree[gkey]['types'][tkey].append(concept)
            concepts_idx[c_id] = concept

        if r['r_id']:
            concepts_idx[c_id]['renditions'].append({
                'id': r['r_id'],
                'width': r['width'],
                'height': r['height'],
                'duration_sec': r['duration_sec'],
                'file_path': r['file_path'],
                'thumbnail_path': r['thumbnail_path'],
                'generated_name': r['r_name'],
                'file_size_mb': r['file_size_mb'],
            })

    filters = {k: request.args.get(k, '') for k in ('game', 'type', 'tag', 'status', 'search')}
    return render_template('catalog.html', tree=tree, games=games_list,
                           filters=filters, types=CREATIVE_TYPES,
                           statuses=STATUSES, networks=NETWORKS,
                           tags=TAGS)


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        with get_db() as db:
            games_list = db.execute('SELECT * FROM games ORDER BY short_name').fetchall()
        return render_template('create.html', games=games_list,
                               types=CREATIVE_TYPES, tags=TAGS)

    # ── POST ──
    game_id = request.form.get('game_id', type=int)
    creative_type = request.form.get('type')
    selected_tags = request.form.getlist('tags')
    tags_str = ','.join(t for t in selected_tags if t in TAGS)
    description = request.form.get('description', '').strip()
    width = request.form.get('width', type=int)
    height = request.form.get('height', type=int)
    duration_sec = request.form.get('duration_sec', type=int)
    file = request.files.get('file')

    if not game_id or not creative_type or not file or not file.filename:
        flash('Заполните все обязательные поля и прикрепите файл', 'error')
        return redirect(url_for('create'))

    with get_db() as db:
        game = db.execute('SELECT * FROM games WHERE id = ?', (game_id,)).fetchone()
        if not game:
            flash('Игра не найдена', 'error')
            return redirect(url_for('create'))

        seq = get_next_seq(db, game_id, creative_type)
        cname = make_concept_name(creative_type, seq,
                                  game['code_1c'], game['short_name'])
        rname = make_rendition_name(cname, creative_type, width, height, duration_sec)

        # Save file
        original = secure_filename(file.filename)
        ext = os.path.splitext(original)[1].lower()
        saved = f'{rname}{ext}'
        dest = os.path.join(app.config['UPLOAD_FOLDER'], saved)
        file.save(dest)

        size_mb = round(os.path.getsize(dest) / (1024 * 1024), 2)

        thumb = None
        if ext in IMAGE_EXTENSIONS:
            thumb_name = f'thumb_{rname}.png'
            if make_thumbnail(dest, os.path.join(app.config['THUMBNAIL_FOLDER'], thumb_name)):
                thumb = thumb_name

        # Insert concept
        cur = db.execute(
            'INSERT INTO creatives (game_id,type,seq_number,concept_name,description,tags) '
            'VALUES (?,?,?,?,?,?)',
            (game_id, creative_type, seq, cname, description, tags_str),
        )
        creative_id = cur.lastrowid

        # Insert rendition
        db.execute(
            'INSERT INTO renditions '
            '(creative_id,width,height,duration_sec,file_path,thumbnail_path,'
            'generated_name,original_filename,file_size_mb) '
            'VALUES (?,?,?,?,?,?,?,?,?)',
            (creative_id, width, height, duration_sec, saved, thumb,
             rname, original, size_mb),
        )

    flash(f'Креатив создан: {rname}', 'success')
    return redirect(url_for('catalog'))


@app.route('/games')
def games():
    with get_db() as db:
        rows = db.execute('SELECT * FROM games ORDER BY short_name').fetchall()
    return render_template('games.html', games=rows, platforms=PLATFORMS)


# ── Routes: games CRUD ───────────────────────────────────────────────────────

@app.route('/games/add', methods=['POST'])
def games_add():
    code = request.form.get('code_1c', '').strip()
    name = request.form.get('name', '').strip()
    short = request.form.get('short_name', '').strip()
    platform = request.form.get('platform', 'Both')

    if not all([code, name, short]):
        flash('Заполните все поля', 'error')
        return redirect(url_for('games'))

    with get_db() as db:
        try:
            db.execute(
                'INSERT INTO games (code_1c, name, short_name, platform) VALUES (?,?,?,?)',
                (code, name, short, platform),
            )
            flash(f'Игра добавлена: {name}', 'success')
        except sqlite3.IntegrityError:
            flash(f'Код 1С «{code}» уже существует', 'error')

    return redirect(url_for('games'))


@app.route('/games/<int:gid>/edit', methods=['POST'])
def games_edit(gid):
    code = request.form.get('code_1c', '').strip()
    name = request.form.get('name', '').strip()
    short = request.form.get('short_name', '').strip()
    platform = request.form.get('platform', 'Both')

    if not all([code, name, short]):
        flash('Заполните все поля', 'error')
        return redirect(url_for('games'))

    with get_db() as db:
        db.execute(
            'UPDATE games SET code_1c=?, name=?, short_name=?, platform=? WHERE id=?',
            (code, name, short, platform, gid),
        )
        flash(f'Игра обновлена: {name}', 'success')

    return redirect(url_for('games'))


@app.route('/games/<int:gid>/delete', methods=['POST'])
def games_delete(gid):
    with get_db() as db:
        cnt = db.execute('SELECT COUNT(*) FROM creatives WHERE game_id=?', (gid,)).fetchone()[0]
        if cnt:
            flash(f'Нельзя удалить: к игре привязано {cnt} креативов', 'error')
        else:
            db.execute('DELETE FROM games WHERE id=?', (gid,))
            flash('Игра удалена', 'success')
    return redirect(url_for('games'))


# ── Routes: API ──────────────────────────────────────────────────────────────

@app.route('/api/creatives/quick-add', methods=['POST'])
def api_quick_add():
    data = request.get_json(silent=True) or {}
    game_id = data.get('game_id')
    ctype = data.get('type')
    if not game_id or ctype not in CREATIVE_TYPES:
        return jsonify(error='missing params'), 400
    with get_db() as db:
        game = db.execute('SELECT code_1c, short_name FROM games WHERE id=?', (game_id,)).fetchone()
        if not game:
            return jsonify(error='game not found'), 404
        seq = get_next_seq(db, game_id, ctype)
        cname = make_concept_name(ctype, seq, game['code_1c'], game['short_name'])
        db.execute(
            'INSERT INTO creatives (game_id,type,seq_number,concept_name) '
            'VALUES (?,?,?,?)',
            (game_id, ctype, seq, cname),
        )
    return jsonify(ok=True, concept_name=cname, seq=seq)


@app.route('/api/next-seq')
def api_next_seq():
    game_id = request.args.get('game_id', type=int)
    ctype = request.args.get('type')
    if not game_id or not ctype:
        return jsonify(error='missing params'), 400
    with get_db() as db:
        seq = get_next_seq(db, game_id, ctype)
        game = db.execute('SELECT code_1c, short_name FROM games WHERE id=?', (game_id,)).fetchone()
    return jsonify(next_seq=seq,
                   code_1c=game['code_1c'] if game else '',
                   short_name=game['short_name'] if game else '')


@app.route('/api/creatives/<int:cid>/networks', methods=['PATCH'])
def api_toggle_network(cid):
    data = request.get_json(silent=True) or {}
    network = data.get('network')
    if network not in NETWORKS:
        return jsonify(error='invalid network'), 400
    with get_db() as db:
        row = db.execute('SELECT networks FROM creatives WHERE id=?', (cid,)).fetchone()
        if not row:
            return jsonify(error='not found'), 404
        current = [n for n in (row['networks'] or '').split(',') if n]
        if network in current:
            current.remove(network)
        else:
            current.append(network)
        val = ','.join(current)
        db.execute('UPDATE creatives SET networks=? WHERE id=?', (val, cid))
    return jsonify(networks=current)


@app.route('/api/creatives/<int:cid>/tags', methods=['PATCH'])
def api_toggle_tag(cid):
    data = request.get_json(silent=True) or {}
    tag = data.get('tag')
    if tag not in TAGS:
        return jsonify(error='invalid tag'), 400
    with get_db() as db:
        row = db.execute('SELECT tags FROM creatives WHERE id=?', (cid,)).fetchone()
        if not row:
            return jsonify(error='not found'), 404
        current = [t for t in (row['tags'] or '').split(',') if t]
        if tag in current:
            current.remove(tag)
        else:
            current.append(tag)
        val = ','.join(current)
        db.execute('UPDATE creatives SET tags=? WHERE id=?', (val, cid))
    return jsonify(tags=current)


@app.route('/api/creatives/<int:cid>/status', methods=['PATCH'])
def api_update_status(cid):
    data = request.get_json(silent=True) or {}
    status = data.get('status')
    if status not in STATUSES:
        return jsonify(error='invalid status'), 400
    with get_db() as db:
        db.execute('UPDATE creatives SET status=? WHERE id=?', (status, cid))
    return jsonify(status=status)


@app.route('/api/creatives/<int:cid>', methods=['DELETE'])
def api_delete_creative(cid):
    with get_db() as db:
        rends = db.execute(
            'SELECT file_path, thumbnail_path FROM renditions WHERE creative_id=?', (cid,)
        ).fetchall()
        for r in rends:
            for field in ('file_path', 'thumbnail_path'):
                if r[field]:
                    p = os.path.join(
                        app.config['UPLOAD_FOLDER'] if field == 'file_path'
                        else app.config['THUMBNAIL_FOLDER'],
                        r[field],
                    )
                    if os.path.exists(p):
                        os.remove(p)
        db.execute('DELETE FROM creatives WHERE id=?', (cid,))
    return jsonify(ok=True)


# ── Static files ─────────────────────────────────────────────────────────────

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/thumbnails/<path:filename>')
def thumbnail_file(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)


# ── Jinja helpers ────────────────────────────────────────────────────────────

@app.template_filter('file_kind')
def file_kind_filter(path):
    if not path:
        return 'other'
    return file_kind(os.path.splitext(path)[1].lower())


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    print('Creatives Catalog running at http://localhost:5001')
    app.run(debug=True, port=5001)
