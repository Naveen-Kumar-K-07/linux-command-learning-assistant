from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, TerminalState
from services.simulator import VirtualLinuxSimulator

code_bp = Blueprint('code', __name__)

def _get_user_state():
    state = TerminalState.query.filter_by(user_id=current_user.id).first()
    if not state:
        default_vfs = VirtualLinuxSimulator.get_default_vfs()
        state = TerminalState(user_id=current_user.id, cwd='/home/user')
        state.set_filesystem(default_vfs)
        db.session.add(state)
        db.session.commit()
    return state

@code_bp.route('/code')
@login_required
def index():
    """Renders the interactive Linux Code Studio and Executable Runner."""
    return render_template('code/index.html')

@code_bp.route('/api/code/files', methods=['GET'])
@login_required
def list_files():
    """Lists files within the user's home workspace (/home/user)."""
    state = _get_user_state()
    vfs = state.get_filesystem() or VirtualLinuxSimulator.get_default_vfs()
    sim = VirtualLinuxSimulator(vfs=vfs, cwd=state.cwd, user=current_user.full_name.split()[0].lower())

    files = []
    def crawl(node, curr_path):
        if not node:
            return
        if node.get('type') == 'file':
            perms = node.get('perms', 'rw-r--r--')
            files.append({
                'name': node.get('name', ''),
                'path': curr_path,
                'size': node.get('size', 0),
                'perms': perms,
                'is_executable': 'x' in perms
            })
        elif node.get('type') == 'dir':
            for name, child in sorted(node.get('children', {}).items()):
                crawl(child, f"{curr_path}/{name}" if curr_path != '/' else f"/{name}")

    start_node = sim.get_node('/home/user') or vfs
    crawl(start_node, '/home/user')

    return jsonify({
        'success': True,
        'cwd': state.cwd,
        'files': files
    })

@code_bp.route('/api/code/file/get', methods=['POST'])
@login_required
def get_file():
    """Fetches the content, permissions, and metadata of a file."""
    data = request.get_json() or {}
    path = data.get('path', '').strip()
    if not path:
        return jsonify({'success': False, 'error': 'Missing path operand'}), 400

    state = _get_user_state()
    vfs = state.get_filesystem() or VirtualLinuxSimulator.get_default_vfs()
    sim = VirtualLinuxSimulator(vfs=vfs, cwd=state.cwd, user=current_user.full_name.split()[0].lower())

    abs_path = sim.normalize_path(path)
    node = sim.get_node(abs_path)

    if not node or node.get('type') != 'file':
        return jsonify({'success': False, 'error': f"File '{path}' not found."}), 404

    perms = node.get('perms', 'rw-r--r--')
    return jsonify({
        'success': True,
        'name': node.get('name', ''),
        'path': abs_path,
        'content': node.get('content', ''),
        'size': node.get('size', 0),
        'perms': perms,
        'is_executable': 'x' in perms
    })

@code_bp.route('/api/code/file/save', methods=['POST'])
@login_required
def save_file():
    """Creates or updates a file in the user's virtual filesystem."""
    data = request.get_json() or {}
    path = data.get('path', '').strip()
    content = data.get('content', '')
    make_executable = data.get('make_executable', False)

    if not path:
        return jsonify({'success': False, 'error': 'Filename is required'}), 400

    state = _get_user_state()
    vfs = state.get_filesystem() or VirtualLinuxSimulator.get_default_vfs()
    sim = VirtualLinuxSimulator(vfs=vfs, cwd=state.cwd, user=current_user.full_name.split()[0].lower())

    # If relative path, default to /home/user or cwd
    if not path.startswith('/'):
        abs_path = sim.normalize_path(f"/home/user/{path}" if not path.startswith('scripts/') else f"/home/user/{path}")
    else:
        abs_path = sim.normalize_path(path)

    parent, name = sim.get_parent_and_name(abs_path)
    if not parent:
        # Create parent directory recursively if missing
        parts = [p for p in abs_path.split('/') if p][:-1]
        curr = sim.vfs
        for p in parts:
            children = curr.setdefault('children', {})
            if p not in children:
                children[p] = {'type': 'dir', 'name': p, 'owner': sim.user, 'group': sim.user, 'perms': 'rwxr-xr-x', 'children': {}}
            curr = children[p]
        parent = curr

    children = parent.setdefault('children', {})
    existing = children.get(name)

    perms = existing.get('perms') if existing else ('rwxr-xr-x' if make_executable else 'rw-r--r--')
    if make_executable:
        perms = 'rwxr-xr-x'

    children[name] = {
        'type': 'file',
        'name': name,
        'owner': sim.user,
        'group': sim.user,
        'perms': perms,
        'size': len(content.encode('utf-8')),
        'content': content
    }

    state.set_filesystem(sim.vfs)
    db.session.commit()

    return jsonify({
        'success': True,
        'name': name,
        'path': abs_path,
        'perms': perms,
        'is_executable': 'x' in perms,
        'size': len(content.encode('utf-8'))
    })

