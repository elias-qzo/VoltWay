# Documentation de l'API REST

### Requête GET : Ajouter un trajet

**Endpoint** : `/itinerary`

**Méthode** : `GET`

**Description** : Récupère un trajet avec les bornes de rechargement incluses

**Exemple de requête** :

```json
{
  "origin": "Paris",
  "destination": "Chambéry",
  "autonomy": 300,
  "load_time": 50,
}
```

**Exemple de réponse** :

```json
{
	"bbox": [
		2.305902,
		45.55384,
		5.921076,
		48.858894
	],
	"summary": {
		"distance": 579237.0,
		"duration": 22802.0,
		"cost": 225.0
	},
	"waypoints": [
		[
			2.32003,
			48.85889
		],
        [
			2.31984,
			48.85864
		]
        ],
    "charging_stations": [
		[
			2.99276544367632,
			48.199541641152
		],
        [
			3.87812852535507,
			47.665130689367
		]
    ]
}
```

---

### Requête GET : Véhicules

**Endpoint** : `/vehicles`

**Méthode** : `GET`

**Description** : Récupère les informations d'un véhicule à partir d'une marque

**Exemple de requête** :

```json
{
  "brand": "Tesla"
}
```

**Exemple de réponse** :

```json
[
	{
		"brand": "Tesla",
		"model": "Model S",
		"autonomy": 323,
		"image": "https://cars.chargetrip.io/5f1aafdb657beb44c4638991.png",
		"charge-time": 38
	},
	{
		"brand": "Tesla",
		"model": "Model Y",
		"autonomy": 404,
		"image": "https://cars.chargetrip.io/61fa2f5170d2c0b3b340dbb0.png",
		"charge-time": 27
	}
]
```
