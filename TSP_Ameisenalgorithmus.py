# VOR ERSTMALIGER NUTZUNG:
# Webdriver downloaden: https://github.com/mozilla/geckodriver/releases/tag/v0.24.0
# kopiere mit: sudo cp QUELLE ZIELORT ; die geckodriver binary in diesen Pfad: /usr/local/bin
# danach selenium und pygame als Projektinterpreter über die settings installieren

import math
import random
import sys
import time

from selenium import webdriver

from lib import stddraw
from lib.Ort import Ort
from lib.picture import Picture


def daten_beschaffen():
    browser = webdriver.Firefox()  # ggf einen anderen Browser nutzen (Chrome, Edge, usw.)
    browser.get('https://www.gpskoordinaten.de/gps-koordinaten-konverter')  # öffnet Internetseite
    time.sleep(1.5)  # wartet kurz, um die Internetseite aufzubauen

    # akzeptieren der Cookies, für einen weiteren reibungslosen Ablauf
    browser.find_element_by_xpath('//a[@data-cc-event="click:dismiss"]').click()

    # finde Eingabe-/Datenfelder auf der Webseite
    adresse = browser.find_element_by_id('address')
    breitengrad = browser.find_element_by_id('latitude')
    laengengrad = browser.find_element_by_id('longitude')

    # Knopf zum Anfordern der GPS-Daten finden
    koordinaten_anfordern_knopf = browser.find_element_by_xpath('//button[@onclick="codeAddress()"]')

    # Beschaffung der GPS-Daten der Orte und Speichern in eine Liste
    liste_orte = []
    for i in range(1, len(sys.argv)):
        # löscht den Inhalt von Adresse und fügt einen neuen ein; klickt den Knopf zum Anfordern der Daten
        while adresse.get_attribute('value') is not "":
            adresse.clear()  # stellt sicher, dass das Suchfeld keinen Eintrag mehr enthält
        adresse.send_keys(sys.argv[i])
        koordinaten_anfordern_knopf.click()
        time.sleep(0.2)  # wartet kurz, um Daten zu laden

        # erstellt einen neuen Ort mit dessen Koordinanten
        ort = Ort(sys.argv[i], float(breitengrad.get_attribute('value')), float(laengengrad.get_attribute('value')))
        liste_orte.append(ort)
    browser.close()  # schließt den Browser
    return liste_orte


# speichert die Daten der Orte in ein .txt Dokument
def daten_in_dok_schreiben(liste_orte):
    dok = open('Orte_+_GPS-Koordinaten.txt', 'w')  # öffnet Dokument, im Schreibmodus (w)
    for i in range(len(liste_orte)):
        dok.write(liste_orte[i].name + ", " + str(liste_orte[i].breitengrad)
                  + ", " + str(liste_orte[i].laengengrad) + '\n')
    dok.close()


def daten_von_dok_einlesen():
    dok = open('Orte_+_GPS-Koordinaten.txt', 'r')  # öffnet Dokument, im Lesemodus (r)
    daten = dok.readlines()
    dok.close()
    return daten


def daten_formatieren(daten):
    liste_orte = []
    for i in range(len(daten)):
        feld = str.split(daten[i])  # trennt die Datenzeile in Felder auf
        feld[0] = feld[0].strip(',')  # entfernt die Kommas in dem Feld
        feld[1] = feld[1].strip(',')
        ort = Ort(feld[0], float(feld[1]), float(feld[2]))  # 0 = Ortsname 1 = Breitengrad 2 = Laengengrad
        liste_orte.append(ort)
    return liste_orte


# Erstellen einer 2D Distanzmatrix, beinhaltet die Abstände der Orte untereinader
def distanzmatrix_erstellen(anzahl_orte, liste_orte):
    distanzmatrix = []
    for i in range(anzahl_orte):
        distanzmatrix.append([])
        for j in range(anzahl_orte):
            distanzmatrix[i].append(0)
            if i == j: continue
            # Berechnung der Entfernungen: https://www.kompf.de/gps/distcalc.html
            bg_von = math.radians(liste_orte[i].breitengrad)
            lg_von = math.radians(liste_orte[i].laengengrad)
            bg_nach = math.radians(liste_orte[j].breitengrad)
            lg_nach = math.radians(liste_orte[j].laengengrad)

            distanzmatrix[i][j] = 6378.388 * math.acos(math.sin(bg_von) * math.sin(bg_nach)
                                                       + math.cos(bg_von) * math.cos(bg_nach) * math.cos(
                lg_von - lg_nach))
    return distanzmatrix


# Anzeigen der Distanzmatrix lassen
def distanzmatrix_anzeigen(distanzmatrix):
    for i in range(len(distanzmatrix)):
        print(distanzmatrix[i])


# Pheromonmatrix erstellen
def pheromonmatrix_erstellen(anzahl_orte):
    pheromonmatrix = []
    for i in range(anzahl_orte):
        pheromonmatrix.append([])
        for j in range(anzahl_orte):
            pheromonmatrix[i].append(0.1)  # Ausgangspheromonwert aller Verbindungen
    return pheromonmatrix


