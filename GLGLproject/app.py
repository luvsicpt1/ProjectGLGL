from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
import uuid

app = Flask(__name__)
# ძალიან მნიშვნელოვანია გამოიყენოთ რთული და უსაფრთხო საიდუმლო გასაღები
app.secret_key = 'your-very-secret-and-secure-key-goes-here'

# --- ფაილების გზები ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE = os.path.join(BASE_DIR, 'products.json')
CONTACTS_FILE = os.path.join(BASE_DIR, 'contacts.json')
ADMIN_USER = 'GLGLadmin'
ADMIN_PASS = 'thispasswordisnoteasy' # წარმოებაში გამოიყენეთ გარემოს ცვლადები

# --- დამხმარე ფუნქციები მონაცემთა ბაზისთვის (JSON ფაილები) ---

def load_data(file_path):
    """ზოგადი ფუნქცია JSON ფაილიდან მონაცემების წასაკითხად."""
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_data(data, file_path):
    """ზოგადი ფუნქცია მონაცემების JSON ფაილში შესანახად."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def migrate_products_to_uuid():
    """ერთჯერადი ფუნქცია, რომელიც ანიჭებს უნიკალურ ID-ებს პროდუქტებს, რომლებსაც ის არ აქვთ."""
    products = load_data(PRODUCTS_FILE)
    migrated = False
    for product in products:
        if 'id' not in product:
            product['id'] = str(uuid.uuid4())
            migrated = True
    if migrated:
        save_data(products, PRODUCTS_FILE)
        print("Product ID migration complete.")

# --- ძირითადი გვერდები ---

@app.route('/')
def home():
    products = load_data(PRODUCTS_FILE)
    return render_template('index.html', products=products)

@app.route('/catalog')
def catalog():
    products = load_data(PRODUCTS_FILE)
    return render_template('catalog.html', products=products)

@app.route('/product/<string:product_id>')
def product_detail(product_id):
    """პროდუქტის დეტალური გვერდი."""
    products = load_data(PRODUCTS_FILE)
    product = next((p for p in products if p.get('id') == product_id), None)
    if product is None:
        flash('პროდუქტი ვერ მოიძებნა.', 'danger')
        return redirect(url_for('catalog'))
    return render_template('product_detail.html', product=product)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not name or not email or not message:
            flash('გთხოვთ, შეავსოთ ყველა ველი.', 'danger')
            return render_template('contact.html')

        contacts = load_data(CONTACTS_FILE)
        contacts.append({
            'id': str(uuid.uuid4()),
            'name': name,
            'email': email,
            'message': message
        })
        save_data(contacts, CONTACTS_FILE)
        flash('თქვენი შეტყობინება წარმატებით გაიგზავნა!', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')

# --- ადმინის ავტორიზაცია ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'admin' in session:
        return redirect(url_for('admin'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin'] = True
            flash('ავტორიზაცია წარმატებით დასრულდა.', 'success')
            return redirect(url_for('admin'))
        else:
            flash('მომხმარებლის სახელი ან პაროლი არასწორია.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash('თქვენ გამოხვედით სისტემიდან.', 'info')
    return redirect(url_for('home'))


# --- ადმინის პანელის გვერდები ---

def is_admin():
    """ამოწმებს, არის თუ არა მომხმარებელი ადმინი."""
    return 'admin' in session

@app.route('/admin')
def admin():
    if not is_admin():
        return redirect(url_for('login'))
    products = load_data(PRODUCTS_FILE)
    return render_template('admin.html', products=products)

@app.route('/admin/add', methods=['POST'])
def add_product():
    if not is_admin():
        return redirect(url_for('login'))

    products = load_data(PRODUCTS_FILE)
    new_product = {
        'id': str(uuid.uuid4()),
        'name': request.form.get('name'),
        'price': request.form.get('price'),
        'size': request.form.get('size'),
        'image_url': request.form.get('image_url')
    }
    products.append(new_product)
    save_data(products, PRODUCTS_FILE)
    flash('პროდუქტი წარმატებით დაემატა.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/edit/<string:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not is_admin():
        return redirect(url_for('login'))

    products = load_data(PRODUCTS_FILE)
    product = next((p for p in products if p.get('id') == product_id), None)
    if product is None:
        flash('პროდუქტი ვერ მოიძებნა.', 'danger')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        product['name'] = request.form.get('name')
        product['price'] = request.form.get('price')
        product['size'] = request.form.get('size')
        product['image_url'] = request.form.get('image_url')
        save_data(products, PRODUCTS_FILE)
        flash('პროდუქტი წარმატებით განახლდა.', 'success')
        return redirect(url_for('admin'))

    return render_template('edit.html', product=product)

@app.route('/admin/delete/<string:product_id>', methods=['POST'])
def delete_product(product_id):
    if not is_admin():
        return redirect(url_for('login'))

    products = load_data(PRODUCTS_FILE)
    products = [p for p in products if p.get('id') != product_id]
    save_data(products, PRODUCTS_FILE)
    flash('პროდუქტი წარმატებით წაიშალა.', 'success')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    migrate_products_to_uuid() # აპლიკაციის გაშვებისას ამოწმებს და ანიჭებს ID-ებს
    app.run(debug=True)

