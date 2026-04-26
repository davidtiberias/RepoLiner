//  STATE
// ═══════════════════════════════════════════════════════════
let scanData = null;
let currentMode = "folder";
let manualOverrides = {
    included: new Set(),
    excluded: new Set()
};
let selectedTreeNode = null;

// ═══════════════════════════════════════════════════════════
//  API CALLS
// ═══════════════════════════════════════════════════════════

async function browseFolder() {
    const btn = document.getElementById('btnBrowse');
    btn.textContent = '...';
    btn.disabled = true;
    try {
        const res = await fetch('/api/browse', { method: 'POST' });
        const data = await res.json();
        if (data.success && data.path) {
            document.getElementById('pathInput').value = data.path;
            scanProject();
        }
    } catch (e) {
        console.error('Browse error:', e);
    }
    btn.textContent = 'Browse';
    btn.disabled = false;
}

async function scanProject() {
    const path = document.getElementById('pathInput').value.trim();
    if (!path) return;

    const loader = document.getElementById('treePanelLoader');
    loader.classList.add('active');
    document.getElementById('btnMerge').disabled = true;

    try {
        const res = await fetch('/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path }),
        });
        const data = await res.json();

        if (data.success) {
            scanData = data;
            scanData._path = path;
            renderTree(data.tree);
            renderExtensionsTab(data);
            renderFoldersTab(data);
            renderFilesTab(data);
            renderGitignoreTab(data);
            document.getElementById('btnMerge').disabled = false;
        } else {
            alert('Scan failed: ' + (data.error || 'Unknown error'));
        }
    } catch (e) {
        alert('Connection error: ' + e.message);
    }

    loader.classList.remove('active');
}

async function runMerge() {
    const path = scanData?._path;
    if (!path) return;

    const btn = document.getElementById('btnMerge');
    const origText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Working...';
    btn.disabled = true;

    // Collect current configuration from the UI
    const includedExts = getCheckedValues('ext-checkbox');
    const excludedDirs = getUncheckedValues('dir-checkbox');
    const excludedFiles = getUncheckedValues('file-checkbox');
    const gitignorePatterns = getCheckedValues('gitignore-checkbox');

    try {
        const res = await fetch('/api/merge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                path,
                mode: currentMode,
                included_extensions: includedExts,
                excluded_dirs: excludedDirs,
                excluded_files: excludedFiles,
                gitignore_patterns: gitignorePatterns,
                manually_included: Array.from(manualOverrides.included),
                manually_excluded: Array.from(manualOverrides.excluded)
            }),
        });
        const data = await res.json();
        showResult(data);
    } catch (e) {
        alert('Merge error: ' + e.message);
    }

    btn.innerHTML = origText;
    btn.disabled = false;
}

async function openFolder(type) {
    let folderPath = '';
    if (type === 'output') {
        folderPath = '__output__';
    } else {
        folderPath = document.getElementById('pathInput').value.trim();
        if (!folderPath) {
            alert('No project path set.');
            return;
        }
    }

    await fetch('/api/open-folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: folderPath }),
    });
}

// ═══════════════════════════════════════════════════════════
//  RENDER: Project Tree
// ═══════════════════════════════════════════════════════════