# Pheromonmatrix anzeigen lassen
def pheromonmatrix_anzeigen(pheromonmatrix):
    for i in range(len(pheromonmatrix)):
        print(pheromonmatrix[i])


# führt einen Durchlauf des Ameisenalgorithmus durch
def ameisenalgotithmus_durchlauf(anzahl_orte, distanzmatrix, pheromonmatrix):
    loesungsvektor = [0] * anzahl_orte
    nbo = list(range(anzahl_orte))  # nbo = nicht besuchte Orte, list(range) erstellt Liste von 0,1,...,anzahl_orte
    auswahl = 0  # auswahl = Ort der gewählt wurde; von dem aus neu gesucht wird

    for i in range(1, anzahl_orte):
        nbo.remove(auswahl)  # entfernt den momentan besuchten Ort aus der nbo-Liste
        p = [0] * len(nbo)  # p = Wert der zur Berechnung der Wahrscheilichkeit einer Auswahl dient
        summe_p = 0  # wird Summe über alle p, zur Berechnung der Wahrscheinlichkeit
        for j in range(len(nbo)):
            # Tupel aus den Wert von p der sich aus der Division ergibt + die Nummer des nicht besuchten Ortes
            p[j] = (pheromonmatrix[auswahl][nbo[j]] / distanzmatrix[auswahl][nbo[j]], nbo[j])
            summe_p += p[j][0]

        # Berechnung der Wahrscheinlichkeiten + Monte-Carlo-Auswahl (Roulette Wheel Selection)
        kum_wahrscheinlichkeit = 0  # aufsummierte Wahrscheinlichkeiten, zur Auswahl eines Ortes
        zufall = random.random()  # Zufallswert zw. 0 und 1, zur Auswahl
        for x in range(len(p)):
            kum_wahrscheinlichkeit += p[x][0] / summe_p
            # Monte-Carlo-Auswahl
            if kum_wahrscheinlichkeit >= zufall:
                auswahl = p[x][1]
                break
        loesungsvektor[i] = auswahl  # die getroffene Auswahl wird dem Lösungsvektor hinzugefügt
    zfw = zielfunktionswert_berechnen(loesungsvektor, distanzmatrix)
    pheromonmatrix_neuberechnung(loesungsvektor, zfw, pheromonmatrix)
    return (loesungsvektor, zfw)  # gibt Tupel zurück mit, der Strecke und den dazugehörigen Zielfunktionswert


# Berechnung des Zielfunktionswerts
def zielfunktionswert_berechnen(loesungsvektor, distanzmatrix):
    zfw = 0
    for i in range(len(loesungsvektor) - 1):
        zfw += distanzmatrix[loesungsvektor[i]][loesungsvektor[i + 1]]  # berechnet die Strecke von i nach i+1
    zfw += distanzmatrix[-1][0]  # Strecke vom letzten Ort zurück zum ersten um Rundreise zu beenden
    return zfw


# Neuberechnung der pheromonmatrix
# erhöht die Pheromone der genutzten Verbindungen
def pheromonmatrix_neuberechnung(loesungsvektor, zfw, pheromonmatrix):
    for i in range(len(loesungsvektor) - 1):
        pheromonmatrix[loesungsvektor[i]][loesungsvektor[i + 1]] += 1 / zfw  # Strecke von i nach i+1
    pheromonmatrix[loesungsvektor[-1]][loesungsvektor[0]] += 1 / zfw  # ltzte Strecke um Rundreise zu beenden


# wiedergabe der besten gefundenen Lösung, entweder beste gefundene Strecke (min zfw)
# oder bester Weg anhand der Pheromonwerte, wenn diese Strecke kürzer ist als die bisher beste gefundene Strecke
def loesung(anzahl_orte, pheromonmatrix, distanzmatrix, zfw_bester_weg):
    loesungsvektor = [0] * anzahl_orte
    auswahl = 0
    for i in range(anzahl_orte):
        loesungsvektor[i] = auswahl
        for j in range(anzahl_orte):  # setzt in allen Zeilen den Pheromonwert der getroffenen
            pheromonmatrix[j][auswahl] = 0  # Auswahl auf 0 um eine erneute Auswahl zu verhindern
        # sucht den größten Pheromonwert in einer Zeile und gibt davon den Index
        auswahl = pheromonmatrix[auswahl].index(max(pheromonmatrix[auswahl]))
    zfw_pheromone = zielfunktionswert_berechnen(loesungsvektor, distanzmatrix)
    # prüft ob die Strecke anhand der Pheromonwerte kürzer ist als die bisher beste gefundene Strecke
    if zfw_pheromone <= zfw_bester_weg[1]:
        return (loesungsvektor, zfw_pheromone)  # gibt Tupel zurück mit, Strecke und den dazugehörigen Zielfunktionswert
    else:
        return zfw_bester_weg


