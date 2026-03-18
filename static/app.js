/* ── Creatives Catalog — client-side logic ──────────────────────────────── */

let currentSeq = null;
let currentCode1c = '';
let currentShortName = '';

/* ── Create page: fetch next sequence number ─────────────────────────────── */

function fetchSeq() {
    const gameId = document.getElementById('game_id')?.value;
    const type = document.getElementById('type')?.value;
    if (!gameId || !type) return;

    fetch(`/api/next-seq?game_id=${gameId}&type=${type}`)
        .then(r => r.json())
        .then(data => {
            currentSeq = data.next_seq;
            currentCode1c = data.code_1c;
            currentShortName = data.short_name;

            const seqInfo = document.getElementById('seqInfo');
            const seqNumber = document.getElementById('seqNumber');
            if (seqInfo && seqNumber) {
                seqNumber.textContent = String(currentSeq).padStart(3, '0');
                seqInfo.style.display = 'block';
            }
            updatePreview();
            checkReady();
        });
}

/* ── Create page: type change handler ─────────────────────────────────────── */

function onTypeChange() {
    fetchSeq();
}

/* ── Create page: file selection & auto-detect ───────────────────────────── */

function onFileSelected(input) {
    const file = input.files[0];
    if (!file) return;

    const drop = document.getElementById('fileDrop');
    const preview = document.getElementById('filePreview');
    if (drop) {
        drop.classList.add('has-file');
        drop.querySelector('p').textContent = file.name;
    }

    const url = URL.createObjectURL(file);

    if (file.type.startsWith('image/')) {
        if (preview) preview.innerHTML = `<img src="${url}" alt="Preview">`;
        const img = new window.Image();
        img.onload = function () {
            setDimensions(img.naturalWidth, img.naturalHeight);
            updatePreview();
            checkReady();
        };
        img.src = url;
    } else if (file.type.startsWith('video/')) {
        if (preview) preview.innerHTML = `<video src="${url}" controls style="max-width:100%;max-height:300px;"></video>`;
        const video = document.createElement('video');
        video.preload = 'metadata';
        video.onloadedmetadata = function () {
            setDimensions(video.videoWidth, video.videoHeight);
            const durInput = document.getElementById('duration_sec');
            if (durInput && video.duration && isFinite(video.duration)) {
                durInput.value = Math.round(video.duration);
            }
            updatePreview();
            checkReady();
        };
        video.src = url;
    } else {
        if (preview) preview.innerHTML = `<span class="placeholder-text">${file.name}</span>`;
        checkReady();
    }
}

function setDimensions(w, h) {
    const wi = document.getElementById('width');
    const hi = document.getElementById('height');
    if (wi) wi.value = w;
    if (hi) hi.value = h;
}

/* ── Create page: live name preview ──────────────────────────────────────── */

function updatePreview() {
    const nameEl = document.getElementById('generatedName');
    if (!nameEl) return;

    const type = document.getElementById('type')?.value;
    const seasonal = document.getElementById('seasonal_tag')?.value || 'STD';
    const width = document.getElementById('width')?.value;
    const height = document.getElementById('height')?.value;
    const duration = document.getElementById('duration_sec')?.value;

    if (!type || !currentSeq || !currentCode1c) {
        nameEl.textContent = '—';
        return;
    }

    const tag = seasonal === 'STD' ? '' : seasonal;
    const n = String(currentSeq).padStart(3, '0');
    const size = width && height ? `_${width}x${height}` : '';
    const dur = duration ? `_${duration}s` : '';

    let name = '';
    if (type === 'Video') {
        name = `V${n}${tag}_${currentCode1c}_${currentShortName}${size}${dur}`;
    } else if (type === 'Banner') {
        name = `B${n}${tag}_${currentCode1c}_${currentShortName}${size}`;
    } else if (type === 'Playable') {
        name = `PLAY_${n}${tag}_${currentCode1c}_${currentShortName}`;
    }

    nameEl.textContent = name || '—';
}

/* ── Create page: enable submit only when form is ready ──────────────────── */

function checkReady() {
    const btn = document.getElementById('submitBtn');
    if (!btn) return;
    const gameId = document.getElementById('game_id')?.value;
    const type = document.getElementById('type')?.value;
    const file = document.getElementById('fileInput')?.files[0];
    btn.disabled = !(gameId && type && file);
}

/* ── Catalog page: tree toggle ────────────────────────────────────────────── */

function toggleTree(header) {
    header.classList.toggle('open');
    const children = header.nextElementSibling;
    if (children) {
        children.style.display = children.style.display === 'none' ? 'block' : 'none';
    }
}

/* ── Catalog page: modal add ──────────────────────────────────────────────── */

let mSeq = null, mCode = '', mShort = '';

function quickAdd(gameId, type) {
    const modal = document.getElementById('addModal');
    document.getElementById('m_game_id').value = gameId;
    document.getElementById('m_type').value = type;
    document.getElementById('m_seasonal').value = 'STD';
    document.getElementById('m_file').value = '';
    document.getElementById('m_width').value = '';
    document.getElementById('m_height').value = '';
    document.getElementById('m_duration').value = '';
    document.getElementById('m_submit').disabled = true;
    const drop = document.getElementById('modalFileDrop');
    if (drop) { drop.classList.remove('has-file'); drop.querySelector('p').textContent = 'Перетащите файл или нажмите для выбора'; }
    modal.style.display = 'flex';
    modalFetchSeq();
}