@code_bp.route('/api/code/file/chmod', methods=['POST'])
@login_required
def chmod_file():
    """Toggles or sets executable permission on a file."""
    data = request.get_json() or {}
    path = data.get('path', '').strip()
    executable = data.get('executable', True)

    if not path:
        return jsonify({'success': False, 'error': 'Path is required'}), 400

    state = _get_user_state()
    vfs = state.get_filesystem() or VirtualLinuxSimulator.get_default_vfs()
    sim = VirtualLinuxSimulator(vfs=vfs, cwd=state.cwd, user=current_user.full_name.split()[0].lower())

    abs_path = sim.normalize_path(path)
    node = sim.get_node(abs_path)
    if not node or node.get('type') != 'file':
        return jsonify({'success': False, 'error': 'File not found'}), 404

    node['perms'] = 'rwxr-xr-x' if executable else 'rw-r--r--'
    state.set_filesystem(sim.vfs)
    db.session.commit()

    return jsonify({
        'success': True,
        'path': abs_path,
        'perms': node['perms'],
        'is_executable': 'x' in node['perms']
    })

@code_bp.route('/api/code/file/delete', methods=['POST'])
@login_required
def delete_file():
    """Removes a file from the virtual filesystem."""
    data = request.get_json() or {}
    path = data.get('path', '').strip()
    if not path:
        return jsonify({'success': False, 'error': 'Path required'}), 400

    state = _get_user_state()
    vfs = state.get_filesystem() or VirtualLinuxSimulator.get_default_vfs()
    sim = VirtualLinuxSimulator(vfs=vfs, cwd=state.cwd, user=current_user.full_name.split()[0].lower())

    abs_path = sim.normalize_path(path)
    parent, name = sim.get_parent_and_name(abs_path)
    if parent and 'children' in parent and name in parent['children']:
        del parent['children'][name]
        state.set_filesystem(sim.vfs)
        db.session.commit()
        return jsonify({'success': True, 'path': abs_path})

    return jsonify({'success': False, 'error': 'File not found'}), 404

@code_bp.route('/api/code/run', methods=['POST'])
@login_required
def run_executable():
    """
    Executes a script/executable or custom Linux command in the isolated virtual sandbox.
    """
    data = request.get_json() or {}
    path = data.get('path', '').strip()
    run_type = data.get('run_type', 'executable') # 'executable', 'bash', 'python', 'custom'
    custom_cmd = data.get('custom_cmd', '').strip()

    state = _get_user_state()
    vfs = state.get_filesystem() or VirtualLinuxSimulator.get_default_vfs()
    sim = VirtualLinuxSimulator(vfs=vfs, cwd=state.cwd, user=current_user.full_name.split()[0].lower())

    # Determine command to run
    if run_type == 'custom' and custom_cmd:
        cmd_to_run = custom_cmd
    elif run_type == 'bash':
        cmd_to_run = f"bash {path}"
    elif run_type == 'python':
        cmd_to_run = f"python {path}"
    else:
        # Default: direct executable invocation (./path or /path)
        if not path.startswith('/') and not path.startswith('./'):
            cmd_to_run = f"./{path}"
        else:
            cmd_to_run = path

    result = sim.execute(cmd_to_run)

    # Persist updated VFS and history
    state.cwd = sim.cwd
    state.set_filesystem(sim.vfs)
    history = state.get_history()
    history.append(cmd_to_run)
    state.set_history(history)
    db.session.commit()

    return jsonify({
        'success': True,
        'command': cmd_to_run,
        'output': result.get('output', ''),
        'status': result.get('status', 'success'),
        'cwd': sim.cwd,
        'visual_changes': result.get('visual_changes', []),
        'explanation': result.get('explanation', ''),
        'vfs': sim.vfs
    })
