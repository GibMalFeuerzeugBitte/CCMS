╔══════════════════════════════════════════════════════════════════════════════╗
║                    COMMENTARY COUNTER - README & DOKUMENTATION               ║
║                            Version 5 - Meta Systems                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

===============================================================================
                              INHALTSVERZEICHNIS
===============================================================================

1. ÜBERSICHT
2. FUNKTIONSWEISE DER KOMMENTAR-ZÄHLUNG
3. TIMESTAMP-BASIERTES ZÄHLSYSTEM
4. BENUTZEROBERFLÄCHE
5. KOMMENTAR-ANALYSE DETAILS
6. SAMMEL-PDF FUNKTION
7. KOMMENTIERTE SEITEN
8. TECHNISCHE DETAILS
9. BEKANNTE BESONDERHEITEN
10. FAQ


===============================================================================
                              1. ÜBERSICHT
===============================================================================

Der Commentary Counter ist ein spezialisiertes Tool zur Analyse und Zählung 
von Kommentaren in PDF-Dokumenten. Das Programm wurde entwickelt, um eine 
präzise Erfassung aller Annotationen zu gewährleisten und basiert auf einem 
innovativen Timestamp-basierten Zählsystem.

HAUPTFUNKTIONEN:
• Zählung aller PDF-Kommentare basierend auf eindeutigen Zeitstempeln
• Detaillierte Analyse mit Seitennummer, Typ, Autor und Inhalt
• Intelligente Sammel-PDF Funktion mit Annotation-Merging
• Automatische Duplikat-Erkennung beim Import von Kommentaren
• Drag & Drop Unterstützung für schnelles Hinzufügen von PDFs
• Dark Mode / Light Mode Umschaltung
• Übersichtliche Darstellung mit formatierter Zeitanzeige

WAS MACHT DIESES PROGRAMM SO BESONDERS?

Der Commentary Counter ist nicht nur ein einfacher Zähler - er ist ein 
vollwertiges PDF-Kommentar-Analyse- und Merge-Tool. Im Gegensatz zu anderen
Tools versteht das Programm die interne Struktur von PDF-Annotationen und
kann diese präzise zusammenführen, ohne dabei Kommentar-Threads oder 
Antworten zu verlieren.

Die einzigartige Timestamp-basierte Zählung garantiert absolute Genauigkeit,
während die Annotation-Merge-Funktion mit pikepdf eine professionelle 
Zusammenführung von Kommentaren ermöglicht - vergleichbar mit Adobe Acrobat's
"Kommentare importieren" Funktion, aber mit zusätzlicher Duplikat-Erkennung!


===============================================================================
                    2. FUNKTIONSWEISE DER KOMMENTAR-ZÄHLUNG
===============================================================================

GRUNDPRINZIP:
Das Programm verwendet ein Timestamp-basiertes System zur Identifikation
eindeutiger Kommentare. Jeder Kommentar wird anhand seines Erstellungs- oder
Änderungszeitstempels identifiziert.

WARUM TIMESTAMP-BASIERT?
────────────────────────
Frühere Ansätze versuchten, Kommentare anhand ihres Typs zu klassifizieren
(z.B. StrikeOut + Caret als ein Kommentar). Dies führte jedoch zu Problemen:

• StrikeOut-Kommentare konnten mit oder ohne Caret-Partner vorkommen
• Verschiedene Autoren nutzen unterschiedliche Kommentierungsstile
• Manche Kommentare haben Content, andere nicht
• Adobe zeigt manche Annotation-Paare als separate Einträge an

LÖSUNG: EINDEUTIGE ZEITSTEMPEL
────────────────────────────────
Jeder Kommentar in einem PDF hat einen eindeutigen Erstellungszeitpunkt.
Durch Zählung der eindeutigen Zeitstempel erhalten wir die exakte Anzahl
der Kommentare - unabhängig vom Typ oder der internen Struktur.

FORMEL: 1 eindeutiger Zeitstempel = 1 Kommentar


===============================================================================
                    3. TIMESTAMP-BASIERTES ZÄHLSYSTEM
===============================================================================

PDF-ZEITSTEMPEL-ARTEN:
─────────────────────

1. creationDate (Erstellungsdatum)
   • Wird beim ersten Erstellen des Kommentars gesetzt
   • Beispiel: Sie markieren Text und klicken "Kommentar hinzufügen"
   • Zeitpunkt: 09:16:44

