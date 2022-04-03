from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from market import app
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchseItemForm, SellItemForm
from market import db



@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')



@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchseItemForm()
    if request.method == 'POST':
        purchased_item = request.form.get('purchased_item')
        purchased_item_object = Item.query.filter_by(name=purchased_item).first()

        if purchased_item_object:
            purchased_item_object.owner = current_user.id
            current_user.budget -= purchased_item_object.price
            db.session.commit()

            flash(
                f'Congratulations! You have purchased '
                f'{purchased_item_object.name} for '
                f'{purchased_item_object.price} EUR.'
            )

    if request.method == 'GET':
        items = Item.query.filter_by(owner=None)
        return render_template(
            'market.html', 
            items=items, 
            purchase_form=purchase_form
        )



@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()

    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()

        login_user(user_to_create)
        flash(
            (f'Account created successfully. You are now logged in as '
             f'{user_to_create.username}'),
            category='success'
        )

        return redirect(url_for('market_page'))

    if form.errors:
        for err_message in form.errors.values():
            flash(
                f'There was an error with creating a user: {err_message}',
                category='danger'
            )

    return render_template('register.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        is_valid_login = (
            attempted_user and 
            attempted_user.check_password_correction(
                attempted_password=form.password.data
            )
        )
        
        if is_valid_login:
            login_user(attempted_user)
            flash(
                f'Successfully logged in as {attempted_user.username}',
                category='success'
            )
            
            return redirect(url_for('market_page'))
    
        else:
            flash(
                'Either username or password are incorrect. Please try again.',
                category='danger'
            )

    return render_template('login.html', form=form)



@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out successfully.', category='info')
    return redirect(url_for('home_page'))
