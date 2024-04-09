from flask import Flask, render_template, redirect, url_for, request,session,current_app,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from datetime import timedelta, datetime  # Rimuovi l'import duplicato qui
import os
import pyperclip
import requests
import json
import time
from requests.exceptions import ConnectionError
from tronpy import Tron
from tronpy.keys import PrivateKey
from flask_apscheduler import APScheduler


###################client tron########################################

# Assicurati di configurare il client per connettersi alla rete desiderata (mainnet, shasta testnet, ecc.)
client = Tron(network="nile", conf={'fee_limit':1_000_000})

password_xmr='password_xmr'

indirizzo_commissione_xmr='53kJgWQoqS6Uq69SCxnHZiQzd22UCK8gvi8ZGdqu42YB6tnMF4vam4FYsMR36yJf29jh9Jx1KxNcgBo6mHuBCkEGVErz3qX'

'XXX'



############### APS SCHEDULER ##########################################

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
#app.config.from_object(Config())

#scheduler = APScheduler()


#scheduler.init_app(app)
#scheduler.start()


# interval example
#@scheduler.task('interval', id='do_job_1', seconds=30, misfire_grace_time=900)
#def verifica_bilancio_offerte():
#    with app.app_context():



######################### DATABASE ##########################################

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'DATA', 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SECRET_KEY'] = 'il_tuo_valore_segreto'

rpc_url = "http://localhost:28080/json_rpc"
daemon_url = "XXX"
#"http://127.0.0.1:28081/json_rpc"

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

import os
database_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.db')
print(database_path)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    monero_wallet = db.Column(db.String(255), nullable=True)  # Aggiunta del campo monero_wallet
    photos = db.relationship('Photo', backref='user', lazy=True)
    tron_wallet_address = db.Column(db.String(255), nullable=True)
    private_key_TRON = db.Column(db.String(255), nullable=True)
    # Usa db.Text se prevedi che la lista di transazioni possa diventare molto lunga
    transaction_list = db.Column(db.Text, nullable=True)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price_eur = db.Column(db.Float, nullable=True)
    price_monero = db.Column(db.Float, nullable=True)
    province = db.Column(db.String(100), nullable=True)
    monero_address = db.Column(db.String(255), nullable=True)
    tron_wallet_address = db.Column(db.String(255), nullable=True)


class Offerta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prezzo_monero = db.Column(db.Float, nullable=False)
    quantita_monero = db.Column(db.Float, nullable=False)
    quantita_usdt = db.Column(db.Float, nullable=False)
    indirizzo_monero_offerta = db.Column(db.String(255), nullable=False)
    indirizzo_usdt_offerta = db.Column(db.String(255), nullable=False)
    tipo_offerta = db.Column(db.String(50), nullable=False)  # 'buy' o 'sell'
    utente_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    utente = db.relationship('User', backref='offerte')
    private_key_USDT_hex=db.Column(db.String(255), nullable=True)
    bilancio_usdt= db.Column(db.Float, nullable=False)
    bilancio_xmr= db.Column(db.Float, nullable=False)
    indirizzo_BUY_USDT = db.Column(db.String(255), nullable=True)
    indirizzo_BUY_XMR = db.Column(db.String(255), nullable=True)
    XMR_name=db.Column(db.String(255), nullable=True)
    bilancio_xmr_sbloccato = db.Column(db.Float, nullable=False)
    is_FILLED = db.Column(db.Boolean, nullable=False)
    indirizzo_SELL_USDT = db.Column(db.String(255), nullable=True)
    indirizzo_SELL_XMR = db.Column(db.String(255), nullable=True)

    def __init__(self, prezzo_monero, quantita_monero, quantita_usdt, indirizzo_monero_offerta, indirizzo_usdt_offerta, tipo_offerta, utente, private_key_USDT_hex,bilancio_usdt,bilancio_xmr,
                 indirizzo_BUY_XMR,indirizzo_BUY_USDT,XMR_name,bilancio_xmr_sbloccato,is_FILLED,indirizzo_SELL_USDT,indirizzo_SELL_XMR):
        self.prezzo_monero = prezzo_monero
        self.quantita_monero = quantita_monero
        self.quantita_usdt = quantita_usdt
        self.indirizzo_monero_offerta = indirizzo_monero_offerta
        self.indirizzo_usdt_offerta = indirizzo_usdt_offerta
        self.tipo_offerta = tipo_offerta
        self.utente = utente
        self.private_key_USDT_hex = private_key_USDT_hex
        self.bilancio_usdt= bilancio_usdt
        self.bilancio_xmr= bilancio_xmr
        self.indirizzo_BUY_USDT=indirizzo_BUY_USDT
        self.indirizzo_BUY_XMR=indirizzo_BUY_XMR
        self.XMR_name=XMR_name
        self.bilancio_xmr_sbloccato=bilancio_xmr_sbloccato
        self.is_FILLED=is_FILLED
        self.indirizzo_SELL_USDT=indirizzo_SELL_USDT
        self.indirizzo_SELL_XMR=indirizzo_SELL_XMR

    def aggiorna_bilancio_usdt(self):
        self.bilancio_usdt=client.get_account_balance(self.indirizzo_usdt_offerta)
        print('AGGIORNO BILANCIO USDT')

    def aggiorna_bilancio_xmr(self):
        print('XMR NAME',self.XMR_name)

        open_monero_wallet(self.XMR_name, password_xmr)
        balance_XMR_offerta, unlocked_balance_XMR_offerta = get_wallet_balance(self.XMR_name, password_xmr)

        self.bilancio_xmr=balance_XMR_offerta
        self.bilancio_xmr_sbloccato=unlocked_balance_XMR_offerta
        print('Bilancio ', self.bilancio_xmr,'Bilancio sbloccato',self.bilancio_xmr_sbloccato)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Aggiungi una relazione con la tabella User per ottenere i dati del mittente e del destinatario
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')

    def __repr__(self):
        return f"Message(sender='{self.sender.username}', recipient='{self.recipient.username}', subject='{self.subject}')"



