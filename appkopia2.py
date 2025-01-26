from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
import sqlite3
from email.mime.image import MIMEImage
import os
import random
import string
def generate_game_key(length=16):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

app = Flask(__name__)
app.secret_key = 'sekret'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sklepmoregames@gmail.com'
app.config['MAIL_PASSWORD'] = 'nfbezgnxbamebijt'

mail = Mail(app)

# Funkcja inicjalizująca bazę danych
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Tabela produktów
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL)')

    # Tabela kluczy do gier
    c.execute('CREATE TABLE IF NOT EXISTS keys (id INTEGER PRIMARY KEY, product_id INTEGER, game_key TEXT, is_used INTEGER DEFAULT 0, FOREIGN KEY(product_id) REFERENCES products(id))')

    # Tabela zamówień
    c.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, email TEXT, products TEXT, keys TEXT, shipping_address TEXT)')

    # Dodaj przykładowe produkty, jeśli baza jest pusta
    c.execute('SELECT COUNT(*) FROM products')
    if c.fetchone()[0] == 0:
        products = [
            ("CS GO", 35),
            ("Diablo IV", 215),
            ("Elden Ring", 249),
            ("Farming Simulator 25", 231),
            ("Fortnite", 2137),
            ("GTA", 129),
            ("Hogwarts Legacy", 269),
            ("Minecraft", 99),
            ("Roblox", 1),
            ("Terraria", 45),
            ("The Sims 4", 1000),
            ("Wiedźmin", 99),
            ("Cyberpunk", 200),
            ("Space Engineers", 15),
            ("Fallout 4", 49),
            ("The forest", 31),
            ("Raft", 46),
            ("Crossout", 121),
            ("War thunder", 68),
            ("CS2", 9),
            ("Stardew valley", 10),
            ("Stalker", 450),
            ("Red dead redemption II", 311),
            ("Euro truck simulator 2", 72),
        ]
        for name, price in products:
            c.execute('INSERT INTO products (name, price) VALUES (?, ?)', (name, price))

        # Dodanie przykładowych kluczy do produktów
        keys = [
    (1, generate_game_key()), (1, generate_game_key()),
    (2, generate_game_key()), (2, generate_game_key()),
    (3, generate_game_key()), (3, generate_game_key()),
    (4, generate_game_key()), (4, generate_game_key()),
    (5, generate_game_key()), (5, generate_game_key()),
    (6, generate_game_key()), (6, generate_game_key()),
    (7, generate_game_key()), (7, generate_game_key()),
    (8, generate_game_key()), (8, generate_game_key()),
    (9, generate_game_key()), (9, generate_game_key()),
    (10, generate_game_key()), (10, generate_game_key()),
    (11, generate_game_key()), (11, generate_game_key()),
    (12, generate_game_key()), (12, generate_game_key()),
    (13, generate_game_key()), (13, generate_game_key()),
    (14, generate_game_key()), (14, generate_game_key()),
    (15, generate_game_key()), (15, generate_game_key()),
    (16, generate_game_key()), (16, generate_game_key()),
    (17, generate_game_key()), (17, generate_game_key()),
    (18, generate_game_key()), (18, generate_game_key()),
    (19, generate_game_key()), (19, generate_game_key()),
    (20, generate_game_key()), (20, generate_game_key()),
    (21, generate_game_key()), (21, generate_game_key()),
    (22, generate_game_key()), (22, generate_game_key()),
    (23, generate_game_key()), (23, generate_game_key()),
    (24, generate_game_key()), (24, generate_game_key())
]
        for product_id, game_key in keys:
            c.execute('INSERT INTO keys (product_id, game_key) VALUES (?, ?)', (product_id, game_key))

    conn.commit()
    conn.close()

