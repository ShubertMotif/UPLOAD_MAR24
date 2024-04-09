import os
import schedule
import time
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import requests
from datetime import timedelta, datetime
from tronpy import Tron



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'DATA', 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'il_tuo_valore_segreto'

db = SQLAlchemy(app)

# Assicurati di configurare il client per connettersi alla rete desiderata (mainnet, shasta testnet, ecc.)
client = Tron(network="nile", conf={'fee_limit':10_000_000})

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    monero_wallet = db.Column(db.String(255), nullable=True)
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

        open_monero_wallet(self.XMR_name, 'password_offerta')
        balance_XMR_offerta, unlocked_balance_XMR_offerta = get_wallet_balance(self.XMR_name, 'password_offerta')

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


def get_xmr_price():
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


def update():
    with app.app_context():
        photos = Photo.query.all()
        xmr_price = get_xmr_price()  # Ottieni il prezzo di Monero (XMR)


        for photo in photos:
            price_eur = photo.price_eur
            price_monero = price_eur / xmr_price
            photo.price_monero = price_monero

        offerte = Offerta.query.all()  # Recupera tutte le offerte dal database
        for offerta in offerte:
            try:
                # Supponendo di avere un'istanza client TRON configurata come `client_tron`
                bilancio = client.get_account_balance(offerta.indirizzo_usdt_offerta)
                print(f"Bilancio per {offerta.indirizzo_usdt_offerta}: {bilancio} USDT")
            except Exception as e:
                print(f"Errore nel recuperare il bilancio per {offerta.indirizzo_usdt_offerta}: {str(e)}")

        db.session.commit()
        print(f"Ho aggiornato il database. Prezzo XMRUSDT = {xmr_price}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    # Schedula l'esecuzione di update_monero_prices() ogni minuto
    schedule.every(1).minutes.do(update)

    while True:
        schedule.run_pending()
        time.sleep(1)
