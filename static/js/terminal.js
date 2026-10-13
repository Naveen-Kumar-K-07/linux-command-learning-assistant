/* ===================================================================
   Linux Simulator & Terminal Engine (client-side synchronization)
   =================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const terminalBody = document.getElementById('terminal-body');
    const terminalHistory = document.getElementById('terminal-history');
    const termInput = document.getElementById('term-input');
    const btnExecute = document.getElementById('btn-execute');
    const btnClear = document.getElementById('btn-clear-term');
    const btnReset = document.getElementById('btn-reset-term');
    const currentPathBadge = document.getElementById('term-current-path');
    const promptPathSpan = document.getElementById('prompt-path');
    const vfsTreeContainer = document.getElementById('vfs-tree-container');
    const visualChangesContainer = document.getElementById('visual-changes-container');
    const explanationContainer = document.getElementById('explanation-container');
    const practiceStatusBadge = document.getElementById('practice-status-badge');

    if (!termInput) return; // Not on lesson/terminal page

    const lessonId = termInput.dataset.lessonId;
    let commandHistory = [];
    let historyIndex = -1;

    // Load initial VFS & terminal state
    fetchInitialState();

    // Event Listeners
    if (btnExecute) {
        btnExecute.addEventListener('click', handleCommandSubmit);
    }

    termInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleCommandSubmit();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (commandHistory.length > 0) {
                if (historyIndex === -1) historyIndex = commandHistory.length - 1;
                else if (historyIndex > 0) historyIndex--;
                termInput.value = commandHistory[historyIndex] || '';
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (historyIndex !== -1) {
                if (historyIndex < commandHistory.length - 1) {
                    historyIndex++;
                    termInput.value = commandHistory[historyIndex] || '';
                } else {
                    historyIndex = -1;
                    termInput.value = '';
                }
            }
        }
    });

    if (btnClear) {
        btnClear.addEventListener('click', () => {
            if (terminalHistory) terminalHistory.innerHTML = '';
        });
    }

    if (btnReset) {
        btnReset.addEventListener('click', async () => {
            if (confirm('Reset your simulated virtual filesystem back to the initial default state?')) {
                const res = await fetch('/api/terminal/reset', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
                const data = await res.json();
                if (data.success) {
                    updatePromptPath(data.cwd);
                    renderVFSTree(data.vfs);
                    appendTerminalEntry('system', 'Simulated virtual filesystem reset to clean state.');
                }
            }
        });
    }

    // Inspector Tab Switching
    document.querySelectorAll('.inspector-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.inspector-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const target = tab.dataset.target;
            document.querySelectorAll('.inspector-pane').forEach(p => p.style.display = 'none');
            const targetEl = document.getElementById(target);
            if (targetEl) targetEl.style.display = 'block';
        });
    });

    // Copy command buttons in lesson examples
    document.querySelectorAll('.btn-copy-cmd').forEach(btn => {
        btn.addEventListener('click', () => {
            const cmd = btn.dataset.cmd;
            if (cmd && termInput) {
                termInput.value = cmd;
                termInput.focus();
            }
        });
    });

    async function handleCommandSubmit() {
        const rawCmd = termInput.value.trim();
        if (!rawCmd) return;

        commandHistory.push(rawCmd);
        historyIndex = -1;
        termInput.value = '';

        const currentCwd = promptPathSpan ? promptPathSpan.textContent : '~';

        // Render command line in terminal log
        appendTerminalEntry('command', rawCmd, currentCwd);

        try {
            const resp = await fetch('/api/terminal/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: rawCmd, lesson_id: lessonId })
            });
            const data = await resp.json();

            if (data.output === '__CLEAR__') {
                if (terminalHistory) terminalHistory.innerHTML = '';
            } else if (data.output) {
                appendTerminalEntry('output', data.output, null, data.status === 'error');
            }

            // Update CWD & Prompt
            if (data.cwd) {
                updatePromptPath(data.cwd);
            }

            // Update VFS Tree
            if (data.vfs) {
                renderVFSTree(data.vfs);
            }

            // Update Visual Changes & Explanations
            updateInspectorVisuals(data.visual_changes, data.explanation);

            // Check practice task & auto-complete lesson
            if (data.practice_matched) {
                if (practiceStatusBadge) {
                    practiceStatusBadge.innerHTML = '<span class="badge badge-completed"><i class="fas fa-check-circle"></i> Challenge Completed!</span>';
                    practiceStatusBadge.classList.add('animate-bounce');
                }
                const lessonStatusBadge = document.getElementById('lesson-status-badge');
                if (lessonStatusBadge) {
                    lessonStatusBadge.innerHTML = '<span class="badge badge-completed" style="font-size: 0.85rem; padding: 0.45rem 0.95rem; display: inline-flex; align-items: center; gap: 0.45rem;"><i class="fas fa-check-circle"></i> Lesson Completed</span>';
                    lessonStatusBadge.classList.add('animate-bounce');
                }
                appendTerminalEntry('system', '🎉 Practice challenge completed! Lesson automatically marked as completed.');
            }

        } catch (err) {
            appendTerminalEntry('output', 'Error executing command in virtual sandbox: ' + err, null, true);
        }

        // Scroll to bottom
        terminalBody.scrollTop = terminalBody.scrollHeight;
    }

    function appendTerminalEntry(type, content, cwd = '~', isError = false) {
        if (!terminalHistory) return;

        const entry = document.createElement('div');
        entry.className = 'term-entry';

        if (type === 'command') {
            entry.innerHTML = `
                <div class="term-prompt-line">
                    <span class="prompt-user">user</span><span class="prompt-at">@</span><span class="prompt-host">linux-assistant</span><span class="prompt-colon">:</span><span class="prompt-path">${formatPathDisplay(cwd)}</span><span class="prompt-symbol">$</span>
                    <span>${escapeHtml(content)}</span>
                </div>
            `;
        } else if (type === 'output') {
            const outDiv = document.createElement('div');
            outDiv.className = 'term-output' + (isError ? ' term-output-error' : '');
            outDiv.textContent = content;
            entry.appendChild(outDiv);
        } else if (type === 'system') {
            entry.innerHTML = `<div class="term-output" style="color: #10b981;">[system] ${escapeHtml(content)}</div>`;
        }

        terminalHistory.appendChild(entry);
    }

    function updatePromptPath(absPath) {
        const display = formatPathDisplay(absPath);
        if (promptPathSpan) promptPathSpan.textContent = display;
        if (currentPathBadge) currentPathBadge.textContent = absPath;
    }

    function formatPathDisplay(absPath) {
        if (!absPath || absPath === '/home/user') return '~';
        if (absPath.startsWith('/home/user/')) return '~/' + absPath.replace('/home/user/', '');
        return absPath;
    }

    async function fetchInitialState() {
        try {
            const resp = await fetch('/api/terminal/state');
            const data = await resp.json();
            if (data.success) {
                updatePromptPath(data.cwd);
                renderVFSTree(data.vfs);
            }
        } catch (e) {
            console.error('Failed to load initial VFS state:', e);
        }
    }

    function renderVFSTree(vfs) {
        if (!vfsTreeContainer || !vfs) return;
        vfsTreeContainer.innerHTML = '';

        function renderNode(node, container, depth = 0) {
            const isDir = node.type === 'dir';
            const name = node.name || '/';
            const indent = depth * 14;

            const item = document.createElement('div');
            item.className = 'vfs-tree-item';
            item.style.paddingLeft = `${indent}px`;

            const icon = isDir ? '<i class="fas fa-folder' + (depth > 0 ? '' : '-open') + ' vfs-folder"></i>' : '<i class="fas fa-file-code vfs-file"></i>';
            const perms = node.perms || (isDir ? 'rwxr-xr-x' : 'rw-r--r--');

            item.innerHTML = `
                ${icon}
                <span class="${isDir ? 'vfs-folder' : 'vfs-file'}">${escapeHtml(name)}</span>
                <span class="vfs-meta">${escapeHtml(perms)}</span>
            `;
            container.appendChild(item);

            if (isDir && node.children) {
                const keys = Object.keys(node.children).sort();
                for (const key of keys) {
                    renderNode(node.children[key], container, depth + 1);
                }
            }
        }

        renderNode(vfs, vfsTreeContainer);
    }

    function updateInspectorVisuals(changes, explanation) {
        if (visualChangesContainer) {
            if (changes && changes.length > 0) {
                visualChangesContainer.innerHTML = changes.map(c => `
                    <div class="visual-change-pill">
                        <i class="fas fa-magic"></i> ${escapeHtml(c)}
                    </div>
                `).join('');
            } else {
                visualChangesContainer.innerHTML = '<span style="color: #64748b;">No filesystem state mutations in last command.</span>';
            }
        }

        if (explanationContainer) {
            if (explanation) {
                explanationContainer.innerHTML = `
                    <div class="explanation-box">
                        <strong style="color: #38bdf8;"><i class="fas fa-info-circle"></i> Command Behavior:</strong>
                        <p style="margin-top: 4px;">${escapeHtml(explanation)}</p>
                    </div>
                `;
            }
        }
    }

    function escapeHtml(str) {
        return (str || '').replace(/[&<>'"]/g, tag => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
        }[tag] || tag));
    }
});
