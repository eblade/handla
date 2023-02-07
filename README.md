# Handla

Familjens handlingslista. Mjukvara på svenska.

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

I en blockkedja med AI. Nej :) i en sqlite3-database i filen `handla.db`.