2. modDate (Änderungsdatum)
   • Wird aktualisiert bei jeder Änderung des Kommentars
   • Beispiel: Sie tippen Text ein und drücken Enter
   • Zeitpunkt: 09:16:45 (1 Sekunde nach Erstellung)

PRIORITÄT IM PROGRAMM:
─────────────────────
Das Programm sucht in folgender Reihenfolge:

1. Zuerst: creationDate → wenn vorhanden, wird dieser verwendet
2. Dann: modDate → wenn creationDate fehlt
3. Fallback: Generierter eindeutiger Identifier aus:
   - NO_TIMESTAMP_[Nummer]_[Typ]_[Autor]_[Seitenzahl]

ZEITABWEICHUNGEN ZU ADOBE:
──────────────────────────
Sie werden feststellen, dass die angezeigten Zeiten manchmal um wenige
Sekunden oder Minuten von Adobe abweichen. Das ist normal!

GRUND:
• Unser Programm bevorzugt creationDate (Erstellungszeitpunkt)
• Adobe zeigt oft modDate an (letztes Änderungsdatum)
• Unterschied entsteht durch Bearbeitungszeit des Kommentars

BEISPIEL:
Adobe zeigt: 09:16:45 (modDate - nach dem Tippen)
Programm zeigt: 09:16:44 (creationDate - beim Erstellen)
Differenz: 1 Sekunde

WICHTIG: Die Abweichung beeinflusst NICHT die Zählgenauigkeit!
Jeder Kommentar hat weiterhin einen eindeutigen Identifier.

ZEITFORMAT-KONVERTIERUNG:
────────────────────────
PDF-intern: D:20251114091825+01'00'
            └─ Jahr: 2025, Monat: 11, Tag: 14
               Stunde: 09, Minute: 18, Sekunde: 25
               Zeitzone: +01:00

Anzeige: 14.11.2025 09:18:25
         └─ Lesbar formatiert von links nach rechts


===============================================================================
                         4. BENUTZEROBERFLÄCHE
===============================================================================

DATEI-AUSWAHL BEREICH:
─────────────────────
• Listbox mit alternierenden Hintergrundfarben für bessere Lesbarkeit
• Buttons:
  - "PDFs hinzufügen" (Grün): Mehrere PDFs auswählen
  - "Ausgewählte entfernen" (Rot): Markierte PDFs aus Liste entfernen
  - "Alle entfernen": Liste komplett leeren

ZÄHLUNG BEREICH:
───────────────
• Zeigt Gesamtanzahl der gefundenen Kommentare
• Wird nach jeder Zählung aktualisiert

KOMMENTAR-DETAILS KONSOLE:
─────────────────────────
• Detaillierte Auflistung aller gefundenen Kommentare
• Scrollbar für lange Listen
• Grauer Hintergrund für bessere Lesbarkeit

AKTIONS-BUTTONS:
───────────────
1. "Kommentare zählen": Analysiert alle PDFs und zeigt Details
2. "Sammel-PDF erstellen": Exportiert alle kommentierten Seiten

DARK MODE / LIGHT MODE UMSCHALTUNG:
───────────────────────────────────
• Toggle-Button befindet sich unten rechts im Fenster
• Standard: Light Mode (helle Farben)
• Per Klick umschaltbar zwischen beiden Modi