function renderTree(tree) {
    const container = document.getElementById('treeBody');
    let totalItems = 0;

    function countItems(nodes) {
        for (const n of nodes) {
            totalItems++;
            if (n.children) countItems(n.children);
        }
    }
    countItems(tree);

    container.innerHTML = buildTreeHTML(tree, true);
    document.getElementById('treeCount').textContent = `${totalItems} items`;

    // Add all event listeners
    container.querySelectorAll('.tree-toggle').forEach(el => {
        el.addEventListener('click', (e) => {
            e.stopPropagation();
            const node = el.closest('.tree-node');
            const children = node.querySelector('.tree-children');
            if (children) {
                children.classList.toggle('collapsed');
                el.classList.toggle('open');
            }
        });
    });

    container.querySelectorAll('.tree-checkbox').forEach(el => {
        el.addEventListener('change', (e) => {
            e.stopPropagation();
            const node = el.closest('.tree-node');
            const checked = el.checked;
            const path = el.dataset.path;

            // Record manual override
            const originalExcluded = isOriginallyExcluded(path);
            if (checked && originalExcluded) {
                manualOverrides.included.add(path);
                manualOverrides.excluded.delete(path);
            } else if (!checked && !originalExcluded) {
                manualOverrides.excluded.add(path);
                manualOverrides.included.delete(path);
            } else {
                manualOverrides.included.delete(path);
                manualOverrides.excluded.delete(path);
            }

            // Propagate to children
            node.querySelectorAll('.tree-checkbox').forEach(child => {
                child.checked = checked;
                child.indeterminate = false;
                const childPath = child.dataset.path;
                const childOrigExcluded = isOriginallyExcluded(childPath);
                if (checked && childOrigExcluded) {
                    manualOverrides.included.add(childPath);
                    manualOverrides.excluded.delete(childPath);
                } else if (!checked && !childOrigExcluded) {
                    manualOverrides.excluded.add(childPath);
                    manualOverrides.included.delete(childPath);
                } else {
                    manualOverrides.included.delete(childPath);
                    manualOverrides.excluded.delete(childPath);
                }
            });

            // Update UI (pins)
            refreshTreeVisuals();

            // Update parent indeterminate states
            updateParentCheckState(el);
            
            // Re-inspect if selected
            if (selectedTreeNode === path) {
                inspectNode(path);
            }
        });
    });
}

function isOriginallyExcluded(path) {
    if (!scanData) return false;
    // Helper to find node in tree
    function findNode(nodes) {
        for (const n of nodes) {
            if (n.path === path) return n;
            if (n.children) {
                const found = findNode(n.children);
                if (found) return found;
            }
        }
        return null;
    }
    const node = findNode(scanData.tree);
    return node ? node.excluded : false;
}

function refreshTreeVisuals() {
    document.querySelectorAll('.tree-node').forEach(node => {
        const path = node.dataset.path;
        const row = node.querySelector('.tree-row');
        const hasPin = manualOverrides.included.has(path) || manualOverrides.excluded.has(path);
        
        let pin = row.querySelector('.tree-pin');
        if (hasPin) {
            if (!pin) {
                pin = document.createElement('span');
                pin.className = 'tree-pin';
                pin.title = 'Manual Override';
                pin.textContent = '📌';
                row.querySelector('.tree-label').after(pin);
            }
        } else if (pin) {
            pin.remove();
        }
    });
}

function inspectNode(path) {
    selectedTreeNode = path;
    const nodeEl = document.querySelector(`.tree-node[data-path="${path}"]`);
    if (!nodeEl) return;

    const rules = JSON.parse(decodeURIComponent(nodeEl.dataset.rules));
    const type = nodeEl.dataset.type;
    const isIncluded = nodeEl.querySelector('.tree-checkbox').checked;
    
    // Update active tab to inspector
    const inspectorTabBtn = document.querySelector('.tab-btn[onclick*="inspector"]');
    if (inspectorTabBtn && !inspectorTabBtn.classList.contains('active')) {
        switchTab('inspector', inspectorTabBtn);
    }

    const container = document.getElementById('tab-inspector');
    
    let rulesHtml = '';
    
    // Manual Override status
    const isManIncluded = manualOverrides.included.has(path);
    const isManExcluded = manualOverrides.excluded.has(path);
    const manualStatus = isManIncluded ? 'Included ✅' : (isManExcluded ? 'Excluded ❌' : 'Not set');
    const manualMatched = isManIncluded || isManExcluded;

    rulesHtml += `
        <div class="inspection-item">
            <div class="inspection-header">
                <span class="inspection-name">Manual Override</span>
                <span class="inspection-status ${manualMatched ? 'matched' : ''}">${manualStatus}</span>
            </div>
            <div class="inspection-desc">Your explicit choice in the tree view.</div>
        </div>
    `;

    // Other rules
    rules.forEach(rule => {
        if (rule.name === "Manual Override") return;
        const matched = rule.status === 'matched' || rule.status === 'unsupported' || rule.status === 'supported';
        const statusText = rule.status.replace('_', ' ');
        
        rulesHtml += `
            <div class="inspection-item">
                <div class="inspection-header">
                    <span class="inspection-name">${rule.name}</span>
                    <span class="inspection-status ${matched ? 'matched' : ''}">${statusText}</span>
                </div>
            </div>
        `;
    });

    container.innerHTML = `
        <div class="inspector-panel">
            <div class="inspector-header">
                <div class="inspector-path">${path}</div>
                <div class="inspector-final-status ${isIncluded ? 'status-included' : 'status-excluded'}">
                    ${isIncluded ? 'INCLUDED ✅' : 'EXCLUDED ❌'}
                </div>
            </div>
            <div class="inspector-hierarchy">
                <div class="hierarchy-title">Rule Hierarchy (Top down)</div>
                ${rulesHtml}
            </div>
        </div>
    `;
}