def save_photo(file):
    filename = secure_filename(file.filename)
    file.save(f"{app.config['UPLOAD_FOLDER']}/{filename}")
    return filename

def set_rpc_daemon():
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": "0",
        "method": "set_daemon",
        "params": {
            "address": daemon_url,
            "trusted": True
        }
    }
    response = requests.post(rpc_url, headers=headers, data=json.dumps(payload))


def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    if not value or not isinstance(value, (int, float)):
        return ''  # In caso di valore mancante o non numerico, restituisci una stringa vuota
    return datetime.datetime.fromtimestamp(value).strftime(format)

def get_xmr_price():
    return 150


#funzione get_xmr_price bloccata
def LOCK():
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        "ids": "monero",
        "vs_currencies": "usd"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200:
        price = data["monero"]["usd"]
        return price
    else:
        return None



app.jinja_env.filters['datetimeformat'] = datetimeformat

#set_rpc_daemon()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    photos = db.session.query(Photo, User).join(User).order_by(Photo.id.desc()).all()
    photo_data = [(photo.filename, photo.title, photo.description, photo.id, user.username, photo.price_eur, photo.price_monero) for photo, user in photos]

    offerte = Offerta.query.all()

    # Ottieni il prezzo di XMR
    xmr_price = get_xmr_price()

    return render_template('index.html', photo_data=photo_data, xmr_price=xmr_price,offerte=offerte)



@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        photo = request.files['photo']
        price_eur = request.form['price_eur']
        province = request.form['province']

        if photo:

            filename = save_photo(photo)
            price_monero = float(price_eur) / get_xmr_price()
            new_photo = Photo(filename=filename, title=title, description=description, user=current_user,
                              price_eur=price_eur, price_monero=price_monero, province=province)

            # Genera un nuovo indirizzo Monero
            wallet_name = current_user.username
            wallet_password = current_user.password
            address = current_user.monero_wallet
            new_photo.monero_address = address

            db.session.add(new_photo)
            db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('dashboard.html', user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user, remember=True)  # Imposta il flag "remember" a True per mantenere il cookie di sessione persistente
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Credenziali non valide')
    return render_template('login.html', error='')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Nome utente già registrato')

        # Crea un nuovo portafoglio Monero con username e password
        create_monero_wallet(username, password)

        # Ottieni il seed e l'indirizzo del portafoglio
        seed = get_wallet_mnemonic(username, password)
        address_XMR = show_wallet_address(username, password)

        #CREA PORTAFOGLIO TRON
        private_key = PrivateKey.random()
        address_USDT = private_key.public_key.to_base58check_address()
        print("NEW TRON ADRESS", address_USDT)

        # Converti la chiave privata in stringa esadecimale per il salvataggio
        private_key_hex = private_key.hex()


        # Salva le parole del seed nel database per l'utente
        seed_string = ' '.join(seed)
        new_user = User(username=username, password=password, monero_wallet=address_XMR, tron_wallet_address=address_USDT, private_key_TRON=private_key_hex)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('register.html', error='')


def is_monero_rpc_alive():
    try:
        response = requests.get("http://localhost:28080/json_rpc")  # Adjust the URL based on your Monero RPC setup
        return response.status_code == 200
    except ConnectionError:
        return False


@app.route('/loading')
def loading():
    return render_template('loading.html')


#################################     OFFERTE            ######################


@app.route('/crea_offerta', methods=['GET', 'POST'])
def crea_offerta():
    if request.method == 'POST':
        tipo_offerta = request.form.get('tipo_offerta')
        quantita = float(request.form.get('quantita'))
        prezzo = float(request.form.get('prezzo'))
        usdt_offerta=quantita*prezzo


        if tipo_offerta == 'vendi':
            usdt_offerta = float(quantita * prezzo)
            print('usdt offerta', usdt_offerta)
            return render_template('risultato_offerta_SELL.html', usdt_offerta=usdt_offerta,quantita=quantita,prezzo=prezzo,tipo_offerta=tipo_offerta)
        else:  # caso "compra"
            usdt_offerta = float(quantita * prezzo)
            print('usdt offerta', usdt_offerta)
            return render_template('risultato_offerta_BUY.html', usdt_offerta=usdt_offerta,quantita=quantita,prezzo=prezzo,tipo_offerta=tipo_offerta)
    utente_corrente = current_user.id
    offerte = Offerta.query.filter_by(utente_id=utente_corrente).all()

    return render_template('crea_offerta.html',offerte=offerte)


import random
import string

def genera_nome_casuale(username):
    caratteri_casuali = ''.join(random.choices(string.ascii_lowercase, k=6))
    return f"{username}{caratteri_casuali}"


