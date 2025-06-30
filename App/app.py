from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import re
from pymongo import MongoClient


app = Flask(__name__)
app.secret_key = 'UDLA_SECRET'

# Conexión MongoDB: especificar la base de datos CATEQUESIS
app.config["MONGO_URI"] = "mongodb+srv://admin:udla@cluster0.ysc08sf.mongodb.net/CATEQUESIS?retryWrites=true&w=majority"
mongo = PyMongo(app)

# ======== RUTAS PRINCIPALES ========

@app.route('/')
def index():
    catequizandos = mongo.db.catequizando.find()
    return render_template('index.html', catequizandos=catequizandos)

@app.route('/registro', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        cedula = request.form['cedula']
        
        # Validaciones
        if not re.fullmatch(r'\d{10}', cedula):
            flash('La cédula debe tener exactamente 10 dígitos.', 'danger')
            return redirect(url_for('crear'))
        
        if mongo.db.catequizando.find_one({'cedula': cedula}):
            flash('Ya existe un catequizando con esa cédula.', 'danger')
            return redirect(url_for('crear'))

        catequizando = {
            'nombre': request.form['nombre'],
            'fecha_nac': request.form['fecha_nac'],
            'cedula': cedula,
            'direccion': request.form['direccion'],
            'parroquia_id': request.form['parroquia_id'],
            'representantes': [
                {
                    'nombre': request.form['rep_nombre'],
                    'parentesco': request.form['rep_parentesco'],
                    'telefono': request.form['rep_telefono']
                }
            ]
        }

        mongo.db.catequizando.insert_one(catequizando)
        flash("Registro creado exitosamente", "success")
        return redirect(url_for('index'))

    return render_template('registro.html')

@app.route('/editar/<id>', methods=['GET', 'POST'])
def editar(id):
    catequizando = mongo.db.catequizando.find_one({"_id": ObjectId(id)})

    # Asegura que siempre exista el campo 'representantes' con al menos un elemento
    if not catequizando.get('representantes') or not isinstance(catequizando['representantes'], list) or len(catequizando['representantes']) == 0:
        catequizando['representantes'] = [{
            'nombre': '',
            'parentesco': '',
            'telefono': ''
        }]

    if request.method == 'POST':
        cedula = request.form['cedula']

        # Validación de cédula duplicada (excluyendo al actual)
        if not re.fullmatch(r'\d{10}', cedula):
            flash('La cédula debe tener exactamente 10 dígitos.', 'danger')
            return redirect(url_for('editar', id=id))

        cedula_existente = mongo.db.catequizando.find_one({'cedula': cedula, '_id': {'$ne': ObjectId(id)}})
        if cedula_existente:
            flash('Ya existe un catequizando con esa cédula.', 'danger')
            return redirect(url_for('editar', id=id))

        nuevos_datos = {
            'nombre': request.form['nombre'],
            'fecha_nac': request.form['fecha_nac'],
            'cedula': cedula,
            'direccion': request.form['direccion'],
            'parroquia_id': request.form['parroquia_id'],
            'representantes': [
                {
                    'nombre': request.form['rep_nombre'],
                    'parentesco': request.form['rep_parentesco'],
                    'telefono': request.form['rep_telefono']
                }
            ]
        }

        mongo.db.catequizando.update_one({'_id': ObjectId(id)}, {'$set': nuevos_datos})
        flash("Registro actualizado exitosamente", "info")
        return redirect(url_for('index'))

    return render_template('editar.html', catequizando=catequizando)

@app.route('/eliminar/<id>', methods=['POST'])
def eliminar(id):
    mongo.db.catequizando.delete_one({'_id': ObjectId(id)})
    flash("Registro eliminado correctamente", "warning")
    return redirect(url_for('index'))

# ========= EJECUCIÓN =========
if __name__ == '__main__':
    print("Servidor ejecutándose en http://127.0.0.1:5000")
    app.run(debug=True)
    app.run(debug=True)
