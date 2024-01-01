from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from flask_login.mixins import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User
from app import app
from sqlalchemy.exc import IntegrityError
import random
from routes.logs import log_event

avatar_names = ["Ironthorn, the Immortal Juggernaut",
                "Bloodtalon, the Crimson Assassin",
                "Shadowshroud, the Dark Veil",
                "Vilemaw, the Abyssal Fiend",
                "Sorrowcrown, the Woebringe",
                "Gravelurk, the Stone Predator",
                "Soulthirst, the Eternity Devourer",
                "Umbraflame, the Gloom Phoenix",
                "Voidfang, the Soul Eater",
                "Azraelskull, the Harbinger of Shadows",
                "Voidstorm, the Abyssal Maelstrom",
                "Dreadhowl, the Fearmonger",
                "Dreadheart, the Corpse Collector",
                "Ironscorn, the Unyielding Titan",
                "Dreadmane, the Terrifying Nightmare",
                "Pyreclaw, the Flame Warden"
                ]

class NewUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    is_admin = BooleanField('Admin', default=False)
    is_enabled = BooleanField('Enabled', default=True)
    submit = SubmitField('Create user')

class EditUserForm(FlaskForm):
    avatar = SelectField('Avatar', choices=[(i, name) for i, name in enumerate(avatar_names)])
    username = StringField('Username', validators=[DataRequired()])
    is_admin = BooleanField('Admin', default=False)
    is_enabled = BooleanField('Enabled', default=True)
    submitEdit = SubmitField('Update')


class EditPassForm(FlaskForm):
    oldPassword = PasswordField('Old Password', validators=[DataRequired()])
    newPassword = PasswordField('New Password', validators=[DataRequired()])
    submitPass = SubmitField('Update')


@app.route('/users', methods=['GET'])
@login_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('users/users.html', users=users, page=page)


@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('You are not authorized to perform this action.', 'error')
        return redirect(url_for('users'))
    form = NewUserForm()
    if form.validate_on_submit():
        user = User()
        user.avatar = random.randint(0, 15)
        user.username = form.username.data
        user.password = generate_password_hash(form.password.data, method='sha256')
        user.is_admin = form.is_admin.data
        user.is_enabled = form.is_enabled.data
        db.session.add(user)
        try:
            db.session.commit()
            log_event('User added: ' + user.username)
            flash('User added: ' + user.username, 'success')
            return redirect(url_for('users'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists', 'error')
    return render_template('users/add_user.html', form=form)


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get(user_id)
    if user:
        editUserForm = EditUserForm(obj=user)
        editPassForm = EditPassForm(obj=user)
        if current_user.is_admin or current_user.username == user.username:
            if editUserForm.submitEdit.data and editUserForm.validate_on_submit():
                user.avatar = editUserForm.avatar.data
                user.username = editUserForm.username.data
                if current_user.is_admin:
                    if editUserForm.is_admin.data:
                        user.is_admin = editUserForm.is_admin.data
                    if  editUserForm.is_enabled.data:
                        user.is_enabled = editUserForm.is_enabled.data
                try:
                    db.session.commit()
                    log_event('Account updated: ' + user.username)
                    flash('Account updated.', 'success')
                except IntegrityError:
                    db.session.rollback()
                    flash('Username already exists', 'error')
            if editPassForm.submitPass.data and editPassForm.validate_on_submit():
                if check_password_hash(user.password, editPassForm.oldPassword.data):
                    user.password = generate_password_hash(editPassForm.newPassword.data, method='sha256')
                    db.session.commit()
                    log_event('Password updated: ' + user.username)
                    flash('Password updated.', 'success')
                else:
                    flash('Incorrect password.', 'error')
            return render_template('users/edit_user.html', editUserForm = editUserForm, editPassForm=editPassForm)
        else:
            flash('You are not authorized to perform this action.', 'error')
            return redirect(url_for('users'))
    flash('User not found', 'error')
    return redirect(url_for('users'))




@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('You are not authorized to perform this action.', 'error')
        return redirect(url_for('users'))
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    log_event('User deleted: ' + user.username)
    flash('User deleted: ' + user.username, 'success')
    return redirect(url_for('users'))