LIGHT MODE (Standard):
• Helle Grautöne (#CDCDCD, #E8E8E8, #DDD7D7)
• Grüne Buttons (#4CAF50) für Hauptaktionen
• Rote Buttons (#f44336) für Löschen-Aktionen
• Schwarze Schrift (#000000)

DARK MODE:
• Dunkle Grautöne (#2b2b2b, #3c3c3c, #1e1e1e)
• Dunkelblaue Buttons (#1e3a5f) für Hauptaktionen
• Dunkelgrüne Buttons (#1e4d2b) für Hinzufügen
• Dunkelrote Buttons (#5f1e1e) für Löschen-Aktionen
• Helle Schrift (#e0e0e0, #ffffff)

FARBSCHEMA ANPASSEN:
Alle Farben sind im Code in Hex-Format definiert und können leicht 
angepasst werden in den Dictionaries LIGHT_MODE und DARK_MODE.


===============================================================================
                      5. KOMMENTAR-ANALYSE DETAILS
===============================================================================

AUSGABE-FORMAT PRO KOMMENTAR:
────────────────────────────
Seite [Nr] | [Typ] | [Autor]
  → [Kommentar-Inhalt (erste 80 Zeichen)]
  📅 [Formatiertes Datum]

BEISPIEL:
────────
Seite 172 | StrikeOut | Anna von Bonhorst
  📅 14.11.2025 09:16:45

Seite 201 | Text | Anna von Bonhorst
  → Zeilenfall: bitte vor der Klammer
  📅 14.11.2025 11:50:29

ERKANNTE KOMMENTAR-TYPEN:
────────────────────────
• Text - Textkommentare und Notizen
• StrikeOut - Durchgestrichener Text (mit Löschvorschlag)
• Caret - Eingefügter Text (Einfügevorschläge)
• Highlight - Markierungen/Hervorhebungen
• Underline - Unterstreichungen
• Squiggly - Wellenlinien
• FreeText - Freitext-Annotationen
• und weitere PDF-Annotation-Typen

BESONDERHEITEN BEI DER ANZEIGE:
──────────────────────────────
• Kommentare werden nach Seitennummer sortiert angezeigt
• Inhalte werden auf 80 Zeichen gekürzt (mit "..." Suffix)
• Zeitstempel werden nur angezeigt, wenn vorhanden
• Leere Zeile zwischen Kommentaren für bessere Lesbarkeit

ZUSAMMENFASSUNG AM ENDE:
───────────────────────
✓ Gesamt: [Anzahl] Kommentar(e) (basierend auf eindeutigen Zeitstempeln)

Pro Datei:
  • [Dateiname]: [Anzahl] Kommentar(e)


===============================================================================
                    6. SAMMEL-PDF FUNKTION (NEU!)
===============================================================================

"SAMMEL-PDF ERSTELLEN" FUNKTION:
───────────────────────────────
Dies ist eine der Hauptfunktionen des Programms und arbeitet ähnlich wie
Adobe Acrobat's "Kommentare importieren", aber mit intelligenten Zusatzfeatures!

═══════════════════════════════════════════════════════════════════════════════
                        WIE FUNKTIONIERT DAS GENAU?
═══════════════════════════════════════════════════════════════════════════════

KONZEPT: ANNOTATION-MERGING
───────────────────────────
Das Programm kann Kommentare aus mehreren PDFs zusammenführen, OHNE dabei
die Seiten zu duplizieren. Das funktioniert wie folgt:

EINGABE:
--------
• PDF1.pdf (100 Seiten, 50 Kommentare) ← BASIS-PDF
• PDF2.pdf (100 Seiten, 30 Kommentare) ← Nur Kommentare importieren
• PDF3.pdf (100 Seiten, 20 Kommentare) ← Nur Kommentare importieren

AUSGABE:
--------
• Sammlung.pdf (100 Seiten, 100 Kommentare)
  └─ Alle Seiten von PDF1
  └─ Alle Kommentare von PDF1 + PDF2 + PDF3

═══════════════════════════════════════════════════════════════════════════════
                         WICHTIGE VORAUSSETZUNG
═══════════════════════════════════════════════════════════════════════════════

Alle PDFs müssen:
• ✓ Identische Seitenzahl haben (z.B. alle 100 Seiten)
• ✓ Identische Seitenreihenfolge haben
• ✓ Idealerweise dasselbe Dokument sein (verschiedene Versionen mit Kommentaren)

WARUM IST DAS SO?
─────────────────
Die Kommentare werden 1:1 zugeordnet:
• Kommentar auf Seite 5 in PDF2 → wird auf Seite 5 in PDF1 platziert
• Kommentar auf Seite 23 in PDF3 → wird auf Seite 23 in PDF1 platziert

Wenn die PDFs unterschiedliche Seitenanzahl oder Reihenfolge haben,
landen die Kommentare auf den falschen Seiten!

═══════════════════════════════════════════════════════════════════════════════
                       TECHNISCHER ABLAUF (INTERN)
═══════════════════════════════════════════════════════════════════════════════

PHASE 1: BASIS-PDF LADEN
────────────────────────
• Die erste PDF in der Liste wird als Basis verwendet
• Diese PDF liefert alle Seiten für das Endergebnis
• Ihre eigenen Kommentare bleiben erhalten

PHASE 2: ANNOTATION-IMPORT MIT PIKEPDF
──────────────────────────────────────
Für jede weitere PDF (PDF2, PDF3, ...):

1. PDF wird geöffnet
2. Für jede Seite werden alle Annotationen extrahiert
3. Annotationen werden mit copy_foreign() in die Basis-PDF kopiert
   → Dies kopiert AUTOMATISCH auch:
     • Appearance Streams (/AP) - visuelle Darstellung
     • Popup-Fenster
     • Reply-Threads (IRT = In-Reply-To)
     • Parent/Child Beziehungen
4. Annotationen werden der entsprechenden Seite in der Basis-PDF hinzugefügt

PHASE 3: REFERENZ-REPARATUR
───────────────────────────
• Kommentar-Threads (Antworten auf Kommentare) haben interne Referenzen
• Diese Referenzen zeigen auf die alten Objekt-IDs aus der Quell-PDF
• Das Programm erstellt eine Mapping-Tabelle: alte ID → neue ID
• Alle Referenzen (/IRT, /Parent, /Popup, /Next, /Prev) werden aktualisiert
• Dadurch bleiben Kommentar-Threads intakt!

PHASE 4: DUPLIKAT-ERKENNUNG
───────────────────────────
Bevor ein Kommentar hinzugefügt wird, prüft das Programm:

✓ Hat die Zielseite bereits einen identischen Kommentar?

EIN KOMMENTAR GILT ALS DUPLIKAT WENN:
• Gleicher Typ (z.B. beide "Text" oder beide "Highlight")
• Gleiche Position (Rect-Koordinaten)
• Gleicher Inhalt (Contents)
• Gleiche QuadPoints (bei Markierungen)

Wenn alle Kriterien übereinstimmen → Kommentar wird übersprungen
Wenn auch nur ein Kriterium unterschiedlich ist → Kommentar wird hinzugefügt

BEISPIEL:
---------
Seite 10 hat bereits: "Tolle Idee!" an Position (100, 200)
PDF2 will hinzufügen: "Tolle Idee!" an Position (100, 200)
→ DUPLIKAT! Wird nicht hinzugefügt

Seite 10 hat bereits: "Tolle Idee!" an Position (100, 200)
PDF2 will hinzufügen: "Tolle Idee!" an Position (150, 300)
→ KEIN DUPLIKAT! Wird hinzugefügt (andere Position)

═══════════════════════════════════════════════════════════════════════════════
                           7. KOMMENTIERTE-SEITEN
═══════════════════════════════════════════════════════════════════════════════
• Öffne die Datei
• Analysiert jede Seite
   - Enthält sie /Annots ? → Dann behalten
   - Keine /Annots ? → Dann rauswerfen
• Speichert eine Kommentierte_SeitenPDF (mit nur kommentierten Seiten)

    Args:
        source_pdf_path: str - Die Quell-PDF
        output_pdf_path: str - Die Ausgabe-PDF
    
    Returns:
        int: Anzahl der behaltenen Seiten

═══════════════════════════════════════════════════════════════════════════════
                           PRAKTISCHE ANWENDUNGSFÄLLE
═══════════════════════════════════════════════════════════════════════════════

USE CASE 1: TEAM-REVIEW ZUSAMMENFÜHREN
──────────────────────────────────────
Situation:
• Sie verteilen Dokument.pdf an 3 Kollegen zur Durchsicht
• Jeder kommentiert unabhängig seine Kopie
• Sie wollen alle Kommentare in einem PDF sehen

Lösung:
1. Fügen Sie alle 4 PDFs (Ihre + 3 Kollegen) zum Programm hinzu
2. Ihre PDF wird als Basis genommen
3. Klicken Sie "Sammel-PDF erstellen"
4. Ergebnis: Ein PDF mit allen Kommentaren aller Beteiligten!

USE CASE 2: MEHRERE REVIEW-RUNDEN KONSOLIDIEREN
───────────────────────────────────────────────
Situation:
• Review Runde 1: Sie erhalten Dokument_v1_Kommentare.pdf
• Review Runde 2: Sie erhalten Dokument_v2_Kommentare.pdf
• Review Runde 3: Sie erhalten Dokument_v3_Kommentare.pdf
• Sie wollen alle Kommentare in einem PDF zusammenführen

Lösung:
1. Alle drei PDFs zum Programm hinzufügen
2. "Sammel-PDF erstellen"
3. Automatische Duplikat-Erkennung verhindert doppelte Kommentare
4. Ergebnis: Vollständige Übersicht aller Review-Kommentare!

USE CASE 3: BACKUP & ARCHIVIERUNG
─────────────────────────────────
Situation:
• Sie haben verschiedene Versionen eines PDFs mit unterschiedlichen Kommentaren
• Sie wollen sicherstellen, dass keine Kommentare verloren gehen

Lösung:
1. Alle Versionen hinzufügen
2. Sammel-PDF erstellen
3. Duplikat-Erkennung sorgt dafür, dass jeder Kommentar nur einmal vorkommt
4. Ergebnis: Vollständiges Archiv ohne Redundanzen!

═══════════════════════════════════════════════════════════════════════════════
                              DATEINAME & AUSGABE
═══════════════════════════════════════════════════════════════════════════════

DATEINAME:
─────────
Standard: Kommentare_Sammlung_YYYYMMDD_HHMMSS.pdf
Beispiel: Kommentare_Sammlung_20251121_143022.pdf

Sie können beim Speichern einen eigenen Namen wählen.

KONSOLEN-AUSGABE WÄHREND DES VORGANGS:
──────────────────────────────────────
============================================================
SAMMEL-PDF WIRD ERSTELLT …
============================================================

Basis-PDF: Dokument_v1.pdf
Importiere Kommentare aus 2 weiteren PDF(s)

✔ Fertig! Datei gespeichert:
C:\Users\...\Kommentare_Sammlung_20251121_143022.pdf
============================================================

═══════════════════════════════════════════════════════════════════════════════
                        VERGLEICH MIT ADOBE ACROBAT
═══════════════════════════════════════════════════════════════════════════════

ADOBE ACROBAT PRO:
──────────────────
• Hat "Kommentare importieren" Funktion
• Importiert nur Kommentare, nicht die Seiten ✓
• Behält Kommentar-Threads bei ✓
• KEINE automatische Duplikat-Erkennung ✗
• Kostenpflichtig (ca. 15€/Monat) ✗

COMMENTARY COUNTER:
───────────────────
• Hat "Sammel-PDF erstellen" Funktion ✓
• Importiert nur Kommentare, nicht die Seiten ✓
• Behält Kommentar-Threads bei ✓
• AUTOMATISCHE Duplikat-Erkennung ✓
• Kostenlos ✓
• Funktioniert mit mehreren PDFs gleichzeitig ✓

→ Das Programm ist eine kostenlose Alternative zu Adobe Acrobat Pro
   mit zusätzlichen intelligenten Features!


===============================================================================
                         8. TECHNISCHE DETAILS
===============================================================================

VERWENDETE BIBLIOTHEKEN:
───────────────────────
• tkinter - Grafische Benutzeroberfläche
• tkinterdnd2 - Drag & Drop Funktionalität
• PyMuPDF (fitz) - PDF-Verarbeitung und Annotation-Extraktion für Zählung
• pikepdf - Professionelles Annotation-Merging (Low-Level PDF-Manipulation)
• pathlib - Dateipfad-Verwaltung
• datetime - Zeitstempel-Formatierung

WARUM ZWEI PDF-BIBLIOTHEKEN?
────────────────────────────
PyMuPDF (fitz):
• Schnell und einfach für Analyse und Zählung
• Perfekt für Annotation-Extraktion und Zeitstempel-Auslesen
• Ideal für die "Kommentare zählen" Funktion

pikepdf:
• Low-Level Zugriff auf PDF-Interna
• Präzise Objektreferenz-Verwaltung
• Notwendig für korrektes Annotation-Merging mit Thread-Erhaltung
• Ideal für die "Sammel-PDF erstellen" Funktion

→ Jede Bibliothek hat ihre Stärken, gemeinsam sind sie unschlagbar!

ALGORITHMUS ZUR KOMMENTAR-ZÄHLUNG:
──────────────────────────────────

1. INITIALISIERUNG:
   - Erstelle leeres Set für eindeutige Zeitstempel
   - Erstelle Dictionary für Kommentar-Details
   - Initialisiere Counter für Kommentare ohne Zeitstempel

2. FÜR JEDES PDF:
   a) Öffne PDF-Dokument
   b) Durchlaufe alle Seiten
   
   c) FÜR JEDE ANNOTATION AUF DER SEITE:
      - Lese Typ, Autor, Inhalt
      - Lese creationDate und modDate
      
      - TIMESTAMP-AUSWAHL:
        * Wenn creationDate vorhanden → verwende als Identifier
        * Sonst wenn modDate vorhanden → verwende als Identifier
        * Sonst → generiere eindeutigen Fallback-Identifier
      
      - DUPLIKAT-PRÜFUNG:
        * Prüfe ob Timestamp bereits im Set existiert
        * Wenn NEU → füge zu Set hinzu und speichere Details
        * Wenn DUPLIKAT → überspringe (verhindert Doppelzählung)

3. ZÄHLUNG:
   - Anzahl Kommentare = Größe des Timestamp-Sets
   - Jeder eindeutige Timestamp = 1 Kommentar

4. AUSGABE:
   - Sortiere Kommentare nach Seitennummer
   - Formatiere Zeitstempel für Anzeige
   - Zeige Details in Konsole

DATENSTRUKTUR:
─────────────
unique_timestamps = Set{
    "D:20251114091644+01'00'",
    "D:20251114091825+01'00'",
    "NO_TIMESTAMP_1_Text_Anna von Bonhorst_201"
}

timestamp_details = Dict{
    "D:20251114091644+01'00'": {
        "page": 172,
        "type": "StrikeOut",
        "author": "Anna von Bonhorst",
        "content": "",
        "date": "D:20251114091644+01'00'"
    }
}


===============================================================================
                       9. BEKANNTE BESONDERHEITEN
===============================================================================

KOMMENTARE OHNE ZEITSTEMPEL:
───────────────────────────
Manche PDF-Editoren erstellen Kommentare ohne Zeitstempel.
Diese erscheinen in Adobe als "Unbestimmt".

LÖSUNG:
Das Programm generiert für jeden zeitstempel-losen Kommentar einen
eindeutigen Fallback-Identifier mit fortlaufender Nummerierung:
NO_TIMESTAMP_1, NO_TIMESTAMP_2, etc.

Dadurch wird garantiert, dass auch diese Kommentare einzeln gezählt werden.

MEHRFACH-ANNOTATIONEN:
─────────────────────
Wenn auf derselben Textstelle mehrere Annotations-Ebenen liegen
(z.B. Highlight + Text-Kommentar), werden diese als separate Kommentare
gezählt, da sie unterschiedliche Zeitstempel haben.

PERFORMANCE:
───────────
Bei sehr großen PDFs (>1000 Seiten) oder vielen Dateien kann die Analyse
einige Sekunden dauern. Dies ist normal und hängt von der PDF-Komplexität ab.

DRAG & DROP:
───────────
Sie können PDF-Dateien direkt aus dem Windows Explorer in die Dateiliste
ziehen. Das Programm erkennt mehrere Dateien gleichzeitig und fügt sie
automatisch zur Liste hinzu.

APPEARANCE STREAMS:
──────────────────
Manche Kommentare haben visuelle Darstellungen (Appearance Streams /AP).
Diese werden beim Annotation-Merging automatisch mitkopiert, sodass die
Kommentare in der Sammel-PDF genau so aussehen wie im Original.


===============================================================================
                                  10. FAQ
===============================================================================

F: Kann ich PDFs mit unterschiedlicher Seitenzahl zusammenführen?
A: Nein, für die Sammel-PDF Funktion müssen alle PDFs identische Seitenzahl
   haben. Die Kommentare werden 1:1 auf die entsprechenden Seiten übertragen.
   Wenn die PDFs unterschiedliche Seitenzahlen haben, landen Kommentare auf
   falschen Seiten oder gehen verloren.

F: Was passiert wenn ich denselben Kommentar mehrfach importiere?
A: Die Duplikat-Erkennung verhindert automatisch doppelte Kommentare.
   Ein Kommentar wird als Duplikat erkannt, wenn Typ, Position, Inhalt und
   QuadPoints identisch sind.

F: Werden Kommentar-Threads (Antworten) richtig zusammengeführt?
A: Ja! Das Programm repariert automatisch alle internen Referenzen
   (/IRT, /Parent, /Popup, etc.), sodass Kommentar-Threads intakt bleiben.

F: Kann ich mehr als 2 PDFs gleichzeitig zusammenführen?
A: Ja! Sie können beliebig viele PDFs hinzufügen. Die erste PDF ist die
   Basis, alle weiteren PDFs liefern ihre Kommentare.

F: Warum weichen die Zeitstempel manchmal von Adobe ab?
A: Das Programm bevorzugt creationDate (Erstellungszeitpunkt), während
   Adobe oft modDate (Änderungsdatum) anzeigt. Die Differenz entsteht
   durch die Bearbeitungszeit. Die Zählgenauigkeit wird dadurch nicht
   beeinflusst.

F: Kann ich die Farben der Benutzeroberfläche ändern?
A: Ja! Die Farben sind im Code in den Dictionaries LIGHT_MODE und DARK_MODE
   definiert (Hex-Format) und können leicht angepasst werden.

F: Was ist der Unterschied zu Adobe Acrobat's "Kommentare importieren"?
A: Unser Programm funktioniert ähnlich, ist aber kostenlos und hat eine
   automatische Duplikat-Erkennung. Außerdem können Sie mehrere PDFs
   gleichzeitig verarbeiten statt nur zwei.

F: Kann ich das Programm auch für PDFs verwenden, die keine Kommentare haben?
A: Ja, das Programm zeigt dann einfach "0 Kommentare" an. Bei der
   Sammel-PDF Funktion benötigen Sie mindestens 2 PDFs.

F: Werden auch Zeichnungen, Stempel und Unterschriften kopiert?
A: Ja! Alle Annotationstypen werden unterstützt (Text, Highlight, StrikeOut,
   Stamps, FreeText, Ink, Line, etc.). Das Programm kopiert alles, was im
   PDF als Annotation markiert ist.

F: Kann ich einzelne PDFs aus der Liste wieder entfernen?
A: Ja! Markieren Sie die gewünschten PDFs und klicken Sie auf
   "Ausgewählte entfernen" oder "Alle entfernen" für die komplette Liste.


===============================================================================
                              SUPPORT & KONTAKT
===============================================================================

Entwickelt von: AW Meta-Systems
Version: 2.0
Letzte Aktualisierung: November 2025

Bei Fragen oder Problemen wenden Sie sich bitte an AW (Technischer Support)


===============================================================================
                                 CHANGELOG
===============================================================================

Version 2.1: (November 2025)
• NEU: Intelligente Sammel-PDF Funktion mit Annotation-Merging
• NEU: Automatische Duplikat-Erkennung beim Kommentar-Import
• NEU: Drag & Drop Unterstützung für PDF-Dateien
• NEU: Erhaltung von Kommentar-Threads und Reply-Strukturen
• NEU: Automatisches Kopieren von Appearance Streams (/AP)
• Verbesserte pikepdf-Integration für professionelles PDF-Handling
• Optimierte Referenz-Reparatur für /IRT, /Parent, /Popup
• Detaillierte Konsolen-Ausgabe während der PDF-Erstellung
• Erweiterte Fehlerbehandlung und Validierung

Version 2.0: (November 2025)
• Implementierung des Timestamp-basierten Zählsystems
• Formatierte Zeitanzeige (DD.MM.YYYY HH:MM:SS)
• Verbesserte UI mit alternierenden Listenfarben
• Detaillierte Konsolen-Ausgabe mit Zeitstempeln
• Robuste Handhabung von Kommentaren ohne Zeitstempel
• Dark Mode / Light Mode Umschaltung

Version 1.0: (Initial Release)
• Basis-Funktionalität mit Typ-basierter Kommentar-Erkennung
• PDF-Export Funktion
• Grundlegende GUI

• Potenzielle .exe "Kopie" auf Anfrage beim Entwickler


===============================================================================
                              ABSCHLUSSWORT
===============================================================================

Der Commentary Counter wurde entwickelt, um die Arbeit mit kommentierten
PDF-Dokumenten zu erleichtern. Ob Sie im Verlagswesen arbeiten, wissenschaft-
liche Dokumente reviewen oder einfach nur Feedback von Kollegen zusammen-
führen möchten - dieses Tool bietet professionelle Funktionen, die sonst
nur in kostenpflichtiger Software zu finden sind.

Die Kombination aus präziser Timestamp-basierter Zählung und intelligentem
Annotation-Merging macht das Programm zu einem unverzichtbaren Werkzeug für
jeden, der regelmäßig mit kommentierten PDFs arbeitet.

Vielen Dank für die Nutzung des Commentary Counters!

                                                    - AW Meta-Systems


===============================================================================
                                    ENDE
===============================================================================