function buildTreeHTML(nodes, isRoot) {
    let html = '';
    for (const node of nodes) {
        const isDir = node.type === 'dir';
        const icon = isDir ? '📂' : getFileIcon(node.ext);
        const hasChildren = isDir && node.children && node.children.length > 0;
        const isExcluded = node.excluded;
        const labelClass = isExcluded ? 'excluded' : '';
        const path = node.path;
        
        // Check for manual overrides
        const isManuallyIncluded = manualOverrides.included.has(path);
        const isManuallyExcluded = manualOverrides.excluded.has(path);
        const hasPin = isManuallyIncluded || isManuallyExcluded;

        let reasonHTML = '';
        if (node.reason === 'gitignore') {
            reasonHTML = '<span class="tree-reason reason-gitignore">.gitignore</span>';
        } else if (node.reason === 'repoliner_config') {
            reasonHTML = '<span class="tree-reason reason-config">config</span>';
        } else if (node.reason === 'extension_not_supported') {
            reasonHTML = '<span class="tree-reason reason-ext">ext</span>';
        }

        const rulesData = encodeURIComponent(JSON.stringify(node.rules));

        html += `<div class="tree-node" data-path="${path}" data-type="${node.type}" data-rules="${rulesData}">`;
        html += `<div class="tree-row" onclick="inspectNode('${path}')">`;
        html += `<span class="tree-toggle ${hasChildren ? 'open' : 'empty'}">▶</span>`;
        html += `<input type="checkbox" class="tree-checkbox" ${isExcluded && !isManuallyIncluded ? '' : 'checked'} data-path="${path}">`;
        html += `<span class="tree-icon">${icon}</span>`;
        html += `<span class="tree-label ${labelClass}">${node.name}</span>`;
        if (hasPin) {
            html += `<span class="tree-pin" title="Manual Override">📌</span>`;
        }
        html += reasonHTML;
        html += `</div>`;

        if (hasChildren) {
            html += `<div class="tree-children">`;
            html += buildTreeHTML(node.children, false);
            html += `</div>`;
        }

        html += `</div>`;
    }
    return html;
}

function getFileIcon(ext) {
    const icons = {
        '.py': '🐍', '.js': '⚡', '.ts': '🔷', '.tsx': '🔷',
        '.html': '🌐', '.htm': '🌐', '.css': '🎨',
        '.json': '📋', '.yaml': '⚙️', '.yml': '⚙️',
        '.md': '📝', '.txt': '📄',
        '.rs': '🦀', '.toml': '⚙️',
        '.sh': '🐚', '.bat': '🖥️',
    };
    return icons[ext] || '📄';
}

