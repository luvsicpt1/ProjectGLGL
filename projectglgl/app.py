from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

products = [
    {"name": "Kitchen Set", "price": "100$", "size": "Medium", "image_url": "https://via.placeholder.com/150"},
    {"name": "Cooking Pan", "price": "30$", "size": "Large", "image_url": "https://via.placeholder.com/150"},
    {"name": "Knife Set", "price": "50$", "size": "Small", "image_url": "https://via.placeholder.com/150"}
]


submissions = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/catalog')
def catalog():
    return render_template('catalog.html', products=products)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        size = request.form['size']
        image_url = request.form['image_url']

        products.append({"name": name, "price": price, "size": size, "image_url": image_url})
        return redirect(url_for('catalog'))

    return render_template('admin.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        submissions.append({
            "name": name,
            "email": email,
            "message": message
        })

    return render_template('contact.html', submissions=submissions)

if __name__ == "__main__":
    app.run(debug=True)

