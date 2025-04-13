# Teollisuuden laitehallintarekisteri

## Käyttötarkoitus
Teollisuusyrityksissä on paljon laitteita, joille erilaiset lait, asetukset, laatujärjestelmät, valmistajien ohjeet yms. vaativat säännöllistä seurantaa ja ylläpitoa. Nostolaitteilla voi esimerkiksi olla pakollisia määräaikaistarkastuksia, mittalaitteilla ja siirtonormaaleilla kalibrointeja, tuotantokoneilla määräaikaishuoltoja, ja näiden vaatimusten ajantasalla pitäminen on työlästä. Sovellus toimii rekisterinä, johon talletetaan ensisijaisena tietona yrityksen kone tai laite uniikin koodin perusteella ja toissijaisena tietona laitteiden ylläpidon kannalta tarpeelliset tiedot.

## Sovelluksen tämänhetkinen tila, 30.3.2025

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.

- Käyttäjä näkee kaikki järjestelmään lisätyt laitteet ja niiden tiedot.

- Käyttäjä pystyy lisäämään rekisteriin laitteita ja muokkaamaan sekä päivittämään niiden tietoja.

- Kullekin laitteelle on liitetty vastuuhenkilö, joka on tällä hetkellä aina laitteen lisännyt käyttäjä. Omistajuuden siirtoa toiselle käyttäjälle ei ole vielä toteutettu.

- Käyttäjät voivat muokata ja päivittää muiden käyttäjien vastuulla olevien laitteiden tietoja, mutta kukin käyttäjä voi poistaa vain omalla vastuullaan olevan laitteen rekisteristä.

- Käyttäjä pystyy järjestämään laitelistaa seuraavilla parametreilla:
  - ID-numero 
  - laitetyyppi
  - laitteen valmistaja
  - laitteen malli
  - sijainti
  - laitteen tai sen määräaikaisten toimien tila
  - seuraava umpeutumassa oleva määräpäivä

- Listan suodatusta tai vapaasanahakua ei ole toteutettu.

- Tiedostojen ja raporttien lisäystä ei ole toteutettu.

- Kirjautumisen tarkistus on toteutettu suurimpaan osaan toiminnoista, ei välttämättä kuitenkaan kaikkiin.
- Syötteiden tarkistuksia tehdään, mutta ei välttämättä kaikkialla.

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
$ flask run
```
- Avaa sovellus selaimella osoitteessa http://127.0.0.1:5000.
- Tietokantaan on luotu valmiiksi testidataa ja kaksi testikäyttäjää. Voit kirjautua käyttäjätunnuksilla _testikäyttäjä_ tai _testikäyttäjä2_, käyttäen salasanaa _salasana_. Voit halutessasi luoda myös uuden käyttäjän.

- Mikäli haluat aloittaa käytön tyhjällä tietokannalla, poista projektihakemistosta tietokantatiedosto /database/database.db, luo se uudestaan tyhjänä tiedostona ja alusta tietokanta skeeman pohjalta seuraavalla komennolla:
```
$ sqlite3 database.db < schema.sql
```
