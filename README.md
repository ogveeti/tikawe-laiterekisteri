# Teollisuuden laitehallintarekisteri

## Käyttötarkoitus
Teollisuusyrityksissä on paljon laitteita, joille erilaiset lait, asetukset, laatujärjestelmät, valmistajien ohjeet yms. vaativat säännöllistä seurantaa ja ylläpitoa. Nostolaitteilla voi esimerkiksi olla pakollisia määräaikaistarkastuksia, mittalaitteilla ja siirtonormaaleilla kalibrointeja, tuotantokoneilla määräaikaishuoltoja, ja näiden vaatimusten ajantasalla pitäminen on työlästä. Sovellus toimii rekisterinä, johon talletetaan ensisijaisena tietona yrityksen kone tai laite uniikin koodin perusteella ja toissijaisena tietona laitteiden ylläpidon kannalta tarpeelliset tiedot.

## Sovelluksen tämänhetkinen tila, 13.4.2025

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen. Kirjautumiset tarkistetaan sivuilla.

- Käyttäjä näkee kaikki järjestelmään lisätyt laitteet ja niiden tiedot.

- Käyttäjä pystyy lisäämään rekisteriin laitteita ja muokkaamaan sekä päivittämään niiden tietoja.

- Kullekin laitteelle on liitetty vastuuhenkilö, joka on tällä hetkellä aina laitteen lisännyt käyttäjä. Omistajuuden siirtoa toiselle käyttäjälle ei ole vielä toteutettu.

- Käyttäjät voivat muokata ja päivittää muiden käyttäjien vastuulla olevien laitteiden tietoja, mutta kukin käyttäjä voi poistaa vain omalla vastuullaan olevan laitteen rekisteristä.

- Käyttäjä pystyy lähettämään toisen käyttäjän tietokohteeseen lisätietoa, joskin vapaata tekstitietokenttää kommenteille tai raporteille ei ole vielä tehty.

- Käyttäjä pystyy järjestämään laitelistaa seuraavilla parametreilla:
  - ID-numero 
  - laitetyyppi
  - laitteen valmistaja
  - laitteen malli
  - sijainti
  - laitteen tai sen määräaikaisten toimien tila
  - seuraava umpeutumassa oleva määräpäivä
  
- Tietokohteet luokitellaan ja luokitukset on tallennettu tietokantaan.

- Sovelluksessa on käyttäjähallinta, joka listaa rekisteröidyt käyttäjät ja heidän vastuulla olevat laitemäärät.

- Kullekin käyttäjälle on käyttäjäsivu, jota kautta voi hakea käyttäjän vastuulla olevat laitteet ja joka näyttää käyttäjän viimeisimmän kirjautumisajankohdan.

- Suurin osa syötteistä tarkistetaan selaimessa ja palvelimella, tosin pituuksia ei ole vielä rajoitettu.

- Käyttäjän aiheuttamat virheilmoitukset näytetään samalla sivulla, joskin lomakkeiden ja muiden tietokenttien tarkistus tapahtuu vielä yksi kerrallaan. Virheiden tarkistusta ja näyttöä kerralla ei ole toteutettu. 

- Listojen suodatusta tai vapaasanahakua ei ole toteutettu.
  
- Tiedostojen ja raporttien lisäystä ei ole toteutettu.

## Käyttöohjeet testausta varten
- Kloonaa projekti omalle tietokoneelle, tietokoneella tulee olla asennettuna Python 3 ja pip.
- Navigoi projektihakemiston juureen, luo projektille kurssimateriaalin mukaisesti virtuaaliympäristö komennolla:
```
$ python3 -m venv venv
```
- Käynnistä virtuaaliympäristö komennolla:
```
$ source venv/bin/activate
```
- Asenna Flask virtuaaliympäristöön komennolla:
```
$ pip install flask
```
- Käynnistä sovellus komennolla:
```
$ flask --app app run
```
- Avaa sovellus selaimella osoitteessa http://127.0.0.1:5000.
- Tietokantaan on luotu valmiiksi testidataa ja kaksi testikäyttäjää. Voit kirjautua käyttäjätunnuksilla _testikäyttäjä_ tai _testikäyttäjä2_, käyttäen salasanaa _salasana_. Voit halutessasi luoda myös uuden käyttäjän.

- Mikäli haluat aloittaa käytön tyhjällä tietokannalla, poista projektihakemistosta tietokantatiedosto /database/database.db, luo se uudestaan tyhjänä tiedostona ja alusta tietokanta skeeman pohjalta seuraavalla komennolla:
```
$ sqlite3 database.db < schema.sql
```
