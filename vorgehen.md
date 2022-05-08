# Schritt 1 (Automatische Datenübernahme)

Zuweisung von "identifaction" zu der "address"

## I

```python
all_id_address = [{ "identification": ident1, "address": address1}, ... , { "identification": ident2, "address": address1}]
```

## C

```sql
SELECT DISTINCT identification, address FROM tbl_mode_s WHERE identification IS NOT NULL LIMIT 10;
+----------------+----------+
| identification | address  |
+----------------+----------+
| DILAB          |  4076629 |
|                |  4076629 |
| RYR3702        |  5023762 |
| RAM254         |   131388 |
| EXS8UT         |  4224749 |
| EXS23Y         |  4221636 |
| GFA006         |  8994959 |
| UAE232         |  9004196 |
| WUK19          |  4224269 |
| LAN705         | 15205456 |
+----------------+----------+
```

## Note

Wichtig weil alle Einträge mit `identification` haben NULL Werten

```sql
SELECT id, identification, address, bds, altitude, latitude, longitude, bds60_barometric_altitude_rate AS bar, bds60_inertial_vertical_velocity AS ivv FROM tbl_mode_s WHERE identification IS NOT NULL AND altitude IS NOT NULL LIMIT 10;
+------+----------------+---------+------+----------+----------+-----------+------+------+
| id   | identification | address | bds  | altitude | latitude | longitude | bar  | ivv  |
+------+----------------+---------+------+----------+----------+-----------+------+------+
|  203 | DILAB          | 4076629 |   32 |     3500 |     NULL |      NULL | NULL | NULL |
|  453 | DILAB          | 4076629 |   32 |     3550 |     NULL |      NULL | NULL | NULL |
|  473 | DILAB          | 4076629 |   32 |     3550 |     NULL |      NULL | NULL | NULL |
|  574 | DILAB          | 4076629 |   32 |     3550 |     NULL |      NULL | NULL | NULL |
|  730 | DILAB          | 4076629 |   32 |     3525 |     NULL |      NULL | NULL | NULL |
|  735 | DILAB          | 4076629 |   32 |     3525 |     NULL |      NULL | NULL | NULL |
|  736 | DILAB          | 4076629 |   32 |     3525 |     NULL |      NULL | NULL | NULL |
| 1078 | DILAB          | 4076629 |   32 |     3550 |     NULL |      NULL | NULL | NULL |
| 1089 | DILAB          | 4076629 |   32 |     3550 |     NULL |      NULL | NULL | NULL |
| 1379 | DILAB          | 4076629 |   32 |     3600 |     NULL |      NULL | NULL | NULL |
+------+----------------+---------+------+----------+----------+-----------+------+------+
```

# Schritt 2

Liste von Einträgen erstellen

## I

```python
all_data = [ { "id": id1, ...}, ... , {"id": idx,...} ]
```

## C

