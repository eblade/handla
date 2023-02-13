# Handla

Familjens handlingslista. Mjukvara på svenska.

![image](https://user-images.githubusercontent.com/840259/217183341-97484a2a-a0a6-4a50-be54-a988aa7e504b.png)
![image](https://user-images.githubusercontent.com/840259/217183465-cbaffc5f-5579-4683-8e8f-4032b8d9c14c.png)
![image](https://user-images.githubusercontent.com/840259/217183594-bd83cd09-67e4-420e-aa28-ab9df04bc66a.png)


## Finesser

* Kategoriserade varor, sortering efter hur de kategorierna ligger på vår närmaste Willy's
* Lagga till/ta bort/flytta varor
* Supersäkert med hjälp av hemligt token i url:en
* Man kan tillfälligt kommentera varor
* Ångra att bocka av en vara
* Sök bland varor
* Live-uppdateringar via websocket

## Krav

För bakändan:

- Python 3.6 eller senare
- requirements.txt (fastapi, jinja2 och uvicorn[standard])

För webb-delen:

- JavaScript, HTML och CSS
- Testade browsers: Firefox (desktop/android), Chrome (android), Badwolf, Qutebrowser, Edge
- npm och veckans ramverk? Nope, behövs inte.

## Installation med venv, nginx och systemd

I mappen för utchecking av `handla`, som rimligen ligger i hemkatalogen för användaren som ska köra appen som daemon (heter "mat" i examplen):

```bash
python -m venv venv
. venv/bin/activate
pip install --update pip  # krävs om du kör standard python3.6
pip install -r requirements.txt
echo hemligt_token > token

# nu kan man testa att starta appen med
uvicorn handla:app
```

Sen kan man kopiera `mat.service`, ändra lite sökvägar efter behag, köra de selinux-kommandon som finns där och lägga den i `/etc/systemd/system/`. Sen kör man som `root`:

```bash
systemctl enable mat
systemctl start mat
systemctl status mat

# om det ser illa ut, kolla loggen:
journalctl -u mat
```
Notera att appen förväntar sig att arbetskatalogen är samma som utcheckningen för själva appen.

Om det ser ut att funka, kasta in `nginx`-configen från service-filen vet ja. Set upp letsencrypt med certbot och peka om din domän. Sen besöker du bara först `https://example.com/s/hemligt_token/bootstrap` för att lägga in lite startdata och sen `https://example.com/s/hemligt_token/index.html` för att komma till själva appen.

## Kan man köra den i docker?

Säkert.

## Var lagras datan?

I en blockkedja med AI. Nej :) i en sqlite3-databas i filen `handla.db`.

Om du vill backa upp kan du säkerhetskopiera den filen, eller göra `GET` på `/s/hemligt_token/itm-by-cat` och spara undan den fina JSON-filen du får då. Det finns i nuläget inget sätt att restaurera den så det är väl som backupper mest är antar jag.