# zeigt das Ergebnis in der Konsole an
def ausgabe_ergebnis(loesung, liste_orte):
    print('Strecke:')
    for i in range(len(loesung[0])):
        print(liste_orte[int(loesung[0][i])].name)
    print(liste_orte[0].name)  # kehrt zum Ausgangspunkt zurück um Rundreise zu beenden
    print('mit', loesung[1], 'km')


# richtet die Leinwandgröße ein und sklaiert die Achsen zur weiteren Nutzung
# Quelle Karte: https://de.wikipedia.org/wiki/Datei:Europe_location_map.svg#file
def karte_einrichten():
    karte = Picture('Europe_location_map.svg.png')  # liest das Europakarte ein,
    stddraw.setCanvasSize(karte.width(), karte.height())  # setzt die Leinwandgröße
    stddraw.picture(karte)  # und wandelt in Bild um
    # Geographische Begrenzung der Karte:  N: 82° N   S: 28° N   W: 25° W   O: 54° O
    stddraw.setXscale(-25, 54)  # Laengengrade
    stddraw.setYscale(28, 82)  # Breitengrade


# zeichnet Verbindungen zw. den Orten
# x = Laengengrad y = Breitengrad
def verbinungen_zeichnen(loesung, liste_orte):
    for i in range(len(loesung) - 1):
        stddraw.line(liste_orte[int(loesung[i])].laengengrad, liste_orte[int(loesung[i])].breitengrad,
                     liste_orte[int(loesung[i + 1])].laengengrad, liste_orte[int(loesung[i + 1])].breitengrad)
    stddraw.line(liste_orte[int(loesung[-1])].laengengrad, liste_orte[int(loesung[-1])].breitengrad,
                 liste_orte[int(loesung[0])].laengengrad, liste_orte[int(loesung[0])].breitengrad)


# zeichnet Punkte an die Stelle der Orte
# x = Laengengrad y = Breitengrad
def punkte_zeichnen(liste_orte):
    stddraw.setPenRadius(0.008)
    stddraw.setPenColor(stddraw.RED)
    for i in range(len(liste_orte)):
        stddraw.point(liste_orte[i].laengengrad, liste_orte[i].breitengrad)


# zeigt die Karte an
def karte_anzeigen():
    stddraw.show()


def main():
    # Abfrage ob eine neue Datensuche-/beschaffung getätigt werden soll oder nicht
    # Übergabe der neu zu suchenden Daten erfolgt mittels der Kommandozeile beim Aufruf des Scripts
    # erstgenannter Ort = Anfang und Ende der Rundreise
    eingabe1 = input('Wollen Sie eine neue Suche starten? \nj/n\n')
    iterationen = int(input('Anzahl der Iterationen: '))  # Anzahl der Durchläufe des Ameisenalgorithmus
    if eingabe1 == 'j':
        liste_orte = daten_beschaffen()  # aus dem Internet via Browser
        daten_in_dok_schreiben(liste_orte)
    else:
        daten = daten_von_dok_einlesen()
        liste_orte = daten_formatieren(daten)
    anzahl_orte = len(liste_orte)
    distanzmatrix = distanzmatrix_erstellen(anzahl_orte, liste_orte)
    # distanzmatrix_anzeigen(distanzmatrix)             # falls benötigt/gewollt
    pheromonmatrix = pheromonmatrix_erstellen(anzahl_orte)
    zfw_bester_weg = ([], math.inf)  # möglichst großer Startwert
    zaehler = 0  # zählt wie oft hintereinader das beste Ergebnis erreicht wurde
    for i in range(iterationen):
        zfw = ameisenalgotithmus_durchlauf(anzahl_orte, distanzmatrix, pheromonmatrix)
        if zfw == zfw_bester_weg[1]:
            zaehler += 1  # Abbruch der Durchläufe wenn vermutlich kein besserer Weg gefunden wird
            if zaehler == 3: break  # Anzahl evtl. anpassen nach weiteren Beobachtungen
        else:
            zaehler = 0
        if zfw[1] < zfw_bester_weg[1]: zfw_bester_weg = zfw
    # pheromonmatrix_anzeigen(pheromonmatrix)           # falls benötigt/gewollt
    beste_loesung = loesung(anzahl_orte, pheromonmatrix, distanzmatrix, zfw_bester_weg)
    ausgabe_ergebnis(beste_loesung, liste_orte)
    karte_einrichten()
    verbinungen_zeichnen(beste_loesung[0], liste_orte)  # Übergibt nur den Loesungsvektor
    punkte_zeichnen(liste_orte)
    karte_anzeigen()


if __name__ == '__main__':
    main()

'''
python TSP_Ameisenalgorithmus.py Amsterdam Athen Berlin Bern Brüssel Budapest Bukarest Dublin Kiew Lissabon London

Wollen Sie eine neue Suche starten? 
j/n
j
Strecke:
Amsterdam
Dublin
London
Brüssel
Berlin
Budapest
Kiew
Bukarest
Athen
Bern
Lissabon
Amsterdam
mit 8925.229154990564 km
'''