@app.route('/', methods=['GET'])
def index():
    # Pobranie zapytania wyszukiwania z formularza
    search_query = request.args.get('search', '')  # Domyślnie puste, jeśli brak zapytania
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Jeśli zapytanie wyszukiwania jest obecne, filtrujemy gry
    if search_query:
        c.execute('SELECT * FROM products WHERE name LIKE ?', ('%' + search_query + '%',))
    else:
        c.execute('SELECT * FROM products')  # Pobierz wszystkie produkty, jeśli brak zapytania
    
    products = c.fetchall()  # Pobierz wyniki
    conn.close()  # Zamknięcie połączenia z bazą danych
    
    return render_template('index.html', products=products)  # Zwróć widok z produktami




@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    session.modified = True
    flash("Produkt został dodany do koszyka!")
    return redirect(url_for('index'))


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session and str(product_id) in session['cart']:
        cart = session['cart']
        if cart[str(product_id)] > 1:
            cart[str(product_id)] -= 1
        else:
            del cart[str(product_id)]
        session['cart'] = cart
        session.modified = True
        flash("Produkt został usunięty z koszyka!")
    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    cart = session.get('cart', {})
    products = []
    for product_id, quantity in cart.items():
        c.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = c.fetchone()
        if product:
            products.append({
                'id': product[0],
                'name': product[1],
                'price': product[2],
                'quantity': quantity
            })
    conn.close()
    return render_template('cart.html', products=products)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('cart'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    product_names = []
    total_price = 0
    for product_id, quantity in cart.items():
        c.execute('SELECT name, price FROM products WHERE id = ?', (product_id,))
        result = c.fetchone()
        if result:
            product_names.append(f"{result[0]} (x{quantity})")
            total_price += result[1] * quantity
    conn.close()

    if request.method == 'POST':
        email = request.form['email']
        shipping_address = request.form['shipping_address']
        session['email'] = email
        session['shipping_address'] = shipping_address
        return redirect(url_for('checkout_summary'))
    return render_template('checkout.html', products=product_names, total_price=total_price)


@app.route('/checkout/summary', methods=['GET', 'POST'])
def checkout_summary():
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('cart'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    product_keys = {}
    product_names = []
    total_price = 0

    for product_id, quantity in cart.items():
        c.execute('SELECT name, price FROM products WHERE id = ?', (product_id,))
        product = c.fetchone()
        if product:
            product_names.append(f"{product[0]} (x{quantity})")
            total_price += product[1] * quantity

            # Pobierz unikalne klucze dla produktu
            c.execute('SELECT game_key FROM keys WHERE product_id = ? AND is_used = 0 LIMIT ?', (product_id, quantity))
            keys = c.fetchall()
            if len(keys) < quantity:
                flash("Brak wystarczającej liczby kluczy dla produktu!")
                return redirect(url_for('cart'))
            product_keys[product[0]] = [key[0] for key in keys]

            # Oznacz klucze jako użyte
            c.executemany('UPDATE keys SET is_used = 1 WHERE game_key = ?', keys)

    conn.commit()
    conn.close()

    email = session.get('email')
    shipping_address = session.get('shipping_address')

    if email:
        try:
            key_details = "\n".join([f"{name}: {', '.join(keys)}" for name, keys in product_keys.items()])
            message = Message(
                subject="Twoje zamówienie - Podsumowanie",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email],
                body=f"""Dziękujemy za zamówienie!

Zakupione produkty:
{', '.join(product_names)}

Klucze:
{key_details}

Łączna cena: {total_price} zł
Zakupione przez {shipping_address}

Pozdrawiamy,

-More Games!
                """
            )
            
            mail.send(message)

            flash("Zamówienie zostało wysłane na e-mail!")

            # Opróżnij koszyk po złożeniu zamówienia
            session.pop('cart', None)
        except Exception as e:
            flash(f"Wystąpił błąd podczas wysyłania e-maila: {e}")

    return render_template('checkout_summary.html', 
                           products=product_names, 
                           keys=product_keys, 
                           total_price=total_price,
                           email=email,
                           shipping_address=shipping_address)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