function closeModal() {
    document.getElementById('addModal').style.display = 'none';
}

function modalFetchSeq() {
    const gameId = document.getElementById('m_game_id')?.value;
    const type = document.getElementById('m_type')?.value;
    if (!gameId || !type) return;
    fetch(`/api/next-seq?game_id=${gameId}&type=${type}`)
        .then(r => r.json())
        .then(data => {
            mSeq = data.next_seq;
            mCode = data.code_1c;
            mShort = data.short_name;
            modalUpdateName();
        });
}

function modalUpdateName() {
    const el = document.getElementById('m_name');
    if (!el || !mSeq) { if (el) el.textContent = '—'; return; }
    const type = document.getElementById('m_type')?.value;
    const seasonal = document.getElementById('m_seasonal')?.value || 'STD';
    const w = document.getElementById('m_width')?.value;
    const h = document.getElementById('m_height')?.value;
    const dur = document.getElementById('m_duration')?.value;
    const tag = seasonal === 'STD' ? '' : seasonal;
    const n = String(mSeq).padStart(3, '0');
    const size = w && h ? `_${w}x${h}` : '';
    const d = dur ? `_${dur}s` : '';
    let name = '';
    if (type === 'Video') name = `V${n}${tag}_${mCode}_${mShort}${size}${d}`;
    else if (type === 'Banner') name = `B${n}${tag}_${mCode}_${mShort}${size}`;
    else if (type === 'Playable') name = `PLAY_${n}${tag}_${mCode}_${mShort}`;
    el.textContent = name || '—';
}

function modalFileSelected(input) {
    const file = input.files[0];
    if (!file) return;
    const drop = document.getElementById('modalFileDrop');
    if (drop) { drop.classList.add('has-file'); drop.querySelector('p').textContent = file.name; }
    const url = URL.createObjectURL(file);
    if (file.type.startsWith('image/')) {
        const img = new window.Image();
        img.onload = function () {
            document.getElementById('m_width').value = img.naturalWidth;
            document.getElementById('m_height').value = img.naturalHeight;
            modalUpdateName();
        };
        img.src = url;
    } else if (file.type.startsWith('video/')) {
        const video = document.createElement('video');
        video.preload = 'metadata';
        video.onloadedmetadata = function () {
            document.getElementById('m_width').value = video.videoWidth;
            document.getElementById('m_height').value = video.videoHeight;
            if (video.duration && isFinite(video.duration))
                document.getElementById('m_duration').value = Math.round(video.duration);
            modalUpdateName();
        };
        video.src = url;
    }
    document.getElementById('m_submit').disabled = false;
}

// Modal drag & drop
document.addEventListener('DOMContentLoaded', () => {
    const drop = document.getElementById('modalFileDrop');
    if (!drop) return;
    drop.addEventListener('dragover', e => { e.preventDefault(); drop.classList.add('dragover'); });
    drop.addEventListener('dragleave', () => drop.classList.remove('dragover'));
    drop.addEventListener('drop', e => {
        e.preventDefault();
        drop.classList.remove('dragover');
        const input = document.getElementById('m_file');
        if (input && e.dataTransfer.files.length) {
            input.files = e.dataTransfer.files;
            modalFileSelected(input);
        }
    });
});

/* ── Catalog page: toggle renditions (file list) ─────────────────────────── */

function toggleFiles(toggle) {
    toggle.classList.toggle('open');
    const tr = toggle.closest('tr');
    const rendRow = tr.nextElementSibling;
    if (rendRow && rendRow.classList.contains('renditions-row')) {
        rendRow.style.display = rendRow.style.display === 'none' ? 'table-row' : 'none';
    }
}

/* ── Catalog page: toggle network ─────────────────────────────────────────── */

function toggleNetwork(badge) {
    const id = badge.dataset.id;
    const net = badge.dataset.net;

    fetch(`/api/creatives/${id}/networks`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ network: net }),
    })
        .then(r => r.json())
        .then(data => {
            badge.classList.toggle('badge-net-on', data.networks.includes(net));
        });
}

/* ── Catalog page: change status ─────────────────────────────────────────── */

function changeStatus(select) {
    const id = select.dataset.id;
    const status = select.value;

    fetch(`/api/creatives/${id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
    })
        .then(r => r.json())
        .then(data => {
            select.className = `status-select status-${data.status.toLowerCase()}`;
        });
}

/* ── Catalog page: delete creative ───────────────────────────────────────── */

function deleteCreative(id, btn) {
    if (!confirm('Удалить этот креатив?')) return;

    fetch(`/api/creatives/${id}`, { method: 'DELETE' })
        .then(r => r.json())
        .then(() => {
            const row = btn.closest('tr') || btn.closest('.card');
            if (row) row.remove();
        });
}

/* ── Drag & drop ─────────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
    const drop = document.getElementById('fileDrop');
    if (!drop) return;

    drop.addEventListener('dragover', e => { e.preventDefault(); drop.classList.add('dragover'); });
    drop.addEventListener('dragleave', () => drop.classList.remove('dragover'));
    drop.addEventListener('drop', e => {
        e.preventDefault();
        drop.classList.remove('dragover');
        const input = document.getElementById('fileInput');
        if (input && e.dataTransfer.files.length) {
            input.files = e.dataTransfer.files;
            onFileSelected(input);
        }
    });
});
