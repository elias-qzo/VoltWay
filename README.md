# VoltWay

VoltWay est une application web qui permet d'anticiper un voyage en voiture 
électrique sans se soucier de l'autonomie de celle-ci. Les bornes de rechargement 
sont incluses automatiquement dans le trajet lorsque la batterie du véhicule atteint 
un seuil critique. VoltWay fonctionne avec un front web en Express.js, une API REST 
en Flask et une API SOAP en Flask.

---

# Documentation des API

[Documentation de l'API REST](api/doc/api_doc.md)
[Documentation de l'API SOAP](soap/doc/api_doc.md)

## Installation

### Prérequis
- [Node.js](https://nodejs.org/)
- [Python 3](https://www.python.org/)
- [pip](https://pip.pypa.io/en/stable/)
- [Git](https://git-scm.com/)

---

## Démarrage du projet

```bash
git clone https://github.com/elias-qzo/VoltWay.git
cd VoltWay
```

### Lancer l'API REST
```bash
cd api
pip install -r requirements.txt
python app.py
```

### Lancer l'API SOAP
```bash
cd soap
pip install -r requirements.txt
python app.py
```

### Lancer le frontend
```bash
cd web
npm start
```

---

## Technologies utilisées

### Backend
- Python (Flask) pour l'API REST et l'API SOAP
- Requests, Flask-RESTful, Spyne pour SOAP

### Frontend
- Express.js pour le serveur web
- HTML/CSS/JS pour l'interface utilisateur
- Axios pour les requêtes HTTP
