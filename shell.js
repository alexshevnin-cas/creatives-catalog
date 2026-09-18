/* Shared shell: sidebar rail + topbar + breadcrumbs + tabs. Call writeShell() right after <body>. */
function writeShell(opts) {
    var active = opts.active;
    var title = opts.title || 'Creatives Catalog';
    var svg = function (path) {
        return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' + path + '</svg>';
    };
    var I = {
        home: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
        analytics: '<path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 20v-7"/><path d="M22 20H2"/>',
        apps: '<rect x="7" y="2" width="10" height="20" rx="2.5"/><path d="M11 18h2"/>',
        networks: '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/>',
        payments: '<rect x="2" y="6" width="20" height="13" rx="2.5"/><path d="M2 10h20"/>',
        internal: '<rect x="4" y="3" width="16" height="18" rx="2.5"/><path d="M9 8h6"/><path d="M9 12h6"/><path d="M9 16h3"/>',
        admin: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
        catalog: '<rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M3 9h18"/><path d="M9 20V9"/>',
        history: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
        inbox: '<path d="M3 13l2.5-8h13L21 13v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M3 13h5l1.5 3h5L16 13h5"/>',
        stats: '<path d="M5 20V12"/><path d="M12 20V4"/><path d="M19 20v-6"/>',
        crumbHome: '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>'
    };
    /* every page of this app lives under Internal Services; the Applications reference also lights its own item */
    var sideActive = active === 'apps' ? 'apps' : 'internal';
    var sideItem = function (href, key, label, icon, extra) {
        return '<a class="side-item' + (sideActive === key ? ' active' : '') + (extra === 'soon' ? ' soon' : '') + '" href="' + href + '"' +
            (extra === 'soon' ? ' onclick="event.preventDefault();toast(\'Networks management is coming with the Networks phase (Phase 3)\')"' : '') +
            ' title="' + label + '"><span class="side-ic">' + svg(icon) + '</span><span class="side-label">' + label + '</span>' +
            (extra === 'soon' ? '<span class="side-soon">SOON</span>' : '') + '</a>';
    };
    var tabs = [
        ['index.html', 'catalog', 'Catalog', I.catalog, ''],
        ['history.html', 'history', 'History', I.history, '<span class="tab-dot" title="New files on Google Drive"></span>'],
        ['inbox.html', 'inbox', 'Inbox', I.inbox, ''],
        ['statistics.html', 'stats', 'Statistics', I.stats, '']
    ];
    var tabsHtml = tabs.map(function (t) {
        return '<a href="' + t[0] + '"' + (active === t[1] ? ' class="active"' : '') + '>' + svg(t[3]) + t[2] + t[4] + '</a>';
    }).join('');

    document.write(
        '<aside class="sidebar">' +
            '<a class="side-logo" href="index.html"><span class="logo-mark"><svg viewBox="0 0 36 36"><circle cx="18" cy="18" r="17" fill="#141418"/><path d="M11 12.5h13.5L15 24h9.5" stroke="#fff" stroke-width="3.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg><i class="logo-dot"></i></span><span class="brand">CAS.<b>A</b>I</span><span class="brand-tag">FDID-1410-Creatives</span></a>' +
            sideItem('index.html', 'home', 'Home', I.home) +
            sideItem('#', 'analytics', 'Analytics', I.analytics) +
            sideItem('games.html', 'apps', 'Applications', I.apps) +
            sideItem('#', 'networks', 'Networks', I.networks, 'soon') +
            sideItem('#', 'payments', 'Payments', I.payments) +
            '<span class="side-spacer"></span>' +
            sideItem('index.html', 'internal', 'Internal Services', I.internal) +
            sideItem('#', 'admin', 'Admin', I.admin) +
            '<div class="side-sep"></div>' +
            '<div class="side-user"><span class="avatar">A</span><span class="side-label">admin@cas.ai</span></div>' +
        '</aside>' +
        '<div class="shell">' +
            '<header class="topbar">' +
                '<div class="tb-left">' +
                    '<div class="tb-title-block">' +
                        '<div class="tb-eyebrow">Internal Services</div>' +
                        '<div class="tb-title-row"><h1>' + title + '</h1><span class="stamp">Prototype</span></div>' +
                    '</div>' +
                    '<div class="tb-sub">Data through Sep 18, 2026 &middot; up to date</div>' +
                '</div>' +
                '<div class="tb-right">' +
                    '<span class="pill-internal">&#9432; INTERNAL</span>' +
                    '<span class="theme-dot" title="Theme">&#9728;&#65039;</span>' +
                    '<span class="lang">EN</span>' +
                '</div>' +
            '</header>' +
            '<div class="subbar">' +
                '<nav class="crumbs">' +
                    '<a class="crumb" href="index.html">' + svg(I.crumbHome) + 'Home</a><span class="crumb-sep">&rsaquo;</span>' +
                    '<a class="crumb" href="index.html">Internal Services</a><span class="crumb-sep">&rsaquo;</span>' +
                    '<span class="crumb cur">' + title + '</span>' +
                '</nav>' +
                '<nav class="tabs">' + tabsHtml + '</nav>' +
            '</div>'
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
/* deterministic 0..1 from a string */
function rnd01(str) { return (parseInt(hash36(str, 6), 36) % 100000) / 100000; }

var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
function fmtDate(d) {
    return MONTHS[d.getMonth()] + ' ' + d.getDate() + ', ' + d.getFullYear();
}
function fmtNum(n) { return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
function fmtMoney(n) { return '$' + fmtNum(n); }
var TODAY = new Date(2026, 8, 18); /* prototype freeze date */
function daysAgo(n) {
    var d = new Date(TODAY);
    d.setDate(d.getDate() - n);
    return d;
}
