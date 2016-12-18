#Webradio V2 - Ein MPD-gestützter Music-Player für den Raspberry Pi:

Für eine Beschreibung und Installationsanleitung, siehe das **[Wiki](https://github.com/Acer54/Webradio_v2/wiki/startseite)**

[![Youtube-Video](http://img.youtube.com/vi/8zRfpBta6v8/0.jpg)](https://www.youtube.com/watch?v=8zRfpBta6v8)
---
###Im YouTube-Video ist die Version1 vorgeführt worden, welche über die im Video verlinkten Download-Bereiche heruntergeladen werden kann!

<a href="http://my-darling.is-a-linux-user.org/?p=349">Besuche meinen Blog für mehr Informationen über Version2</a>

__**Zusatzfunktionen welche z.Z. in Arbeit sind von V1 zu V2:**__
<table style="undefined;table-layout: fixed; width: 864px">
<colgroup>
<col style="width: 199px">
<col style="width: 665px">
</colgroup>
  <tr>
    <th>Zusatzfeature:</th>
    <th>Beschreibung:</th>
    <th>Status:</th>
  </tr>
  <tr>
    <td>Skalierbarkeit des Programmfensters</td>
    <td>Bei der Version1 war es Aufgrund des damals von mir verwendeten Displays nie geplant eine andere Auflösung zu
    verwenden als die benutzte "1024x600". Als sich allerdings die ersten Leute auf YouTube an einen Nachbau gewagt
    hatten, wurde es bei abweichenden Displayauflösungen problematisch. Daher wurde in der Version2 darauf geachtet,
    dass das Programmfenster möglichst variabel skallierbar ist. Momentan sind folgende Limits allerdings zu
    berücksichtigen:
    MINIMUM: 640x480
    OPTIMUM: 1024x600
    Alles was darüber hinausgeht, funktioniert natürlich auch, allerdings erscheint das Fenster dann etwas verloren.</td>
    <td>Fertig!</td>
  </tr>
  <tr>
    <td>einfache Konfigurierbarkeit</td>
    <td>Für die konfiguration des Programmes war es bisher notwendig mehr oder weniger tief im Code zu editieren.
    In der Version2 war es daher angedacht, die Benutzerspezifischen Einstellungen an einer Zentralen Stelle editieren
    zu können. Im ersten Schritt erfolgt die Konfiguration nun über die Datei "webradio.conf", allerdings ist geplant
    hierzu noch ein GUI-basiertes Hilfsprogramm zu erstellen.</td>
    <td>Konfiguration über webradio.conf</td>
  </tr>
  <tr>
    <td>Menü für den Standby-Button</td>
    <td>Da nicht jeder Nutzer einen Hardware Button verwendet um die verschiedenen Zustände zu schalten, wurde der
    Wunsch geäußert, ein zusätzliches Menü hinter dem "Standby-Button" zu bekommen in dem mehrere Funktionen
    dargestellt werden können.
    Momentan ist eine Menü verfügbar welches:
    1. Herunterfahren
    2. Neustarten
    3. Standby
    4. Abbrechen
    kann.</td>
    <td>Fertig!</td>
  </tr>
  <tr>
    <td>Sleep-Timer</td>
    <td>Es wurde der Wunsch geäußert, einen Sleep-Timer zu haben, der den Webradio automatisiert nach einer bestimmten
    Zeit selbstständig herunterfährt!</td>
    <td>Fertig!</td>
  </tr>
  <tr>
    <td>Einstellungen</td>
    <td>Manche Einstellungen wollen Nutzer aus dem laufenden Programm heraus ändern können ("on the fly") ohne das
    Programm vorher schließen und neu starten zu müssen. Daher wird ein Einstellungs-Tab erstellt, welcher div. Funktionen
    abbilden kann. Unter anderem ist geplant verschiedenen "Themes" wählen zu können, die Sprache verändern zu können
    aber auch die Position für die Wetteranzeige abändern zu können.</td>
    <td>Einstellungen wie "Design-Theme", "Sprache", "Bildschirmschoner", "Heimatstadt" können im laufenden Betrieb
    geändert werden!</td>
  </tr>
  <tr>
    <td>Wetter-Location</td>
    <td>Die Wetter-Location, also der Code der ausdrückt wo man gerade lebt musste über eine dritte Webseite herausgefunden
    werden und manuell eingetragen werden. Diese soll nun aus dem Programm heraus gesucht und verändert werden können.</td>
    <td>Heimatstadt kann nun direkt über das GUI gesucht und eingestellt werden!</td>
  </tr>
  <tr>
    <td>Mehrsprachigkeit</td>
    <td>Das Programm soll in mehreren Sprachen vorliegen, damit auch Nutzer die nicht aus Deutschland stammen damit
    arbeiten können.</td>
    <td>Momentan liegt das Programm in DE (Deutsch), EN (Englisch) und BY (Bayerisch) vor. 
    Die Sprache wird automatisch mittels eingestellter Systemsprache gewählt. Eine
    eigenständige Auswahl kann jederzeit über den Einstellungs-Tab vorgenommen werden.</td>
  </tr>
  <tr>
    <td>Alternative Anzeige im Standby-Mode</td>
    <td>Viele Nutzer benutzen kein Relais oder Schaltung um das LCD ab zu schalten, oder zumindest die
    Hintergrundbeleuchtung ab zu dunkeln, daher entstand der Wunsch, dass alternativ zum GPIO-Signal eine Art
    "Bildschirmschoner angezeigt wird". Angezeigt soll werden: Eine Uhr, das Datum, der Wochentag die aktuelle
    Aussentemperatur und ein Symbol für die aktuelle Wetterlage am eingestellten Ort.</td>
    <td>Fertig!</td>
  </tr>
  <tr>
    <td>YouTube-Player (Audio)</td>
    <td>Als Erweiterung zum Media-Player werden nun Suchergebnisse von YouTube mit in Suchergebnisse gelistet,
    welche wie jeder andere Track in die Playliste eingereiht werden kann. Als Album-Cover wird ein Vorschaubild
    von Youtube angezeigt, der Link kann zur späteren Wiederverwendung in der Playliste verbleiben.</td>
    <td>In Arbeit!</td>
  </tr>
</table>
---

###Änderungen und Optimierungen die nebenher laufen:
1. Wenn kein DHT11 Temperatur-/Luftfeuchte-Messer angeschlossen ist wird nun nicht mehr nur ein "Standardwert" angezeigt,
sondern die aktuellen Temperaturdaten aus dem Wetterwidget in der Titelleiste angezeigt.

2. Implementierung von sog. "Themes", mit welchen man das Erscheinungsbild beeinflussen kann. Stylesheets werden aus
dem jeweiligen Theme geladen und sind somit variabel und für den Nutzer anpassbar (z.B. wenn eine spezielle Farbe
benötigt wird).

3. Erweiterung der Dateiunterstützung für lokale Medien von der Dateiendung *.mp3 um *.ogg und *.oga

4. Unterstützung für UPnP über mpd-Addon "upmpdcli" (siehe <a href="https://github.com/Acer54/Webradio_v2/wiki/UPnP--Streaming-Support">Wiki</a>)

5. Youtube-Player in Media-Player integriert (in Arbeit)

###Es werden Übersetzer gesucht!
Da nun die Unterstützung für weitere Sprachen fertig ist, wäre es wünschenswert mehr Sprachen zu
unterstützen. Schön wäre, wenn hierzu jemand etwas an Übersetzungen beisteuern könnte!

Bei Interesse einfach über <a href="http://my-darling.is-a-linux-user.org">my-darling.is-a-linux-user.org</a> Kontakt mit mir aufnehmen !