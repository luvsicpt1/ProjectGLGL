from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Initialize products list (consider using a database in production)
products = []
submissions = []


@app.route('/')
def home():
    return render_template('index.html', products=products)  # Added products to home route


@app.route('/catalog')
def catalog():
    return render_template('catalog.html', products=products)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Create new product dictionary
        new_product = {
            "name": request.form['name'],
            "price": request.form['price'],
            "size": request.form['size'],
            "image_url": request.form['image_url']
        }
        products.append(new_product)
        return redirect(url_for('admin'))  # Changed to redirect back to admin

    return render_template('admin.html', products=products)  # Added products to admin view


@app.route('/delete/<int:product_id>', methods=['POST'])  # New delete route
def delete_product(product_id):
    if 0 <= product_id < len(products):
        products.pop(product_id)
    return redirect(url_for('admin'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        submissions.append({
            "name": request.form['name'],
            "email": request.form['email'],
            "message": request.form['message']
        })
    return render_template('contact.html', submissions=submissions)


if __name__ == "__main__":
    app.run(debug=True)