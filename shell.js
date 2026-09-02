/* Shared shell: sidebar + topbar + tabs. Call writeShell() right after <body>. */
function writeShell(opts) {
    var active = opts.active;
    var title = opts.title || 'Creatives Catalog';
    var ic = function (path) {
        return '<span class="side-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' + path + '</svg></span>';
    };
    var tabs = [
        ['index.html', 'catalog', 'Catalog', ''],
        ['history.html', 'history', 'History', '<span class="tab-dot" title="New files on Google Drive"></span>'],
        ['inbox.html', 'inbox', 'Inbox', ''],
        ['statistics.html', 'stats', 'Statistics', '<span class="tab-new">new</span>'],
        ['games.html', 'apps', 'Applications', '']
    ];
    var tabsHtml = tabs.map(function (t) {
        return '<a href="' + t[0] + '"' + (active === t[1] ? ' class="active"' : '') + '>' + t[2] + t[3] + '</a>';
    }).join('');

    document.write(
        '<aside class="sidebar">' +
            '<a class="side-logo" href="index.html"><img src="logo.png" alt="CAS.AI"></a>' +
            ic('<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>') +
            ic('<path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 20v-7"/><path d="M22 20H2"/>') +
            ic('<rect x="7" y="2" width="10" height="20" rx="2.5"/><path d="M11 18h2"/>') +
            ic('<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/>') +
            ic('<rect x="2" y="6" width="20" height="13" rx="2.5"/><path d="M2 10h20"/>') +
            '<span class="side-spacer"></span>' +
            ic('<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-3.5 4.5-5 8-5s6.5 1.5 8 5"/>') +
        '</aside>' +
        '<div class="shell">' +
            '<header class="topbar">' +
                '<div class="tb-left">' +
                    '<div class="tb-title-block">' +
                        '<div class="tb-eyebrow">Internal Services</div>' +
                        '<div class="tb-title-row"><h1>' + title + '</h1><span class="stamp">Prototype</span></div>' +
                    '</div>' +
                    '<div class="tb-sub">Data through Aug 28, 2026 &middot; up to date</div>' +
                '</div>' +
                '<div class="tb-right">' +
                    '<span class="pill-internal">&#9888; Internal</span>' +
                    '<span class="theme-dot" title="Theme"></span>' +
                    '<span class="lang">EN</span>' +
                '</div>' +
            '</header>' +
            '<nav class="tabs">' + tabsHtml + '</nav>'
    );
    /* .shell stays open — page supplies <main class="content">, auto-closed at </body> */
}

function toast(msg) {
    var el = document.getElementById('toast');
    if (!el) {
        el = document.createElement('div');
        el.id = 'toast';
        document.body.appendChild(el);
    }
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(el._t);
    el._t = setTimeout(function () { el.classList.remove('show'); }, 2600);
}

function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
}

/* deterministic tiny hash → base36 string of given length */
function hash36(str, len) {
    var h = 2166136261;
    for (var i = 0; i < str.length; i++) {
        h ^= str.charCodeAt(i);
        h = (h * 16777619) >>> 0;
    }
    var out = '';
    while (out.length < len) {
        out += h.toString(36);
        h = (h * 2654435761 + 1) >>> 0;
    }
    return out.slice(0, len);
}

var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
function fmtDate(d) {
    return MONTHS[d.getMonth()] + ' ' + d.getDate() + ', ' + d.getFullYear();
}
var TODAY = new Date(2026, 7, 28); /* prototype freeze date */
function daysAgo(n) {
    var d = new Date(TODAY);
    d.setDate(d.getDate() - n);
    return d;
}
