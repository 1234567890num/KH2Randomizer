from randomize import Randomize
from flask import Flask
from locationClass import worlds
from randomCmdMenu import cmdMenusChoice
import flask as fl
import numpy as np
import zipfile
import base64
import string
import random

app = Flask(__name__)

expTypes = ["Sora","Valor","Wisdom","Limit","Master","Final"]


@app.route('/')
def index():
    return fl.render_template('index.html', worlds = worlds, expTypes = expTypes)


@app.route('/seed/<hash>')
def hashedSeed(hash):
    argsString = base64.urlsafe_b64decode(hash)
    
    return fl.redirect("/seed?"+str(argsString).replace("b'","").replace("'",""))

@app.route('/seed')
def seed():
    seed = fl.escape(fl.request.args.get("seed")) or ""
    if seed == "":
        characters = string.ascii_letters + string.digits

        seed = (''.join(random.choice(characters) for i in range(30)))

        return fl.redirect("/seed?"+str(fl.request.query_string).replace("seed=&","seed="+seed+"&").replace("b'","").replace("'",""))

    includeList = fl.request.args.getlist("include") or []

    formExpMult = {
        1: fl.request.args.get("ValorExp"), 
        2: fl.request.args.get("WisdomExp"), 
        3: fl.request.args.get("LimitExp"), 
        4: fl.request.args.get("MasterExp"), 
        5: fl.request.args.get("FinalExp")
        }

    soraExpMult = fl.request.args.get("SoraExp")

    levelChoice = fl.request.args.get("levelChoice")

    queryString = fl.request.query_string
    hashedString = base64.urlsafe_b64encode(queryString)

    permaLink = fl.url_for('hashedSeed', hash = hashedString,_external=True)

    return fl.render_template('seed.html', 
    permaLink = permaLink.replace("'",""), 
    cmdMenus = cmdMenusChoice, 
    levelChoice = levelChoice, 
    include = includeList, 
    seed = seed, 
    worlds=worlds, 
    expTypes = expTypes, 
    formExpMult = formExpMult, 
    soraExpMult = soraExpMult)

@app.route('/download')
def randomizePage():
    includeList = fl.request.args.getlist("include") or []
    excludeList = list(set(worlds) - set(includeList))
    levelChoice = fl.request.args.get("levelChoice")
    cmdMenuChoice = fl.request.args.get("cmdMenuChoice")
    seed = fl.request.args.get('seed') or ""

    formExpMult = {
        1: float(fl.request.args.get("ValorExp")), 
        2: float(fl.request.args.get("WisdomExp")), 
        3: float(fl.request.args.get("LimitExp")), 
        4: float(fl.request.args.get("MasterExp")), 
        5: float(fl.request.args.get("FinalExp"))
        }

    soraExpMult = float(fl.request.args.get("soraExpMult"))

    data = Randomize(
    seedName = fl.escape(seed), 
    exclude = excludeList, 
    formExpMult=formExpMult, 
    soraExpMult=soraExpMult, 
    levelChoice = levelChoice, 
    cmdMenuChoice=cmdMenuChoice
    )

    if isinstance(data,str):
        return data

    return fl.send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='randoseed.zip'
    )

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
    
if __name__ == '__main__':
    dataOut = Randomize(exclude=["LingeringWill","Level","FormLevel"], cmdMenuChoice="randAll")
    f = open("randoSeed.zip", "wb")
    f.write(dataOut.read())
    f.close()