function updateParentCheckState(checkbox) {
    const node = checkbox.closest('.tree-node');
    const parentChildren = node.parentElement;
    if (!parentChildren || !parentChildren.classList.contains('tree-children')) return;

    const parentNode = parentChildren.closest('.tree-node');
    if (!parentNode) return;

    const parentCheckbox = parentNode.querySelector(':scope > .tree-row > .tree-checkbox');
    if (!parentCheckbox) return;

    const siblings = parentChildren.querySelectorAll(':scope > .tree-node > .tree-row > .tree-checkbox');
    const total = siblings.length;
    let checked = 0;
    let indeterminate = 0;

    siblings.forEach(s => {
        if (s.checked) checked++;
        if (s.indeterminate) indeterminate++;
    });

    if (checked === total && indeterminate === 0) {
        parentCheckbox.checked = true;
        parentCheckbox.indeterminate = false;
    } else if (checked === 0 && indeterminate === 0) {
        parentCheckbox.checked = false;
        parentCheckbox.indeterminate = false;
    } else {
        parentCheckbox.checked = false;
        parentCheckbox.indeterminate = true;
    }

    updateParentCheckState(parentCheckbox);
}

function treeCheckAll(state) {
    document.querySelectorAll('#treeBody .tree-checkbox').forEach(cb => {
        cb.checked = state;
        cb.indeterminate = false;
    });
}

// ═══════════════════════════════════════════════════════════
//  CONFIG MANAGEMENT
// ═══════════════════════════════════════════════════════════

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = (type === 'success' ? '✅ ' : '❌ ') + message;
    toast.classList.add('visible');
    setTimeout(() => {
        toast.classList.remove('visible');
    }, 3000);
}

async function saveActiveConfig(type) {
    let data = null;
    
    if (type === 'extensions') {
        // Get all checked extensions and their languages
        data = {};
        document.querySelectorAll('.ext-checkbox:checked').forEach(cb => {
            data[cb.dataset.value] = cb.dataset.lang || 'text';
        });
    } else if (type === 'ignore_dirs') {
        // Get all UNCHECKED directories (those the user wants to stay ignored)
        data = Array.from(document.querySelectorAll('.dir-checkbox:not(:checked)'))
            .map(cb => cb.dataset.value);
    } else if (type === 'ignore_files') {
        // Get all UNCHECKED files
        data = Array.from(document.querySelectorAll('.file-checkbox:not(:checked)'))
            .map(cb => cb.dataset.value);
    }

    if (!data) return;

    try {
        const res = await fetch('/api/config/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type, data }),
        });
        const result = await res.json();
        if (result.success) {
            showToast(`Updated global ${type} config`);
        } else {
            showToast('Failed to save config: ' + result.error, 'error');
        }
    } catch (e) {
        showToast('Save error: ' + e.message, 'error');
    }
}

async function removeConfigItem(type, value) {
    if (!confirm(`Remove "${value}" from global ${type} configuration?`)) return;

    let currentList = [];
    if (type === 'extensions') {
        currentList = scanData.lang_map;
        delete currentList[value];
    } else if (type === 'ignore_dirs') {
        currentList = scanData.excluded_dirs.filter(d => d !== value);
    } else if (type === 'ignore_files') {
        currentList = scanData.ignore_files.filter(f => f !== value);
    }

    try {
        const res = await fetch('/api/config/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type, data: currentList }),
        });
        const result = await res.json();
        if (result.success) {
            showToast(`Removed "${value}" from ${type}`);
            scanProject(); // Refresh UI
        }
    } catch (e) {
        showToast('Error removing item: ' + e.message, 'error');
    }
}

async function addNewExtension() {
    const ext = document.getElementById('newExtInput').value.trim();
    const lang = document.getElementById('newLangInput').value.trim() || 'text';

    if (!ext.startsWith('.')) {
        alert('Extension must start with a dot (e.g. .log)');
        return;
    }

    const currentMap = scanData ? { ...scanData.lang_map } : {};
    currentMap[ext] = lang;

    try {
        const res = await fetch('/api/config/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'extensions', data: currentMap }),
        });
        const result = await res.json();
        if (result.success) {
            showToast(`Added ${ext} (${lang}) to global config`);
            document.getElementById('newExtInput').value = '';
            document.getElementById('newLangInput').value = '';
            if (scanData) scanProject(); // Refresh if we have a path
        }
    } catch (e) {
        showToast('Error adding extension: ' + e.message, 'error');
    }
}

