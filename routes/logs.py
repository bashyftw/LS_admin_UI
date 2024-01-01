from database import db, Log
from flask_login import login_required, current_user
from flask import Flask, render_template, redirect, url_for, request, flash
from app import app


def log_event(event):
    log = Log(event=event, username=current_user.username)
    db.session.add(log)
    db.session.commit()
    # Check the number of records
    count = Log.query.count()
    if count > 300:
        # If more than 300 records, delete the oldest one
        oldest_log = Log.query.order_by(Log.timestamp).first()
        db.session.delete(oldest_log)
        db.session.commit()


@app.route('/logs', methods=['GET'])
@login_required
def logs():
    page = request.args.get('page', 1, type=int)
    logs = Log.query.order_by(Log.timestamp.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/logs.html', logs=logs, page=page)


@app.route('/delete_log/<int:log_id>', methods=['POST'])
@login_required
def delete_log(log_id):
    if not current_user.is_admin:
        flash('You are not authorized to perform this action.', 'error')
        return redirect(url_for('logs'))
    log = Log.query.get(log_id)
    db.session.delete(log)
    db.session.commit()
    log_event("Log deleted - " +  log.event)
    flash(log.event +' deleted', 'success')
    return redirect(url_for('logs'))

@app.route('/clear_logs', methods=['GET'])
@login_required
def clear_logs():
    if not current_user.is_admin:
        flash('You are not authorized to perform this action.', 'error')
        return redirect(url_for('logs'))
    Log.query.delete()
    db.session.commit()
    log_event("Logs cleared")
    flash('Logs cleared', 'success')
    return redirect(url_for('logs'))
