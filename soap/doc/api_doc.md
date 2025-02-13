# Documentation de l'API SOAP

## Requête Temps et coût

**Endpoint** : `/get_time_cost`  

### Structure de la requête

```xml
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="voltway.soap">
    <soap:Header/>
    <soap:Body>
        <ns:get_time_cost>
            <ns:distance>795938.0</ns:distance>
            <ns:baseTime>31830.8</ns:baseTime>
            <ns:loadTime>30</ns:loadTime>
            <ns:autonomy>100</ns:autonomy>
        </ns:get_time_cost>
    </soap:Body>
</soap:Envelope>
```

### Paramètres de la requête

| Paramètre   | Type    | Obligatoire | Description |
|-------------|--------|------------|-------------|
| `distance`  | `float` | Oui | Distance du trajet en mètres. |
| `baseTime`  | `float` | Oui | Temps de trajet de base en secondes. |
| `loadTime`  | `int`   | Oui | Temps de recharge estimé en minutes. |
| `autonomy`  | `int`   | Oui | Autonomie du véhicule en kilomètres. |

---

## Réponse

### Structure de la réponse

```xml
<?xml version='1.0' encoding='UTF-8'?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="voltway.soap">
    <soap:Body>
        <tns:get_time_costResponse>
            <tns:get_time_costResult>
                <tns:time>32040</tns:time>
                <tns:cost>315.0</tns:cost>
            </tns:get_time_costResult>
        </tns:get_time_costResponse>
    </soap:Body>
</soap:Envelope>
```

### Paramètres de la réponse

| Paramètre | Type    | Description |
|-----------|--------|-------------|
| `time`    | `int`  | Temps total estimé du trajet en secondes. |
| `cost`    | `float` | Coût estimé du trajet en euros. |

---

## Exemple d'utilisation

### Requête

```xml
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="voltway.soap">
    <soap:Body>
        <ns:get_time_cost>
            <ns:distance>500000</ns:distance>
            <ns:baseTime>20000</ns:baseTime>
            <ns:loadTime>20</ns:loadTime>
            <ns:autonomy>120</ns:autonomy>
        </ns:get_time_cost>
    </soap:Body>
</soap:Envelope>
```

### Réponse

```xml
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="voltway.soap">
    <soap:Body>
        <tns:get_time_costResponse>
            <tns:get_time_costResult>
                <tns:time>20500</tns:time>
                <tns:cost>250.0</tns:cost>
            </tns:get_time_costResult>
        </tns:get_time_costResponse>
    </soap:Body>
</soap:Envelope>
```

---