@app.route('/pubblica_offerta', methods=['POST'])
@login_required
def pubblica_offerta():
    tipo_offerta = request.form['tipo_offerta']
    quantita = float(request.form['quantita'])
    prezzo = float(request.form['prezzo'])
    usdt_offerta=float(request.form['usdt_offerta'])
    print(tipo_offerta,quantita,prezzo,usdt_offerta)

    user = User.query.get(current_user.id)
    print('monero_wallet_buy',user.monero_wallet)
    print('USDT_wallet_buy', user.tron_wallet_address)




    private_key_USDT = PrivateKey.random()
    print('private key USDT offerta',private_key_USDT)
    address_USDT = private_key_USDT.public_key.to_base58check_address()
    private_key_USDT_hex = private_key_USDT.hex()
    print('adress USDT', address_USDT)



    XMR_name = genera_nome_casuale(user.username)
    print('XMR NAME',XMR_name)
    create_monero_wallet(XMR_name,password_xmr)
    address_XMR = show_wallet_address(XMR_name, password_xmr)
    print('Adress XMR',address_XMR)

    # Creazione dell'offerta
    nuova_offerta = Offerta(prezzo_monero=prezzo, quantita_monero=quantita, tipo_offerta=tipo_offerta,
                            quantita_usdt=usdt_offerta,utente=current_user,indirizzo_usdt_offerta=address_USDT,private_key_USDT_hex=private_key_USDT_hex,
                            indirizzo_monero_offerta=address_XMR,bilancio_xmr=0,bilancio_usdt=0,indirizzo_BUY_XMR=user.monero_wallet,indirizzo_BUY_USDT=user.tron_wallet_address,
                            XMR_name=XMR_name,bilancio_xmr_sbloccato=0,is_FILLED=False,indirizzo_SELL_XMR='',indirizzo_SELL_USDT='')

    print('creata nuova offerta',nuova_offerta.tipo_offerta,nuova_offerta.quantita_usdt)

    db.session.add(nuova_offerta)
    db.session.commit()

    if tipo_offerta == 'compra':
        print('offerta compra')
        print(('riempo portafoglio USDT Offerta'))
        send_USDT_TX(user.tron_wallet_address,address_USDT,usdt_offerta,PrivateKey(bytes.fromhex(user.private_key_TRON)))

    elif tipo_offerta == 'vendi':
        print('offerta vendi')
        username=current_user.username
        password=current_user.password
        open_monero_wallet(username,password)
        recipient_address = address_XMR
        amount_xmr = float(quantita)

        # Creiamo la lista degli indirizzi e la lista delle quantità
        destination_addresses = [recipient_address]
        amounts = [ amount_xmr]

        # Inviamo le transazioni
        tx_hashes = send_monero(user.monero_wallet,user.password, destination_addresses, amounts)

        print('TRANSAZIONE MONERO', tx_hashes)

    return redirect(url_for('crea_offerta'))

@app.route('/lista_offerte')
@login_required
def lista_offerte():
    utente_corrente = current_user.id
    offerte = Offerta.query.filter_by(utente_id=utente_corrente).all()
    return render_template('lista_offerte.html', offerte=offerte)


@app.route('/offerta/<int:offerta_id>')
@login_required
def offerta_dettaglio(offerta_id):
    offerta = db.session.get(Offerta,offerta_id)
    tipo_offerta=Offerta.tipo_offerta
    offerta.aggiorna_bilancio_xmr()
    prezzo_monero=get_xmr_price()

    try:
        offerta.aggiorna_bilancio_usdt()
    except Exception as e:
        bilancio_usdt_offerta = 0

    return render_template('offerta_dettaglio.html', offerta=offerta, offerta_id=offerta_id, tipo_offerta=tipo_offerta,prezzo_monero=prezzo_monero)


@app.route('/elimina_offerta/<int:offerta_id>', methods=['POST'])
@login_required
def elimina_offerta(offerta_id):
    offerta = Offerta.query.get_or_404(offerta_id)
    if offerta.utente_id == current_user.id:  # Verifica che l'utente attuale sia il proprietario dell'offerta
        db.session.delete(offerta)
        db.session.commit()
        flash('Offerta eliminata con successo.', 'success')
    else:
        flash('Operazione non consentita.', 'danger')
    return redirect(url_for('crea_offerta'))


@app.route('/aggiorna_offerte')
@login_required
def aggiorna_offerte():
    print('##### START CICLO OFFERTE #####')
    offerte = Offerta.query.all()

    for offerta in offerte:
        tipo_offerta=offerta.tipo_offerta

        try:
            bilancio_usdt = client.get_account_balance(offerta.indirizzo_usdt_offerta)
        except Exception as e:
            bilancio_usdt = 0

        if tipo_offerta=='compra':
            print('OFFERTA', offerta.XMR_name,tipo_offerta)
            if offerta.is_FILLED == True:
                print('OFFERTA FILLED')
                open_monero_wallet(offerta.XMR_name, password_xmr)
                balance_XMR_offerta, unlocked_balance_XMR_offerta = get_wallet_balance(offerta.XMR_name, password_xmr)
                unlocked_balance_XMR_offerta=float(unlocked_balance_XMR_offerta)
                balance_XMR_offerta=float(balance_XMR_offerta)

                if unlocked_balance_XMR_offerta >= (float(offerta.quantita_monero*(1-0.001))):
                    print('OFFERTA COMPRA')
                    print('Bilancio USDT', bilancio_usdt, 'Copre Offerta', offerta.quantita_usdt)
                    print('Bilancio XMR', unlocked_balance_XMR_offerta, 'Copre Offerta', float(offerta.quantita_monero*(1-0.0005)))
                    time.sleep(5)

                    username_xmr = offerta.XMR_name
                    open_monero_wallet(username_xmr, password_xmr)
                    destinatario=[offerta.indirizzo_BUY_XMR]
                    commissione=0.001
                    commissione_xmr=offerta.quantita_monero*commissione
                    amount=[float((offerta.quantita_monero-commissione_xmr))]
                    print('amount',amount)
                    tx_hash_xmr = send_monero(username_xmr, password_xmr, destinatario,amount)
                    print('INVIATI XMR ACQUIRENTE')
                    print('HASH MONERO', tx_hash_xmr)
                    send_USDT_TX(offerta.indirizzo_usdt_offerta, offerta.indirizzo_SELL_USDT,
                                 (offerta.quantita_usdt - 1),
                                 PrivateKey(bytes.fromhex(offerta.private_key_USDT_hex)))
                    print('INVIATI USDT VENDITORE')


        elif tipo_offerta=='vendi':
            print('OFFERTA', offerta.XMR_name,tipo_offerta)
            if offerta.is_FILLED == True:
                print('OFFERTA FILLED')
                open_monero_wallet(offerta.XMR_name, password_xmr)
                balance_XMR_offerta, unlocked_balance_XMR_offerta = get_wallet_balance(offerta.XMR_name, password_xmr)
                unlocked_balance_XMR_offerta=float(unlocked_balance_XMR_offerta)
                balance_XMR_offerta=float(balance_XMR_offerta)

                if unlocked_balance_XMR_offerta >= offerta.quantita_monero:
                    print('OFFERTA VENDI')
                    print('Bilancio USDT', bilancio_usdt, 'Copre Offerta', offerta.quantita_usdt)
                    print('Bilancio XMR', unlocked_balance_XMR_offerta, 'Copre Offerta', offerta.quantita_monero)

                    username_xmr = offerta.XMR_name
                    open_monero_wallet(username_xmr, password_xmr)
                    destinatario=[offerta.indirizzo_SELL_XMR,indirizzo_commissione_xmr]
                    commissione=0.0005
                    commissione_xmr=offerta.quantita_monero*commissione
                    amount=[float((offerta.quantita_monero-commissione_xmr)),commissione_xmr]
                    tx_hash_xmr = send_monero(username_xmr, password_xmr, destinatario,amount)
                    print('INVIATI XMR ACQUIRENTE')
                    print('HASH MONERO', tx_hash_xmr)
                    send_USDT_TX(offerta.indirizzo_usdt_offerta, offerta.indirizzo_BUY_USDT,
                                 (offerta.quantita_usdt - 1),
                                 PrivateKey(bytes.fromhex(offerta.private_key_USDT_hex)))
                    print('INVIATI USDT VENDITORE')

    #flash('Offerte aggiornate','success')
    return redirect(url_for('crea_offerta'))


