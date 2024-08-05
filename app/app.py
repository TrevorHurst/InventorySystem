from flask import Flask, request, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parts.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecretkey'  # Required for flash messages
db = SQLAlchemy(app)

class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False, unique=True)
    serialno = db.Column(db.String(255), nullable=False)
    firmware = db.Column(db.String(80))
    functioning = db.Column(db.Boolean())
    notes = db.Column(db.String(255))
    holder_email = db.Column(db.String(320))
    holder_username = db.Column(db.String(80))
    holder_keybase = db.Column(db.String(80))

with app.app_context():
    def create_tables():
        db.create_all()

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of parts per page
    parts = Part.query.order_by(Part.name).paginate(page=page, per_page=per_page)
    return render_template('index.html', parts=parts)

@app.route('/create', methods=['GET', 'POST'])
def create_part():
    if request.method == 'POST':
        part = request.form['part']
        name = request.form['name']
        serialno = request.form['serialno']
        firmware = request.form.get('firmware')
        functioning = request.form.get('functioning') == 'on'
        notes = request.form.get('notes')
        holder_email = request.form.get('holder_email')
        holder_username = request.form.get('holder_username')
        holder_keybase = request.form.get('holder_keybase')

        new_part = Part(
            part=part,
            name=name,
            serialno=serialno,
            firmware=firmware,
            functioning=functioning,
            notes=notes,
            holder_email=holder_email,
            holder_username=holder_username,
            holder_keybase=holder_keybase
        )
        db.session.add(new_part)
        db.session.commit()
        flash('Part created successfully!')
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_part(id):
    part = Part.query.get_or_404(id)
    if request.method == 'POST':
        part.part = request.form['part']
        part.name = request.form['name']
        part.serialno = request.form['serialno']
        part.firmware = request.form.get('firmware')
        part.functioning = request.form.get('functioning') == 'on'
        part.notes = request.form.get('notes')
        part.holder_email = request.form.get('holder_email')
        part.holder_username = request.form.get('holder_username')
        part.holder_keybase = request.form.get('holder_keybase')

        db.session.commit()
        flash('Part updated successfully!')
        return redirect(url_for('index'))
    return render_template('edit.html', part=part)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_part(id):
    part = Part.query.get(id)
    db.session.delete(part)
    db.session.commit()
    flash('Part deleted successfully!')
    return redirect(url_for('index'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout_part():
    if request.method == 'POST':
        holder_email = request.form['holder_email']
        holder_username = request.form['holder_username']
        holder_keybase = request.form['holder_keybase']
        part_id = request.form['part_id']

        part = Part.query.get(part_id)
        if part and part.functioning:  # Ensure part is available
            part.holder_email = holder_email
            part.holder_username = holder_username
            part.holder_keybase = holder_keybase
            part.functioning = False  # Mark as checked out
            db.session.commit()
            flash('Success', 'success')
            return redirect(url_for('checkout_part'))  # Redirect to the list of parts

    parts = Part.query.order_by(Part.name).all()
    return render_template('checkout.html', parts=parts)


if __name__ == '__main__':
    app.run(debug=True)
