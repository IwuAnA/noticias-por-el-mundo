from flask import Flask, render_template, request, redirect, session
import requests

from flask_sqlalchemy import SQLAlchemy


usuario = ""
app = Flask(__name__)


app.secret_key = 'my_secret_key'  # Necesario para las sesiones


# Conectando SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Creando una base de datos
db = SQLAlchemy(app)
# Creación de una tabla

class Card(db.Model):
    # Creación de columnas
    # id
    id = db.Column(db.Integer, primary_key=True)
    # Título
    title = db.Column(db.String(100), nullable=False)
    # Descripción
    subtitle = db.Column(db.String(300), nullable=False)
    # Texto
    text = db.Column(db.Text, nullable=False)

    # Salida del objeto y del id
    def __repr__(self):
        return f'<Card {self.id}>'
    

#Asignación #2. Crear la tabla Usuario
class User(db.Model):
    # Creación de las columnas
    # id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(100), nullable=False) 

    email = db.Column(db.String(100), nullable=False)

    password = db.Column(db.String(100), nullable=False)


API_KEY = "f3798e116eb342b2bae58e7f0cbd9c11"
CANTIDAD_NOTICIAS = 8


def fetch_noticias_from_api(categoria, cantidad=CANTIDAD_NOTICIAS):
    try:
        url = f"https://newsapi.org/v2/everything?q={categoria}&language=es&apiKey={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        noticias = data.get("articles", [])[:cantidad]
        return [
            {
                "title": noticia.get("title"),
                "image": noticia.get("urlToImage", "../static/img/default_image.jpg"),
                "date": noticia.get("publishedAt", "").split("T")[0],
                "source": noticia.get("source", {}).get("name"),
                "url": noticia.get("url"),
            }
            for noticia in noticias
        ]
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener noticias: {e}")
        return []


@app.route("/", methods=["GET"])
def index():
    # Parámetros para la lógica
    categoria = request.args.get("categoria", "tecnología")
    offset = int(request.args.get("offset", 0))  # Noticias ya cargadas
    cantidad = offset + CANTIDAD_NOTICIAS  # Total de noticias a obtener
    show_sidebar = request.args.get("show_sidebar") == "True"  # Mostrar barra lateral
    close_sidebar = request.args.get("close_sidebar") == "True"  # Cerrar barra lateral

    # Actualizar estado de la barra lateral
    if close_sidebar:
        show_sidebar = False

    # Obtener noticias desde la API
    noticias = fetch_noticias_from_api(categoria, cantidad)

    # Renderizar la plantilla con datos
    return render_template(
        "index.html",
        noticias=noticias[:cantidad],  # Asegurar número exacto de noticias
        offset=cantidad,               # Actualizar el offset
        categoria=categoria,           # Categoría actual
        show_sidebar=show_sidebar,      # Estado de la barra lateral
    )



@app.route("/ayuda", methods=["GET"])
def ayuda():
    return render_template("help.html")

@app.route("/login", methods=["GET","POST"])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['name']
        form_login = request.form['email']
        form_password = request.form['password']
        
        #Asignación #4. Aplicar la autorización
        users_db = User.query.all()

        for user in users_db:
            if form_login == user.email and form_password == user.password:
                global usuario
                session['usuario'] = user.name  # Guardar el nombre del usuario en la sesión
                print(f"Usuario {user.name} ha iniciado sesión.")  # Línea de depuración
                return redirect('/')
        else:
            error = 'Nombre de usuario o contraseña incorrectos'
        return render_template('login.html', error=error)
                     
    else:
        return render_template('login.html') 

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('usuario', None)  # Eliminar el nombre del usuario de la sesión
    return redirect("/")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email= request.form['email']
        password = request.form['password']
        
        #Asignación #3. Hacer que los datos del usuario se registren en la base de datos.
        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        
        return redirect('/login')
    
    else:    
        return render_template('register.html') 
    
@app.route('/discord', methods=["GET"])
def discord():
    return render_template("discord.html")


if __name__ == "__main__":
    app.run(debug=True)