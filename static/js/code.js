/* ===================================================================
   Linux Commands Learning Assistant — Code Studio JavaScript
   =================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const fileListEl = document.getElementById('file-list');
    const activeFileNameEl = document.getElementById('active-filename');
    const filePermBadgeEl = document.getElementById('file-perm-badge');
    const codeEditor = document.getElementById('code-editor');
    const editorGutter = document.getElementById('editor-gutter');
    const editorStatus = document.getElementById('editor-status');
    const editorLineCount = document.getElementById('editor-line-count');
    const btnNewFile = document.getElementById('btn-new-file');
    const btnSaveFile = document.getElementById('btn-save-file');
    const btnToggleChmod = document.getElementById('btn-toggle-chmod');
    const btnRunExecutable = document.getElementById('btn-run-executable');
    const btnRunBash = document.getElementById('btn-run-bash');
    const btnClearConsole = document.getElementById('btn-clear-console');
    const consoleOutput = document.getElementById('console-output');
    const consoleInput = document.getElementById('console-input');
    const templateSelect = document.getElementById('template-select');

    if (!codeEditor) return; // Not on code studio page

    // State
    let currentFilePath = '';
    let currentFilePerms = 'rw-r--r--';
    let isExecutable = false;
    let isDirty = false;

    const TEMPLATES = {
        bash: `#!/bin/bash
# Linux Shell Script Example
echo "========================================="
echo "   Linux Automated Shell Script"
echo "========================================="
echo "Active User   : $(whoami)"
echo "Current Path  : $(pwd)"
echo "Execution Date: $(date)"
echo ""
echo "Creating demo project workspace..."
mkdir -p demo_workspace
echo "Project files generated successfully!" > demo_workspace/readme.txt
cat demo_workspace/readme.txt
echo "Script finished with exit code 0."
`,
        python: `#!/usr/bin/env python3
# Linux Python Executable Script

def main():
    print("=========================================")
    print("   Python Script Executing in Linux")
    print("=========================================")
    modules = ["kernel", "bash", "systemd", "filesystem", "permissions"]
    for idx, mod in enumerate(modules, start=1):
        print(f"[{idx}] Linux Core Component: {mod}")
    print("\\nPython execution completed successfully!")

if __name__ == "__main__":
    main()
`,
        sysinfo: `#!/bin/bash
# System Diagnostics & Health Monitor
echo "=== KERNEL & SYSTEM INFORMATION ==="
uname -a
echo ""
echo "=== MEMORY CONSUMPTION ==="
free -m
echo ""
echo "=== FILESYSTEM STORAGE ALLOCATION ==="
df -h
echo ""
echo "=== PROCESS STATUS ==="
ps
`
    };

    // Initialize
    loadFiles();

    // Event Listeners
    codeEditor.addEventListener('input', () => {
        isDirty = true;
        editorStatus.textContent = 'Modified (Unsaved)';
        editorStatus.style.color = '#fbbf24';
        updateGutter();
    });

    // Handle Tab key in editor
    codeEditor.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = codeEditor.selectionStart;
            const end = codeEditor.selectionEnd;
            codeEditor.value = codeEditor.value.substring(0, start) + '    ' + codeEditor.value.substring(end);
            codeEditor.selectionStart = codeEditor.selectionEnd = start + 4;
            isDirty = true;
            editorStatus.textContent = 'Modified (Unsaved)';
            editorStatus.style.color = '#fbbf24';
            updateGutter();
        } else if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            saveCurrentFile();
        }
    });

    // Synchronize gutter scroll with textarea
    codeEditor.addEventListener('scroll', () => {
        editorGutter.scrollTop = codeEditor.scrollTop;
    });

    btnNewFile.addEventListener('click', () => {
        const fname = prompt('Enter new script filename (e.g. myscript.sh, app.py, task.sh):', 'myscript.sh');
        if (!fname) return;
        const cleanName = fname.trim();
        if (!cleanName) return;

        currentFilePath = cleanName.startsWith('/') ? cleanName : `/home/user/${cleanName}`;
        let initialContent = '#!/bin/bash\n\necho "Hello from ' + cleanName + '!"\n';
        if (cleanName.endsWith('.py')) {
            initialContent = TEMPLATES.python;
        } else if (cleanName.endsWith('.sh')) {
            initialContent = TEMPLATES.bash;
        }

        codeEditor.value = initialContent;
        currentFilePerms = 'rwxr-xr-x'; // default new script executable
        isExecutable = true;
        isDirty = false;
        activeFileNameEl.textContent = cleanName;
        updatePermBadge();
        updateGutter();

        // Save immediately to VFS
        saveCurrentFile(true);
    });

    btnSaveFile.addEventListener('click', () => saveCurrentFile());

    btnToggleChmod.addEventListener('click', async () => {
        if (!currentFilePath) return;
        const newExecutable = !isExecutable;
        try {
            const resp = await fetch('/api/code/file/chmod', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: currentFilePath, executable: newExecutable })
            });
            const data = await resp.json();
            if (data.success) {
                currentFilePerms = data.perms;
                isExecutable = data.is_executable;
                updatePermBadge();
                loadFiles(false);
                appendConsoleLog('system', `chmod ${newExecutable ? '+x' : '-x'} ${currentFilePath}: permissions updated to '${data.perms}'`);
            }
        } catch (err) {
            console.error('Failed to chmod file:', err);
        }
    });

    btnRunExecutable.addEventListener('click', () => executeFile('executable'));
    if (btnRunBash) {
        btnRunBash.addEventListener('click', () => executeFile('bash'));
    }

    if (templateSelect) {
        templateSelect.addEventListener('change', () => {
            const val = templateSelect.value;
            if (val && TEMPLATES[val]) {
                codeEditor.value = TEMPLATES[val];
                isDirty = true;
                editorStatus.textContent = 'Modified (Unsaved)';
                editorStatus.style.color = '#fbbf24';
                updateGutter();
            }
            templateSelect.value = '';
        });
    }

    btnClearConsole.addEventListener('click', () => {
        consoleOutput.innerHTML = '<div style="color: #64748b; font-style: italic;">Console cleared. Click "Run Executable" or execute Linux commands below.</div>';
    });

    // Interactive terminal line inside Code Studio console
    if (consoleInput) {
        consoleInput.addEventListener('keydown', async (e) => {
            if (e.key === 'Enter') {
                const cmd = consoleInput.value.trim();
                if (!cmd) return;
                consoleInput.value = '';

                appendConsoleCmd(cmd);

                try {
                    const resp = await fetch('/api/code/run', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ run_type: 'custom', custom_cmd: cmd })
                    });
                    const data = await resp.json();
                    if (data.output) {
                        appendConsoleOutput(data.output, data.status === 'error');
                    }
                    if (data.visual_changes && data.visual_changes.length > 0) {
                        appendConsoleLog('changes', data.visual_changes.join(', '));
                    }
                    // Refresh file list in case the command created/modified files
                    loadFiles(false);
                } catch (err) {
                    appendConsoleOutput('Error: ' + err, true);
                }
            }
        });
    }

    // -------------------------------------------------------------
    // Core Functions
    // -------------------------------------------------------------
    async function loadFiles(autoOpenFirst = true) {
        try {
            const resp = await fetch('/api/code/files');
            const data = await resp.json();
            if (!data.success) return;

            fileListEl.innerHTML = '';
            if (data.files.length === 0) {
                fileListEl.innerHTML = '<div style="color: #64748b; font-size: 0.8rem; padding: 0.5rem;">No files found. Click "+ New File" to create one.</div>';
                return;
            }

            data.files.forEach(f => {
                const item = document.createElement('div');
                item.className = 'file-item' + (f.path === currentFilePath ? ' active' : '');
                
                let icon = 'fas fa-file-code';
                if (f.name.endsWith('.py')) icon = 'fab fa-python';
                else if (f.name.endsWith('.sh')) icon = 'fas fa-terminal';
                else if (f.name.endsWith('.txt') || f.name.endsWith('.log')) icon = 'fas fa-file-alt';

                item.innerHTML = `
                    <div class="file-item-left" title="${f.path}">
                        <i class="${icon}" style="color: ${f.is_executable ? '#34d399' : '#94a3b8'};"></i>
                        <span>${escapeHtml(f.name)}</span>
                    </div>
                    <div class="file-item-right">
                        ${f.is_executable ? '<span class="badge-x" title="Executable mode enabled">+x</span>' : ''}
                        <button class="btn-icon-del" data-path="${escapeHtml(f.path)}" title="Delete file">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                `;

                item.addEventListener('click', (e) => {
                    if (e.target.closest('.btn-icon-del')) return;
                    openFile(f.path);
                });

                const delBtn = item.querySelector('.btn-icon-del');
                if (delBtn) {
                    delBtn.addEventListener('click', async (e) => {
                        e.stopPropagation();
                        if (confirm(`Delete '${f.name}' from your virtual filesystem?`)) {
                            await deleteFile(f.path);
                        }
                    });
                }

                fileListEl.appendChild(item);
            });

            if (autoOpenFirst && !currentFilePath && data.files.length > 0) {
                // Open first file, prioritizing scripts/backup.sh or any .sh file
                const scriptFile = data.files.find(f => f.name.endsWith('.sh')) || data.files[0];
                openFile(scriptFile.path);
            }
        } catch (err) {
            console.error('Failed to load files:', err);
        }
    }

    async function openFile(path) {
        try {
            const resp = await fetch('/api/code/file/get', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path })
            });
            const data = await resp.json();
            if (!data.success) return;

            currentFilePath = data.path;
            currentFilePerms = data.perms;
            isExecutable = data.is_executable;
            isDirty = false;

            activeFileNameEl.textContent = data.name;
            codeEditor.value = data.content;
            editorStatus.textContent = 'Saved';
            editorStatus.style.color = '#10b981';

            updatePermBadge();
            updateGutter();

            // Update active file styling in sidebar
            document.querySelectorAll('.file-item').forEach(el => {
                const titleEl = el.querySelector('.file-item-left');
                if (titleEl && titleEl.getAttribute('title') === path) {
                    el.classList.add('active');
                } else {
                    el.classList.remove('active');
                }
            });
        } catch (err) {
            console.error('Failed to open file:', err);
        }
    }

    async function saveCurrentFile(makeExecutable = null) {
        if (!currentFilePath) {
            const fname = prompt('Enter filename to save:', 'myscript.sh');
            if (!fname) return;
            currentFilePath = `/home/user/${fname.trim()}`;
        }

        try {
            const body = {
                path: currentFilePath,
                content: codeEditor.value
            };
            if (makeExecutable !== null) {
                body.make_executable = makeExecutable;
            }

            const resp = await fetch('/api/code/file/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await resp.json();
            if (data.success) {
                isDirty = false;
                currentFilePerms = data.perms;
                isExecutable = data.is_executable;
                editorStatus.textContent = 'Saved';
                editorStatus.style.color = '#10b981';
                updatePermBadge();
                loadFiles(false);
                appendConsoleLog('system', `File '${data.name}' saved to ${data.path} (${data.perms})`);
            }
        } catch (err) {
            console.error('Failed to save file:', err);
        }
    }

    async function deleteFile(path) {
        try {
            const resp = await fetch('/api/code/file/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path })
            });
            const data = await resp.json();
            if (data.success) {
                appendConsoleLog('system', `Removed file '${path}'`);
                if (currentFilePath === path) {
                    currentFilePath = '';
                    codeEditor.value = '';
                    activeFileNameEl.textContent = 'No file open';
                    updatePermBadge();
                    updateGutter();
                }
                loadFiles(true);
            }
        } catch (err) {
            console.error('Failed to delete file:', err);
        }
    }

    async function executeFile(runType) {
        if (!currentFilePath) {
            alert('Please select or create a script file to run.');
            return;
        }

        // Auto-save if dirty
        if (isDirty) {
            await saveCurrentFile();
        }

        const relativeName = currentFilePath.replace('/home/user/', '');
        const targetCommand = runType === 'bash' ? `bash ${relativeName}` : `./${relativeName}`;

        appendConsoleCmd(targetCommand);

        try {
            const resp = await fetch('/api/code/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: relativeName, run_type: runType })
            });
            const data = await resp.json();

            if (data.status === 'error') {
                appendConsoleOutput(data.output, true);
                if (data.output.includes('Permission denied')) {
                    appendPermissionDeniedTip(currentFilePath, relativeName);
                }
            } else {
                appendConsoleOutput(data.output || '(Execution finished with exit code 0)');
                if (data.visual_changes && data.visual_changes.length > 0) {
                    appendConsoleLog('changes', 'Filesystem Mutations: ' + data.visual_changes.join(', '));
                }
                // Refresh file explorer in case the script created new files
                loadFiles(false);
            }
        } catch (err) {
            appendConsoleOutput('Sandbox Execution Error: ' + err, true);
        }
    }

    function updatePermBadge() {
        if (!filePermBadgeEl) return;
        if (!currentFilePath) {
            filePermBadgeEl.innerHTML = '<span class="badge" style="background: rgba(255,255,255,0.06); color: #94a3b8;">No File</span>';
            return;
        }

        if (isExecutable) {
            filePermBadgeEl.innerHTML = `
                <span class="badge badge-completed" style="font-size: 0.8rem; padding: 0.3rem 0.65rem;">
                    <i class="fas fa-check"></i> ${currentFilePerms} [Executable]
                </span>
            `;
            btnToggleChmod.innerHTML = '<i class="fas fa-lock"></i> Remove Executable (-x)';
            btnToggleChmod.className = 'btn btn-outline';
        } else {
            filePermBadgeEl.innerHTML = `
                <span class="badge" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); font-size: 0.8rem; padding: 0.3rem 0.65rem;">
                    <i class="fas fa-exclamation-triangle"></i> ${currentFilePerms} [Not Executable]
                </span>
            `;
            btnToggleChmod.innerHTML = '<i class="fas fa-bolt" style="color: #fbbf24;"></i> Make Executable (chmod +x)';
            btnToggleChmod.className = 'btn btn-outline';
        }
    }

    function updateGutter() {
        const lines = codeEditor.value.split('\n');
        const count = lines.length;
        let gutterText = '';
        for (let i = 1; i <= count; i++) {
            gutterText += i + '\n';
        }
        editorGutter.textContent = gutterText;
        editorLineCount.textContent = `${count} lines, ${codeEditor.value.length} chars`;
    }

    function appendConsoleCmd(cmd) {
        const div = document.createElement('div');
        div.className = 'console-cmd-line';
        div.innerHTML = `<span style="color: #10b981;">user@linux-assistant</span>:<span style="color: #38bdf8;">~</span>$ ${escapeHtml(cmd)}`;
        consoleOutput.appendChild(div);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }

    function appendConsoleOutput(text, isError = false) {
        const div = document.createElement('div');
        div.className = isError ? 'console-stderr' : 'console-stdout';
        div.textContent = text;
        consoleOutput.appendChild(div);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }

    function appendConsoleLog(type, msg) {
        const div = document.createElement('div');
        div.style.fontSize = '0.8rem';
        div.style.fontStyle = 'italic';
        div.style.color = type === 'changes' ? '#34d399' : '#94a3b8';
        div.textContent = `[${type}] ${msg}`;
        consoleOutput.appendChild(div);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }

    function appendPermissionDeniedTip(fullPath, relativeName) {
        const tip = document.createElement('div');
        tip.className = 'console-tip';
        tip.innerHTML = `
            <div><i class="fas fa-lightbulb" style="font-size: 1.1rem; color: #fbbf24;"></i></div>
            <div style="flex: 1;">
                <strong>Why did this happen?</strong>
                <p style="margin: 0.25rem 0 0.5rem 0; line-height: 1.4;">
                    In Linux, files cannot be executed directly via <code>./${escapeHtml(relativeName)}</code> unless the execute bit (<code>x</code>) is set.
                </p>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <button class="btn btn-primary" id="btn-fix-chmod" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;">
                        <i class="fas fa-bolt"></i> Grant chmod +x & Re-Run
                    </button>
                    <span style="font-size: 0.78rem; color: #94a3b8;">or run <code>bash ${escapeHtml(relativeName)}</code></span>
                </div>
            </div>
        `;
        consoleOutput.appendChild(tip);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;

        const fixBtn = tip.querySelector('#btn-fix-chmod');
        if (fixBtn) {
            fixBtn.addEventListener('click', async () => {
                await fetch('/api/code/file/chmod', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: fullPath, executable: true })
                });
                isExecutable = true;
                currentFilePerms = 'rwxr-xr-x';
                updatePermBadge();
                loadFiles(false);
                appendConsoleLog('system', `Granted executable permissions (+x) to ${relativeName}`);
                executeFile('executable');
            });
        }
    }

    function escapeHtml(str) {
        return (str || '').replace(/[&<>'"]/g, tag => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
        }[tag] || tag));
    }
});