// ═══════════════════════════════════════════════════════════
//  RENDER: Config Tabs
// ═══════════════════════════════════════════════════════════

function renderExtensionsTab(data) {
    const container = document.getElementById('tab-extensions');
    let html = '';

    // Add Extension Form
    html += `
        <div class="add-ext-form">
            <input type="text" id="newExtInput" class="add-ext-input" placeholder=".ext" style="width: 60px;">
            <input type="text" id="newLangInput" class="add-ext-input" placeholder="lang (e.g. python)" style="flex:1;">
            <button class="btn btn-ghost" onclick="addNewExtension()">Add</button>
        </div>`;

    // Supported (included) extensions
    if (data.included_extensions.length) {
        html += `
            <div class="config-header">
                <span class="config-title">Supported Extensions</span>
                <button class="btn btn-ghost" onclick="saveActiveConfig('extensions')">Save as Default</button>
            </div>`;
        for (const ext of data.included_extensions) {
            const lang = data.lang_map[ext] || 'unknown';
            html += `
                <div class="list-item">
                    <input type="checkbox" checked data-value="${ext}" data-lang="${lang}" class="ext-checkbox">
                    <span class="list-item-label">${ext}</span>
                    <span class="list-item-lang">${lang}</span>
                    <button class="btn btn-ghost" style="padding:2px 6px;opacity:0.3;" onclick="removeConfigItem('extensions', '${ext}')">×</button>
                </div>`;
        }
    }

    // Unsupported (excluded) extensions
    if (data.excluded_extensions.length) {
        html += '<div class="config-header"><span class="config-title">Unsupported (found in project)</span></div>';
        for (const ext of data.excluded_extensions) {
            html += `
                <div class="list-item">
                    <input type="checkbox" data-value="${ext}" data-lang="text" class="ext-checkbox">
                    <span class="list-item-label" style="color:var(--text-muted)">${ext}</span>
                </div>`;
        }
    }

    container.innerHTML = html || '<div class="empty-state"><p>No extensions found.</p></div>';
}

function renderFoldersTab(data) {
    const container = document.getElementById('tab-folders');
    let html = '';

    if (data.included_dirs.length) {
        html += '<div class="config-header"><span class="config-title">Included Folders</span></div>';
        for (const dir of data.included_dirs) {
            html += `
                <div class="list-item">
                    <input type="checkbox" checked data-value="${dir}" class="dir-checkbox">
                    <span class="tree-icon">📂</span>
                    <span class="list-item-label">${dir}</span>
                </div>`;
        }
    }

    if (data.excluded_dirs.length) {
        html += `
            <div class="config-header">
                <span class="config-title">Excluded Folders</span>
                <button class="btn btn-ghost" onclick="saveActiveConfig('ignore_dirs')">Save as Default</button>
            </div>`;
        for (const dir of data.excluded_dirs) {
            html += `
                <div class="list-item">
                    <input type="checkbox" data-value="${dir}" class="dir-checkbox">
                    <span class="tree-icon">📂</span>
                    <span class="list-item-label" style="color:var(--text-muted)">${dir}</span>
                    <button class="btn btn-ghost" style="padding:2px 6px;opacity:0.3;" onclick="removeConfigItem('ignore_dirs', '${dir}')">×</button>
                </div>`;
        }
    }

    container.innerHTML = html || '<div class="empty-state"><p>No folders found.</p></div>';
}

function renderFilesTab(data) {
    const container = document.getElementById('tab-files');
    let html = '';

    html += `
        <div class="config-header">
            <span class="config-title">Excluded Files</span>
            <button class="btn btn-ghost" onclick="saveActiveConfig('ignore_files')">Save as Default</button>
        </div>`;
    for (const file of data.ignore_files) {
        html += `
            <div class="list-item">
                <input type="checkbox" data-value="${file}" class="file-checkbox">
                <span class="tree-icon">📄</span>
                <span class="list-item-label" style="color:var(--text-muted)">${file}</span>
                <button class="btn btn-ghost" style="padding:2px 6px;opacity:0.3;" onclick="removeConfigItem('ignore_files', '${file}')">×</button>
            </div>`;
    }

    container.innerHTML = html;
}

