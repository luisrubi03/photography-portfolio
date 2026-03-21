import flask from flask
app = flask.Flask(__name__)
@app.route(´/´)

def index():
    return flask.render_template('index.html')
if __name__ == '__main__':
    app.run()

def main():

#funcion para poder acceder a tu cuenta
def account('/account'):
    return flask.render_template('account.html')

#acerca de mi mas detallado
def about('/about'):
    return flask.render_template('about.html')

#funcion para poder subir tus fotografias sin necesidad de actualizar el codigo
def load('/load'):
    return flask.render_template('load.html')