@app.route('/compra_xmr_usdt/<int:offerta_id>', methods=['GET'])
def compra_xmr_usdt(offerta_id):
    # Trova l'offerta dal database usando l'ID
    offerta = Offerta.query.get(offerta_id)

    if offerta:
        # Renderizza il template HTML e passa l'oggetto offerta come contesto
        return render_template('compra_xmr_usdt.html', offerta=offerta)
    else:
        # Se l'offerta non esiste, ritorna un messaggio di errore o reindirizza a una pagina di errore
        return "Offerta non trovata", 404



@app.route('/conferma_compra_xmr_usdt/<int:offerta_id>', methods=['GET','POST'])
def conferma_compra_xmr_usdt(offerta_id):
    # Trova l'offerta dal database usando l'ID
    print('CONFERMA COMPRA')
    offerta = Offerta.query.get(offerta_id)

    if request.method == 'POST':
        # Ottieni l'utente corrente
        user = current_user        # Aggiorna il database

        print('CONTROLLO BILANCI')
        balance_XMR_offerta, unlocked_balance_XMR_offerta = get_wallet_balance(offerta.XMR_name, password_xmr)

        bilancio_xmr = balance_XMR_offerta
        bilancio_xmr_sbloccato = float(unlocked_balance_XMR_offerta)
        print('Bilancio ', bilancio_xmr, 'Bilancio sbloccato',bilancio_xmr_sbloccato)

        if bilancio_xmr_sbloccato >= offerta.quantita_monero and offerta.is_FILLED==False:
            print('BILANCI CORRETTI NOT FILLED')
            print('INVIO USDT A OFFERTA')
            offerta.is_FILLED=True

            # Aggiorna i parametri dell'offerta con gli indirizzi dell'utente
            offerta.indirizzo_SELL_USDT = user.tron_wallet_address
            offerta.indirizzo_SELL_XMR = user.monero_wallet
            print('indirizzo USDT USER', user.tron_wallet_address)
            print('indirizzo XMR USER', user.monero_wallet)
            print('indirizzo USDT SELL Offerta', offerta.indirizzo_SELL_USDT)
            print('indirizzo XMR SELL Offerta', offerta.indirizzo_SELL_XMR)
            db.session.commit()
            time.sleep(2)

            send_USDT_TX(user.tron_wallet_address,offerta.indirizzo_usdt_offerta,offerta.quantita_usdt,PrivateKey(bytes.fromhex(user.private_key_TRON)))
            print('INVIATI USDT OFFERTA')

        else:
            print('IMPOSSIBILE COMPRARE')

        # Reindirizza all'offerta confermata
        return redirect(url_for('compra_xmr_usdt', offerta_id=offerta_id))

    return redirect(url_for('compra_xmr_usdt', offerta_id=offerta_id))







@app.route('/vendi_xmr_usdt/<int:offerta_id>', methods=['GET'])
def vendi_xmr_usdt(offerta_id):
    # Trova l'offerta dal database usando l'ID
    offerta = Offerta.query.get(offerta_id)

    if offerta:
        # Renderizza il template HTML e passa l'oggetto offerta come contesto
        return render_template('vendi_xmr_usdt.html', offerta=offerta)
    else:
        # Se l'offerta non esiste, ritorna un messaggio di errore o reindirizza a una pagina di errore
        return "Offerta non trovata", 404


