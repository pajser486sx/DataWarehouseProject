# Data mining project / skladišta i rudarenje podataka - Spotify data warehouse
## 1. dio - odabir dataseta
Odabrani dataset je UserBehaviour.csv koji se nalazi u mapi data. <br>
Sadrži podatke o različitim Spotify korisnicima. U datasetu se može vidjeti iz koje su države korisnici, koliko često na dan preskaću pjesme, koje značajke aplikacije im se sviđaju, koji uređaj koriste za slušanje te još mnogo drugih podataka (raw CVS ima 18 stupaca).
<hr>

## 2. dio - predprocesiranje, ETL
Sve za 2. dio nalazi se unutar 2ndCheckpoint mape. Izvršava se čišćenje podataka. Raw dataset se dijeli na 2 dijela, jedan sadrži 80% podataka, dok drugi sadrži preostalih 20% podataka. Podaci se prenose u relacijsku bazu podataka (MySQL). Baza dobiva naziv spotify_dw te se puni sa podacima iz UserBehaviour_PROCESSED.csv, koja sadrži 80%-tni dio svih podataka. 
<hr>

## 3. dio - kreiranje dimenzijskog modela
Kreiraju se 4 dimemnzije iz naših podataka i jedna tablica činjenica (vidi sliku StarSchema.png). Podaci iz spotify_dw se transformiraju i sa njima se pune dimenzijske tablice i tablica činjenica (dimenzijski.py).
<hr>

## 4. dio - Završni ETL - spajanje dva različita izvora podataka
Struktura datoteka: <br>
<b>Mapa "extract"</b> <br>
Sadrži datoteke extract_csv.py i extract_mysql.py <br>
<b>Mapa "load"</b> <br>
Sadrži datoteku run_loading.py <br>
<b>Mapa "transform", u kojoj su mape "dimensions" i "facts"</b>
Datoteka u transform: pipeline.py <br>
Datoteke u dimensions: DimCountry.py, DimDate.py, DimEngagement.py, DimSubscription.py <br>
Datoteka u facts: FactUserActivity.py <br>
<b>Mapa Connectors</b>
Sadrži datoteku "mysql-connector-j-9.2.0.jar". Treba je preuzeti. <br><br>
Ostale datoteke: main.py, spark_session.py

<hr>

<b>main.py - hadoop</b> <br>
[Za Windows OS] Ako ne postoji, potrebno je na sistemskoj particiji na disku kreirati mapu "hadoop". Unutar "hadoop" kreirati mapu "bin". <br>
Unutar \hadoop\bin staviti datoteku "winutils.exe" (preuzetu sa https://github.com/cdarlint/winutils/tree/master/hadoop-3.3.6/bin). Eventualno ako ne radi, dodati datoteku "hadoop.dll" u istu mapu, preuzetu iz istog repozitorija.



