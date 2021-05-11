from flask import render_template, redirect, request, url_for, flash
from taquesproject import app, database, bcrypt
from taquesproject.forms import FormLogin, FormCriarConta, FormEditarPerfil
from taquesproject.models import Usuario
from flask_login import login_user, logout_user, current_user, login_required

lista_usuarios = ['Gustavo', 'Michele', 'Gabriel', 'Leticia']


@app.route('/')  # Decorator para definir a rota da página
def home():
    return render_template('home.html')  # Ele chama uma página HTML. CHAMAR SEMPRE ENTRE ASPAS!!!


@app.route('/contato')
def contato():
    return render_template('contato.html')


@app.route('/usuarios')
@login_required
def usuarios():
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route('/login', methods=['GET', 'POST'])
def login_criarconta():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()
    if form_login.validate_on_submit() and 'submit_login' in request.form:  # Confirma se o botão que ele apertou é o de login
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()  # O usuário recebe o e-mail que ele acabou de digitar no campo do email no login
        if usuario and bcrypt.check_password_hash(usuario.password, form_login.password.data):  # Confirma se o email e senha são daquele usuário
            login_user(usuario, remember=form_login.lembrar_dados.data)  # Faz o login do usuário no site
            flash(f'Login feito com sucesso no e-mail {form_login.email.data}', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Falha no login. E-mail ou senha incorretos.', 'alert-danger')
    elif form_criarconta.validate_on_submit() and 'submit_criarconta' in request.form:  # Confirma se o botão que ele apertou é o de criar conta
        pw_crypt = bcrypt.generate_password_hash(form_criarconta.password.data)
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, password=pw_crypt)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada com sucesso com o e-mail {form_login.email.data}', 'alert-success')
        return redirect(url_for('home'))
    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)


@app.route('/sair')
@login_required
def logout():
    logout_user()
    flash(f'Logout feito com sucesso!', 'alert-success')
    return redirect(url_for('home'))


@app.route('/profile')
@login_required
def profile():
    profile_picture = url_for('static', filename=f'fotos_perfil/{current_user.profile_pic}')
    return render_template('profile.html', profile_picture=profile_picture)


@app.route('/post/criar')
@login_required
def create_post():
    return render_template('criarpost.html')


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data
        database.session.commit()
        flash('Perfil atualizado com sucesso!', 'alert-success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username
    profile_picture = url_for('static', filename=f'fotos_perfil/{current_user.profile_pic}')
    return render_template('editarperfil.html', profile_picture=profile_picture, form=form)