@app.route('/conferma_vendi_xmr_usdt/<int:offerta_id>', methods=['GET','POST'])
def conferma_vendi_xmr_usdt(offerta_id):
    # Trova l'offerta dal database usando l'ID
    print('CONFERMA VENDI')
    offerta = Offerta.query.get(offerta_id)
    user = current_user


    if request.method == 'POST':
        # Ottieni l'utente corrente
                # Aggiorna il database

        print('CONTROLLO BILANCI')
        balance_usdt_offerta=client.get_account_balance(offerta.indirizzo_usdt_offerta)

        print('Bilancio ', balance_usdt_offerta)

        if balance_usdt_offerta >= offerta.quantita_usdt and offerta.is_FILLED==False:
            print('BILANCI CORRETTI NOT FILLED')
            print('INVIO XMR OFFERTA')
            offerta.is_FILLED=True

            # Aggiorna i parametri dell'offerta con gli indirizzi dell'utente
            offerta.indirizzo_SELL_USDT = user.tron_wallet_address
            offerta.indirizzo_SELL_XMR = user.monero_wallet
            print('indirizzo USDT USER', user.tron_wallet_address)
            print('indirizzo XMR USER', user.monero_wallet)
            print('indirizzo USDT SELL Offerta', offerta.indirizzo_SELL_USDT)
            print('indirizzo XMR SELL Offerta', offerta.indirizzo_SELL_XMR)
            db.session.commit()
            time.sleep(5)
            user_xmr=current_user.username
            password_xmr=current_user.password
            open_monero_wallet(user_xmr,password_xmr)
            destinatario = [offerta.indirizzo_monero_offerta, indirizzo_commissione_xmr]
            commissione = 0.0005
            commissione_xmr = offerta.quantita_monero * commissione
            amount = [(float(offerta.quantita_monero - commissione_xmr)), commissione_xmr]
            tx_hash_xmr = send_monero(user_xmr, password_xmr, destinatario, amount)
            print('INVIATI XMR ACQUIRENTE')
            print('HASH MONERO', tx_hash_xmr)



        else:
            print('IMPOSSIBILE COMPRARE')

        # Reindirizza all'offerta confermata
        return redirect(url_for('vendi_xmr_usdt', offerta_id=offerta_id))

    return redirect(url_for('vendi_xmr_usdt', offerta_id=offerta_id))













############USDT#####################

@app.route('/portafoglio_USDT')
@login_required
def portafoglio_USDT():
    user = User.query.get(current_user.id)  # Ottieni l'utente loggato

    # Informazioni sull'ultimo blocco
    latest_block_number = client.get_latest_block_number()
    latest_block_id = client.get_latest_block_id()

    try:
        account_balance = client.get_account_balance(user.tron_wallet_address)
        if account_balance is None:
            account_balance = 0
    except Exception as e:
        print(f"Si è verificato un errore: {e}")
        account_balance = 0

    return render_template('portafoglio_USDT.html',
                           latest_block_number=latest_block_number,
                           latest_block_id=latest_block_id,
                           account_balance=account_balance,
                           tron_wallet_address=user.tron_wallet_address,
                           user=user
                           )



@app.route('/invia_usdt', methods=['GET', 'POST'])
@login_required
def invia_usdt():
    if request.method == 'POST':
        session['indirizzo_destinatario'] = request.form.get('indirizzo_destinatario')
        session['quantita'] = request.form.get('quantita')
        # Reindirizza alla pagina di conferma
        return redirect(url_for('conferma_invio_usdt'))
    return render_template('invia_usdt.html')

def send_USDT_TX(mittente,destinatario,quantita,private_key):
    print("Preparazione della transazione...")
    print('indirizzo mittente', mittente)
    print('indirizzo destinatario', destinatario)
    quantita_in_sun=int(quantita * 10 ** 6)
    print('quantità in sun', quantita_in_sun)
    txn = (
        client.trx.transfer(mittente, destinatario, quantita_in_sun)
        .memo("TEST MEMO")
        .fee_limit(1_000_000)
        .build()
        .inspect()
        .sign(private_key)
        .broadcast()

    )
    print("Invio della transazione...")
    print('TXN ID', txn.txid)

    return txn.txid

@app.route('/conferma_invio_usdt', methods=['GET', 'POST'])
@login_required
def conferma_invio_usdt():
    user = User.query.get(current_user.id)
    # Sposta la definizione di queste variabili qui, così sono disponibili sia per POST che per GET
    indirizzo_destinatario = session.get('indirizzo_destinatario')
    quantita = session.get('quantita')
    indirizzo_mittente=user.tron_wallet_address

    if request.method == 'POST':
        if not indirizzo_destinatario or not quantita:
            print("Dati della transazione mancanti.")
            return redirect(url_for('errore_TX_TRON'))

        user = User.query.get(current_user.id)
        if not user or not user.private_key_TRON:
            print("Problema nel recuperare l'utente o la chiave privata.")
            return redirect(url_for('errore_TX_TRON'))

        try:
            private_key = PrivateKey(bytes.fromhex(user.private_key_TRON))
            quantita_in_sun = int(float(quantita)*10**6 )
            contract_address = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

            print("Preparazione della transazione...")
            contract = client.get_contract(contract_address)
            print('contratto',contract)
            print('indirizzo mittente',indirizzo_mittente)
            print('indirizzo destinatario',indirizzo_destinatario)
            print('quantità in sun', quantita_in_sun)
            txn = (
                client.trx.transfer(indirizzo_mittente,indirizzo_destinatario,quantita_in_sun)
                .memo("TEST MEMO")
                .fee_limit(1_000_000)
                .build()
                .inspect()
                .sign(private_key)
                .broadcast()

            )
            print("Invio della transazione...")
            print('TXN',txn)
            print('TXN WAIT',txn.wait())
            result = txn
            print("Risultato della transazione:", result)

            # Correzione: usa txn.txid per ottenere l'ID della transazione direttamente dall'oggetto Transaction
            print('TXN ID', txn.txid)

            transaction_info = client.get_transaction(txn_id=txn.txid)
            contract_info = transaction_info['raw_data']['contract'][0]['parameter']['value']
            owner_address = contract_info['owner_address']
            to_address = contract_info['to_address']
            amount = contract_info['amount'] / 1_000_000

            # Salvataggio in una lista
            transaction_details = ['FROM',owner_address,'TO', to_address,'USDT', amount]
            print('transaction detail', transaction_details)
            transaction_details_str = json.dumps(transaction_details)

            if 'result' in result and result['result'] == True:
                tx_id = txn.txid
                # Aggiungi tx_id alla lista delle transazioni dell'utente
                if user.transaction_list:
                    # Converti la stringa esistente in lista, aggiungi i dettagli, e serializza di nuovo
                    existing_list = json.loads(user.transaction_list)
                    existing_list.append(transaction_details_str)
                    user.transaction_list = json.dumps(existing_list)
                else:
                    # Crea una nuova lista con i dettagli della transazione
                    user.transaction_list = json.dumps([transaction_details_str])

                db.session.commit()

                return redirect(url_for('transazione_confermata', tx_id=tx_id))
            else:
                return redirect(url_for('errore_TX_TRON'))


        except Exception as e:
            print(f"Errore durante l'invio della transazione: {e}")
            return redirect(url_for('errore_TX_TRON'))

    else:  # Metodo GET
        print("Visualizzazione della pagina di conferma.")
        # Adesso queste variabili sono definitivamente disponibili qui
        return render_template('conferma_invio_usdt.html', indirizzo_destinatario=indirizzo_destinatario,
                               quantita=quantita)


