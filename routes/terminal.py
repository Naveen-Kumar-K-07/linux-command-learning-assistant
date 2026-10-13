from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, TerminalState, Lesson
from services.simulator import VirtualLinuxSimulator
from services.progress_service import ProgressService

terminal_bp = Blueprint('terminal', __name__)

@terminal_bp.route('/api/terminal/state', methods=['GET'])
@login_required
def get_state():
    """Returns current user's simulated terminal state and virtual filesystem."""
    state = TerminalState.query.filter_by(user_id=current_user.id).first()
    if not state:
        default_vfs = VirtualLinuxSimulator.get_default_vfs()
        state = TerminalState(
            user_id=current_user.id,
            cwd='/home/user',
            filesystem_json=''
        )
        state.set_filesystem(default_vfs)
        db.session.add(state)
        db.session.commit()

    return jsonify({
        'success': True,
        'cwd': state.cwd,
        'vfs': state.get_filesystem(),
        'history': state.get_history()
    })

@terminal_bp.route('/api/terminal/execute', methods=['POST'])
@login_required
def execute_command():
    """
    Executes a simulated Linux command against the user's persistent VFS,
    updates MySQL state, evaluates practice tasks, and returns output + visual changes.
    """
    data = request.get_json() or {}
    raw_command = data.get('command', '').strip()
    lesson_id = data.get('lesson_id')

    if not raw_command:
        return jsonify({'success': False, 'error': 'No command provided'}), 400

    # Load user's persisted terminal state
    state = TerminalState.query.filter_by(user_id=current_user.id).first()
    if not state:
        default_vfs = VirtualLinuxSimulator.get_default_vfs()
        state = TerminalState(user_id=current_user.id, cwd='/home/user')
        state.set_filesystem(default_vfs)
        db.session.add(state)

    vfs = state.get_filesystem() or VirtualLinuxSimulator.get_default_vfs()
    sim = VirtualLinuxSimulator(vfs=vfs, cwd=state.cwd, user=current_user.full_name.split()[0].lower())

    # Execute inside isolated virtual sandbox
    result = sim.execute(raw_command)

    # Persist updated VFS and cwd to database
    state.cwd = sim.cwd
    state.set_filesystem(sim.vfs)
    
    history = state.get_history()
    history.append(raw_command)
    state.set_history(history)
    db.session.commit()

    # Check practice task completion if lesson_id provided
    practice_matched = False
    if lesson_id and result.get('status') != 'error':
        lesson = db.session.get(Lesson, lesson_id)
        if lesson and lesson.practice_expected_command:
            expected = lesson.practice_expected_command.strip().lower()
            actual = raw_command.strip().lower()
            # Normalize multiple spaces and quotes
            clean_expected = " ".join(expected.replace('"', '').replace("'", "").split())
            clean_actual = " ".join(actual.replace('"', '').replace("'", "").split())
            
            matched = False
            if clean_actual == clean_expected or clean_expected in clean_actual:
                matched = True
            elif clean_expected.split() and clean_actual.split():
                exp_parts = clean_expected.split()
                act_parts = clean_actual.split()
                if exp_parts[0] == act_parts[0] and all(p in act_parts for p in exp_parts[1:]):
                    matched = True

            if matched:
                practice_matched = True
                ProgressService.record_progress(current_user.id, lesson.id, practice_completed=True, is_completed=True)

    return jsonify({
        'success': True,
        'command': raw_command,
        'output': result.get('output', ''),
        'status': result.get('status', 'success'),
        'cwd': sim.cwd,
        'vfs': sim.vfs,
        'visual_changes': result.get('visual_changes', []),
        'explanation': result.get('explanation', ''),
        'practice_matched': practice_matched
    })

@terminal_bp.route('/api/terminal/reset', methods=['POST'])
@login_required
def reset_state():
    """Resets the user's virtual filesystem back to clean default."""
    state = TerminalState.query.filter_by(user_id=current_user.id).first()
    if state:
        state.cwd = '/home/user'
        state.set_filesystem(VirtualLinuxSimulator.get_default_vfs())
        state.set_history([])
        db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Simulated terminal filesystem restored to clean state.',
        'cwd': '/home/user',
        'vfs': VirtualLinuxSimulator.get_default_vfs()
    })