function renderGitignoreTab(data) {
    const container = document.getElementById('tab-gitignore');

    if (!data.gitignore_patterns.length) {
        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🚫</div><p>No .gitignore file found in project root.</p></div>';
        return;
    }

    let html = '<div style="padding:8px 12px;font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;font-weight:600;">Patterns from .gitignore (checked = honored)</div>';
    for (const pattern of data.gitignore_patterns) {
        html += `
            <div class="list-item">
                <input type="checkbox" checked data-value="${pattern}" class="gitignore-checkbox">
                <span class="list-item-label">${pattern}</span>
                <span class="tree-reason reason-gitignore">.gitignore</span>
            </div>`;
    }

    container.innerHTML = html;
}

// ═══════════════════════════════════════════════════════════
//  HELPERS
// ═══════════════════════════════════════════════════════════

function switchTab(tabName, btn) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + tabName).classList.add('active');
}

function selectMode(mode) {
    currentMode = mode;
    document.getElementById('modeFolder').classList.toggle('selected', mode === 'folder');
    document.getElementById('modeDump').classList.toggle('selected', mode === 'dump');
}

function getCheckedValues(className) {
    return Array.from(document.querySelectorAll('.' + className + ':checked'))
        .map(el => el.dataset.value);
}

function getUncheckedValues(className) {
    return Array.from(document.querySelectorAll('.' + className + ':not(:checked)'))
        .map(el => el.dataset.value);
}

function showResult(data) {
    const panel = document.getElementById('resultPanel');
    const icon = document.getElementById('resultIcon');
    const title = document.getElementById('resultTitle');
    const stats = document.getElementById('resultStats');
    const tokenBarDiv = document.getElementById('tokenBar');

    if (!data.success) {
        panel.className = 'result-panel visible';
        icon.textContent = '❌';
        title.textContent = 'Merge Failed';
        stats.innerHTML = `<p style="color:var(--danger)">${data.error}</p>`;
        tokenBarDiv.innerHTML = '';
        return;
    }

    panel.className = 'result-panel visible result-success';
    icon.textContent = '✅';
    title.textContent = 'Merge Complete';

    const tokens = data.total_tokens;
    let colorClass = 'green';
    let fitLabel = 'Fits all modern LLMs';
    if (tokens > 200000) {
        colorClass = 'red';
        fitLabel = 'Exceeds Claude 3.5 limit — use Gemini';
    } else if (tokens > 128000) {
        colorClass = 'yellow';
        fitLabel = 'Exceeds GPT-4 limit — use Claude or Gemini';
    }

    stats.innerHTML = `
        <div class="stat">
            <span class="stat-value">${data.files_merged}</span>
            <span class="stat-label">Files Merged</span>
        </div>
        <div class="stat">
            <span class="stat-value ${colorClass}">~${tokens.toLocaleString()}</span>
            <span class="stat-label">Est. Tokens</span>
        </div>
        <div class="stat">
            <span class="stat-value" style="font-size:0.85rem;">${data.output_path}</span>
            <span class="stat-label">Output Path</span>
        </div>
    `;

    const maxTokens = 1000000;
    const pct = Math.min((tokens / maxTokens) * 100, 100);
    const barColor = colorClass === 'green' ? 'var(--success)' :
                     colorClass === 'yellow' ? 'var(--warning)' : 'var(--danger)';

    tokenBarDiv.innerHTML = `
        <div class="token-bar-label">
            <span>${fitLabel}</span>
            <span>${tokens.toLocaleString()} / 1,000,000</span>
        </div>
        <div class="token-bar-track">
            <div class="token-bar-fill" style="width:${pct}%;background:${barColor}"></div>
        </div>
    `;

    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ── Enter key on path input triggers scan ──
document.getElementById('pathInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') scanProject();
});