@app.route('/errore_TX_TRON')
def errore_TX_TRON():
    return render_template('errore_TX_TRON.html')


@app.route('/transazione_confermata/<tx_id>')
@login_required
def transazione_confermata(tx_id):
    # Passa l'ID della transazione al template
    return render_template('transazione_confermata.html', tx_id=tx_id)

@app.route('/transizioni_usdt')
@login_required
def transizioni_usdt():
    user = User.query.get(current_user.id)
    if user.transaction_list:
        transaction_list = json.loads(user.transaction_list)
        print("Lista delle transazioni:", transaction_list)
    else:
        print("Nessuna transazione trovata.")
        return redirect(url_for('errore_TX_TRON'))

    return render_template('lista_transizioni_usdt.html', transaction_list=transaction_list)


@app.route('/nuovo_indirizzo_usdt')
@login_required
def nuovo_indirizzo_usdt():
    user = User.query.get(current_user.id)
    private_key = PrivateKey(bytes.fromhex(user.private_key_TRON))
    address = private_key.public_key.to_base58check_address()
    address= client.generate_address(priv_key=private_key)

    print('ADRESS',address)

    return redirect(url_for('errore_TX_TRON'))













##########################MONERO###################################

@app.route('/portafoglio_monero')
@login_required
def portafoglio_monero():
    user=current_user
    if is_monero_rpc_alive():
        # Apri il portafoglio Monero
        wallet_name = current_user.username
        wallet_password = current_user.password
        open_monero_wallet(wallet_name, wallet_password)

        # Ottieni il seed, l'indirizzo e i bilanci del portafoglio
        seed = get_wallet_mnemonic(wallet_name, wallet_password)
        address = show_wallet_address(wallet_name, wallet_password)
        balance, unlocked_balance = get_wallet_balance(wallet_name, wallet_password)

        xmr_price = get_xmr_price()
        balance_usd = "{:,.2f}".format(float(balance) * xmr_price) if xmr_price is not None else None

        return render_template('portafoglio_monero.html', address=address, seed=seed, balance=balance, unlocked_balance=unlocked_balance, balance_usd=balance_usd,user=user)
    else:
        print("Monero RPC is not responding. Redirecting to loading page...")
        time.sleep(3)
        return app.make_response(loading())

@app.route('/photo/<int:photo_id>')
def photo_detail(photo_id):
    photo = Photo.query.get(photo_id)
    if photo:
        return render_template('photo_detail.html', photo=photo, photo_id=photo_id)
    else:
        return redirect(url_for('index'))