```sql
SELECT id, identification, address , timestamp, bds, altitude, latitude, longitude, bds60_barometric_altitude_rate AS bar, bds60_inertial_vertical_velocity AS ivv FROM tbl_mode_s WHERE bds60_barometric_altitude_rate AND bds60_inertial_vertical_velocity IS NOT NULL LIMIT 10;

+------+----------------+---------+------+----------+----------+-----------+------+-------+
| id   | identification | address | bds  | altitude | latitude | longitude | bar  | ivv   |
+------+----------------+---------+------+----------+----------+-----------+------+-------+
| 7739 | NULL           | 4076629 |   96 |      -50 |     NULL |      NULL |  384 |   -32 |
| 7756 | NULL           | 4076629 |   96 |      -25 |     NULL |      NULL |  448 |  -256 |
| 7778 | NULL           | 4076629 |   96 |       25 |     NULL |      NULL |  864 |  -800 |
| 7804 | NULL           | 4076629 |   96 |      125 |     NULL |      NULL |  864 |  -960 |
| 7856 | NULL           | 4076629 |   96 |      350 |     NULL |      NULL |  832 |  -736 |
| 7883 | NULL           | 4076629 |   96 |      425 |     NULL |      NULL |  672 |  -992 |
| 7935 | NULL           | 4076629 |   96 |      600 |     NULL |      NULL | 1056 |  -992 |
| 7961 | NULL           | 4076629 |   96 |      675 |     NULL |      NULL |  928 |  -928 |
| 8039 | NULL           | 4076629 |   96 |     1000 |     NULL |      NULL |  960 | -1088 |
| 8040 | NULL           | 4076629 |   96 |     1000 |     NULL |      NULL |  960 | -1088 |
+------+----------------+---------+------+----------+----------+-----------+------+-------+


SELECT id, address, bds, altitude, latitude, longitude, bds60_barometric_altitude_rate AS bar, bds60_inertial_vertical_velocity AS ivv FROM tbl_mode_s WHERE latitude IS NOT NULL AND latitude IS NOT NULL LIMIT 10;
+----+---------+------+----------+--------------------+--------------------+------+------+
| id | address | bds  | altitude | latitude           | longitude          | bar  | ivv  |
+----+---------+------+----------+--------------------+--------------------+------+------+
|  2 | 4076629 |    5 |     3700 |  52.56976318359375 | 11.587066650390625 | NULL | NULL |
|  3 | 4076629 |    5 |     3675 |  52.56962585449219 |  11.58660888671875 | NULL | NULL |
|  4 | 4076629 |    5 |     3675 |  52.56934731693591 | 11.585004534040179 | NULL | NULL |
|  7 | 4076629 |    5 |     3675 |  52.56907653808594 | 11.583633422851562 | NULL | NULL |
| 12 | 4076629 |    5 |     3675 |  52.56866455078125 | 11.581649780273438 | NULL | NULL |
| 14 | 4076629 |    5 |     3675 |  52.56852722167969 | 11.580886840820312 | NULL | NULL |
| 15 | 4076629 |    5 |     3675 | 52.568416272179554 | 11.580217633928573 | NULL | NULL |
| 17 | 4076629 |    5 |     3675 |  52.56829833984375 | 11.579666137695312 | NULL | NULL |
| 19 | 4076629 |    5 |     3675 | 52.568023681640625 |    11.578369140625 | NULL | NULL |
| 20 | 4076629 |    5 |     3675 |  52.56793212890625 | 11.577911376953125 | NULL | NULL |
+----+---------+------+----------+--------------------+--------------------+------+------+
```

## Note
- timestamp in Nanosekundendatum konvertieren
- identification dank Ergebnis aus [Schritt 1](#schritt-1-automatische-datenübernahme) zu jeder Addresse zuweisen
- 2 Durchläufe: für latitude und longitude

# Schritt 3

Leere Einträgen aus List beseitigen (ersetzt durch `-1`)

## I

```python
keys = el.keys()
for el in all_data:
    for key in keys:
        if el.key is null: el.key = -1
```

# Schritt 4

Liste nach id sortieren

# Schritt 5

- Auswahl der Datensätze (address) mit der größter Häufigkeit (pro bds? nur 2 bds? ist es wichtig?)

- **Plotten Häufigekeit über Addressen**

- Häufigkeit -> Anzahl an Flügen?

# Schritt 6

- Darstellung der Datensätze (für alle Addressen? Oder nur die mit den meisten Einträgen)
- **bar (blue) & ivv (rot) über Dauer (Zeit - Start Zeit)**
- Start Zeit (Unix Start Time) = 1625559990537752100 [ns]

# Schritt 7 

Medianfilterwertes für bar und vcc berechnen

# Schritt 8 (WICHTIG -> Recherche zu Methoden zur Sicherung der Qualität bei der Auswertung)

Berechnung zeitreihen darstellung, Werte pro minute und Gradient (unevenly distributed timeseries)

```t
Das problem der "unevenly distributed timeseries"

Option der linearen Regression und Berechnung des Mittelpunktes

erstmal dem paper Folgen, 
median glättung, dann Varianz der einzelnen Werte berechnen

gegebüber der Varianz für jeden Wert

für d

to be continued ...

darstellung über die gefilterten daten

darstellung der ersten 10 Werte

wieviel Werte sind notwendig?

Auswahl treffen

kann man das heute schaffen
```

# Schritt 9 (Wichtig für [Schritt 8](#schritt-8-wichtig---recherche-zu-methoden-zur-sicherung-der-qualität-bei-der-auswertung))

Standartabweichung von bar und ivv

# Schritt 10

Flüge plotten
