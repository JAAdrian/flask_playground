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
    selling_form = SellItemForm()

    if request.method == 'POST':
        purchased_item = request.form.get('purchased_item')
        purchased_item_object = Item.query.filter_by(name=purchased_item).first()

        if purchased_item_object:
            if current_user.can_purchase(purchased_item_object):
                purchased_item_object.buy(current_user)
                flash(
                    f'Congratulations! You have purchased '
                    f'{purchased_item_object.name} for '
                    f'{purchased_item_object.price} EUR.',
                    category='success'
                )
            else:
                flash(
                    f'Unfortunately, you do not have enough money to purchase '
                    f'"{purchased_item_object.name}"!',
                    category='danger'
                )


        sold_item = request.form.get('sold_item')
        sold_item_object = Item.query.filter_by(name=sold_item).first()

        if sold_item_object:
            if current_user.can_sell(sold_item_object):
                sold_item_object.sell(current_user)
                flash(
                    f'Congratulations! You have sold '
                    f'{sold_item_object.name} for '
                    f'{sold_item_object.price} EUR.',
                    category='success'
                )
            else:
                flash(
                    f'Unfortunately, you do not own '
                    f'"{sold_item_object.name}"!',
                    category='danger'
                )

        return redirect(url_for('market_page'))

    if request.method == 'GET':
        items = Item.query.filter_by(owner=None)

        owned_items = Item.query.filter_by(owner=current_user.id)

        return render_template(
            'market.html', 
            items=items, 
            purchase_form=purchase_form,
            selling_form=selling_form,
            owned_items=owned_items
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