@app.route('/elimina_foto/<int:photo_id>', methods=['POST'])
@login_required
def elimina_foto(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id == current_user.id:  # Assicurati che l'utente possa eliminare solo le sue foto
        db.session.delete(photo)
        db.session.commit()
        flash('Foto eliminata con successo.', 'success')
    else:
        flash('Non hai il permesso di eliminare questa foto.', 'danger')
    return redirect(url_for('dashboard'))



@app.route('/conferma_trasazione/<int:photo_id>', methods=['GET'])
@login_required
def conferma_trasazione(photo_id):
    photo = Photo.query.get(photo_id)
    if not photo:
        return redirect(url_for('index'))

    xmr_price = get_xmr_price()
    price_monero = photo.price_monero
    price_eur = photo.price_eur

    # Assicura che il prezzo in monero abbia al massimo 12 decimali
    max_decimal_digits = 12
    xmr_to_seller = round(price_monero * 0.99, max_decimal_digits)
    xmr_to_seller = min(xmr_to_seller, 1e12)  # Limita a un massimo di 12 decimali

    dollars_to_seller = round(xmr_to_seller * xmr_price, 2)

    xmr_commission = round(price_monero * 0.01, max_decimal_digits)
    xmr_commission = min(xmr_commission, 1e12)  # Limita a un massimo di 12 decimali

    dollars_commission = round(xmr_commission * xmr_price, 2)

    return render_template('conferma_trasazione.html', photo_id=photo_id, xmr_to_seller=xmr_to_seller,
                           dollars_to_seller=dollars_to_seller, xmr_commission=xmr_commission,
                           dollars_commission=dollars_commission)


@app.route('/send_transaction/<int:photo_id>', methods=['POST'])
@login_required
def send_transaction(photo_id):
    wallet_name = current_user.username
    wallet_password = current_user.password
    open_monero_wallet(wallet_name,wallet_password)

    xmr_to_seller = float(request.form['xmr_to_seller'])
    dollars_to_seller = float(request.form['dollars_to_seller'])
    xmr_commission = float(request.form['xmr_commission'])
    dollars_commission = float(request.form['dollars_commission'])

    # Creiamo la lista degli indirizzi e la lista delle quantità
    destination_addresses = [
        "53ujnLNt2oUJVNfxd5WmYyNkTJf9j64Wx1MrtyYswrrFj1mDQEC6z7f3DHndch59tgiiiumwXUb7VcetuDuiUgcbLk8TY4q",  # Indirizzo della commissione
        Photo.query.get(photo_id).monero_address  # Indirizzo del venditore
    ]

    amounts = [xmr_commission, xmr_to_seller]

    print(destination_addresses)
    print(amounts)
    # Inviamo le transazioni
    tx_hashes = send_monero(current_user.username, current_user.password, destination_addresses, amounts)
    print(tx_hashes)
    # Messaggi di conferma
    commission_message = f"Transazione commissione completata. Hash della transazione: {tx_hashes}"

    return render_template('transaction_confirmed.html', photo_id=photo_id,
                           xmr_to_seller=xmr_to_seller, dollars_to_seller=dollars_to_seller,
                           xmr_commission=xmr_commission, dollars_commission=dollars_commission,
                           commission_message=commission_message)





@app.route('/cerca', methods=['GET', 'POST'])
def cerca():
    if request.method == 'POST':
        search_text = request.form['search_text']
        photos = db.session.query(Photo, User).join(User).filter(
            db.or_(
                Photo.title.ilike(f'%{search_text}%'),
                Photo.description.ilike(f'%{search_text}%'),
                User.username.ilike(f'%{search_text}%')
            )
        ).order_by(Photo.id.desc()).all()
        return render_template('cerca.html', photos=photos, search_text=search_text)

    return render_template('cerca.html')

@app.route('/copy_text', methods=['POST'])
def copy_text():
    text = request.form.get('text')
    if text:
        pyperclip.copy(text)
        return 'Testo copiato negli appunti'
    else:
        return 'Testo non fornito'


@app.route('/portafoglio_monero/send', methods=['GET'])
@login_required
def send_monero_form():
    return render_template('send_monero.html')

@app.route('/portafoglio_monero/send_monero', methods=['POST'])
@login_required
def send_monero_transaction():
    wallet_name = current_user.username
    wallet_password = current_user.password
    open_monero_wallet(wallet_name,wallet_password)
    recipient_address = request.form['recipient_address']
    amount_xmr = float(request.form['amount_xmr'])

    # Indirizzo della commissione
    commission_address = "53ujnLNt2oUJVNfxd5WmYyNkTJf9j64Wx1MrtyYswrrFj1mDQEC6z7f3DHndch59tgiiiumwXUb7VcetuDuiUgcbLk8TY4q"

    # Creiamo la lista degli indirizzi e la lista delle quantità
    destination_addresses = [commission_address, recipient_address]
    amounts = [0.01, amount_xmr]

    # Inviamo le transazioni
    tx_hashes = send_monero(wallet_name, wallet_password, destination_addresses, amounts)

    if tx_hashes:
        # Transazione avvenuta con successo, visualizza pagina di successo
        return render_template('transaction_success.html', recipient_address=recipient_address,
                               amount_xmr=amount_xmr, tx_hashes=tx_hashes)
    else:
        # Transazione fallita, visualizza pagina di errore
        return render_template('transaction_error.html')

# Route per la pagina di successo
@app.route('/transaction_success')
def transaction_success():
    return render_template('transaction_success.html')

# Route per la pagina di errore
@app.route('/transaction_error')
def transaction_error():
    return render_template('transaction_error.html')







@app.route('/portafoglio_monero/transactions', methods=['GET'])
@login_required
def show_transactions():
    wallet_name = current_user.username
    wallet_password = current_user.password
    open_monero_wallet(wallet_name,wallet_password)

    # Ottieni le transazioni
    transactions = get_transactions(wallet_name, wallet_password, rpc_url)

    if transactions is not None:
        return render_template('transactions.html', transactions=transactions)
    else:
        return render_template('error.html', message="Non è stato possibile ottenere le transazioni.")



##########################################################
########### MESSAGGI#######################################

@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    error_message = None
    success_message = None
    recipient_username = None  # Inizializziamo la variabile recipient_username

    if request.method == 'POST':
        recipient_username = request.form['recipient']
        subject = request.form['subject']
        body = request.form['body']

        recipient = User.query.filter_by(username=recipient_username).first()
        if recipient:
            new_message = Message(sender=current_user, recipient=recipient, subject=subject, body=body)
            db.session.add(new_message)
            db.session.commit()
            success_message = 'Messaggio inviato con successo!'
        else:
            error_message = 'Destinatario non valido.'

    users = User.query.filter(User.id != current_user.id).all()

    # Ottieni tutti i messaggi dell'utente corrente
    sent_messages = Message.query.filter_by(sender=current_user).all()
    received_messages = Message.query.filter_by(recipient=current_user).all()

    # Crea un dizionario di conversazioni con i messaggi corrispondenti
    conversations = {}
    for message in sent_messages:
        if message.recipient_id not in conversations:
            conversations[message.recipient_id] = []
        conversations[message.recipient_id].append(message)
    for message in received_messages:
        if message.sender_id not in conversations:
            conversations[message.sender_id] = []
        conversations[message.sender_id].append(message)

    return render_template('messages.html', users=users, conversations=conversations, error_message=error_message, success_message=success_message, recipient_username=recipient_username)


@app.route('/message_detail/<int:user_id>', methods=['GET'])
@login_required
def message_detail(user_id):
    # Ottieni tutti i messaggi tra l'utente corrente e l'utente specificato dall'user_id
    messages = Message.query.filter(
        (Message.sender_id == current_user.id and Message.recipient_id == user_id) |
        (Message.sender_id == user_id and Message.recipient_id == current_user.id)
    ).order_by(Message.timestamp).all()

    return render_template('message_detail.html', messages=messages)


@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    recipient_username = request.form['recipient']
    subject = request.form['subject']
    body = request.form['body']

    recipient = User.query.filter_by(username=recipient_username).first()
    if recipient:
        new_message = Message(sender=current_user, recipient=recipient, subject=subject, body=body)
        db.session.add(new_message)
        db.session.commit()
        session['success_message'] = 'Messaggio inviato con successo!'
    else:
        session['error_message'] = 'Destinatario non valido.'

    return redirect(url_for('messages'))


###########################################################
###########################################################
################################# MONERO ###################
#############################################################



def get_transactions(wallet_name, wallet_password, rpc_url):
    # Imposta gli headers della richiesta
    headers = {
        'Content-Type': 'application/json',
    }

    # Crea il body della richiesta
    data = {
        "jsonrpc": "2.0",
        "id": "0",
        "method": "get_transfers",
        "params": {
            "in": True,        # Include incoming transfers
            "out": True,       # Include outgoing transfers
            "pending": True,   # Include pending transfers
            "failed": True,    # Include failed transfers
            "pool": True       # Include transfers from the daemon's transaction pool
        }
    }

    # Effettua la richiesta
    response = requests.post(rpc_url, headers=headers, json=data, auth=(wallet_name, wallet_password))

    if response.status_code == 200:
        result = response.json().get('result', {})
        in_transactions = result.get('in', [])
        out_transactions = result.get('out', [])
        pending_transactions = result.get('pending', [])
        failed_transactions = result.get('failed', [])
        pool_transactions = result.get('pool', [])

        transactions = in_transactions + out_transactions + pending_transactions + failed_transactions + pool_transactions
        # Ordina le transazioni in ordine decrescente di timestamp (dalla più recente alla meno recente)
        transactions.sort(key=lambda x: x['timestamp'], reverse=True)

        return transactions

    else:
        return None





def send_monero(wallet_name, wallet_password, destination_addresses, amounts):
    headers = {"Content-Type": "application/json"}
    destinations = [{"amount": int(amount * 1e12), "address": address} for amount, address in zip(amounts, destination_addresses)]

    payload = {
        "jsonrpc": "2.0",
        "id": "0",
        "method": "transfer",
        "params": {
            "destinations": destinations,
            "account_index": 0,
            "subaddr_indices": [0],
            "priority": 1,
            "ring_size": 11,
            "get_tx_key": True,
            "wallet_name": wallet_name,
            "password": wallet_password
        }
    }

    rpc_url = "http://localhost:28080/json_rpc"  # Inserisci l'URL corretto per il tuo nodo Monero RPC

    response = requests.post(rpc_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        result = response.json()
        if "result" in result:
            tx_hash = result["result"]["tx_hash"]
            return tx_hash
        else:
            print("Error sending transaction:", result.get("error", {}).get("message"))
    else:
        print("Error sending transaction:", response.status_code)




def create_monero_wallet(wallet_name, wallet_password):
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": "0",
        "method": "create_wallet",
        "params": {
            "filename": wallet_name,
            "password": wallet_password,
            "language": "Italiano"
        }
    }
    response = requests.post(rpc_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        result = response.json()
        if "result" in result:
            print("Wallet created successfully!")
        else:
            print("Error creating Monero wallet:", result.get("error", {}).get("message"))
    else:
        print("Error creating Monero wallet:", response.status_code)

def open_monero_wallet(wallet_name, wallet_password):
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": "0",
        "method": "open_wallet",
        "params": {
            "filename": wallet_name,
            "password": wallet_password
        }
    }
    response = requests.post(rpc_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        result = response.json()
        if "result" in result:
            print("Wallet opened successfully!")
            mnemonic = get_wallet_mnemonic(wallet_name, wallet_password)

        else:
            print("Error opening Monero wallet:", result.get("error", {}).get("message"))
    else:
        print("Error opening Monero wallet:", response.status_code)

def get_wallet_mnemonic(wallet_name, wallet_password):
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": "0",
        "method": "query_key",
        "params": {
            "key_type": "mnemonic",
            "key_data": {"name": wallet_name, "password": wallet_password}
        }
    }
    response = requests.post(rpc_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        result = response.json()
        if "result" in result:
            return result["result"]["key"]
        else:
            print("Error retrieving wallet mnemonic:", result.get("error", {}).get("message"))
    else:
        print("Error retrieving wallet mnemonic:", response.status_code)


def show_wallet_address(wallet_name, wallet_password):
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": "0",
        "method": "get_address",
        "params": {
            "account_index": 0,
            "address_index": 0,
            "wallet_name": wallet_name,
            "password": wallet_password
        }
    }
    response = requests.post(rpc_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        result = response.json()
        if "result" in result:
            address = result["result"]["address"]
            print("Wallet address:", address)
            return address
        else:
            print("Error retrieving wallet address:", result.get("error", {}).get("message"))
    else:
        print("Error retrieving wallet address:", response.status_code)

def create_new_address(wallet_name, wallet_password):
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": "0",
        "method": "create_address",
        "params": {
            "account_index": 0,
            "wallet_name": wallet_name,
            "password": wallet_password
        }
    }
    response = requests.post(rpc_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        result = response.json()
        if "result" in result:
            address = result["result"]["address"]
            return address
        else:
            print("Error creating new address:", result.get("error", {}).get("message"))
    else:
        print("Error creating new address:", response.status_code)



def get_wallet_balance(wallet_name, wallet_password):
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": "0",
        "method": "get_balance",
        "params": {
            "account_index": 0,
            "address_indices": [0],
            "wallet_name": wallet_name,
            "password": wallet_password
        }
    }
    response = requests.post(rpc_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        result = response.json()
        if "result" in result:
            balance = result["result"]["balance"]
            unlocked_balance = result["result"]["unlocked_balance"]

            balance_xmr = balance / 10 ** 12
            formatted_balance = "{:.12f}".format(balance_xmr)

            unlocked_balance_xmr = unlocked_balance / 10 ** 12
            formatted_unlocked_balance = "{:.12f}".format(unlocked_balance_xmr)

            return formatted_balance, formatted_unlocked_balance
        else:
            print("Error retrieving wallet balance:", result.get("error", {}).get("message"))
    else:
        print("Error retrieving wallet balance:", response.status_code)

#######################################################
#######################################################
#######################################################

if __name__ == '__main__':
    app.run(debug=True)