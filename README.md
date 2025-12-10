# Commentary Counter — README & Dokumentation

Kurz: Der Commentary Counter ist ein Tool zur Analyse, Zählung und Zusammenführung von PDF‑Kommentare/Annotationen. Fokus: präzise Zählung per Timestamp, intelligentes Annotation‑Merging (pikepdf) und eine einfache GUI (tkinter).

## Inhaltsverzeichnis

- [Übersicht](#übersicht)
- [Hauptfunktionen](#hauptfunktionen)
- [Schnellstart](#schnellstart)
- [Funktionsweise der Kommentar‑Zählung](#funktionsweise-der-kommentar-zählung)
- [Timestamp‑basiertes Zählsystem](#timestamp-basiertes-zählsystem)
- [Sammel‑PDF (Annotation‑Merging)](#sammel-pdf-annotation-merging)
  - [Voraussetzungen](#voraussetzungen)
  - [Ablauf](#ablauf)
  - [Duplikat‑Erkennung](#duplikat-erkennung)
- [Benutzeroberfläche (UI)](#benutzeroberfläche-ui)
- [Technische Details](#technische-details)
- [Bekannte Besonderheiten & Performance](#bekannte-besonderheiten--performance)
- [FAQ](#faq)
- [Support & Kontakt](#support--kontakt)
- [Changelog](#changelog)

---

## Übersicht

Der Commentary Counter analysiert PDF‑Annotationen und zählt sie zuverlässig anhand von eindeutigen Zeitstempeln (creationDate / modDate). Zusätzlich können Kommentare aus mehreren PDF‑Versionen in eine einzelne Sammlung importiert werden (ohne Seiten zu duplizieren), wobei Kommentar‑Threads erhalten bleiben und doppelte Kommentare vermieden werden.

---

## Hauptfunktionen

- Zählung aller PDF‑Kommentare basierend auf eindeutigen Zeitstempeln
- Detaillierte Analyse: Seite, Typ, Autor, Inhalt, Zeitstempel
- Sammel‑PDF mit Annotation‑Merging (pikepdf)
- Automatische Duplikat‑Erkennung beim Import
- Drag & Drop Unterstützung (tkinterdnd2)
- Dark / Light Mode
- Konsolenausgabe mit formatierten Zeitstempeln

---

## Schnellstart

1. Installiere die benötigten Bibliotheken (Beispiel):
   - pip install pymupdf pikepdf tkinterdnd2
2. Starte das Programm (z. B. python main.py).
3. PDFs per Drag & Drop oder über "PDFs hinzufügen" in die Liste laden.
4. "Kommentare zählen" oder "Sammel‑PDF erstellen" wählen.

---

## Funktionsweise der Kommentar‑Zählung

Grundprinzip: Jeder Kommentar wird durch einen eindeutigen Zeitstempel identifiziert. Die Zählung basiert auf einer Menge einzigartiger Zeitstempel — 1 eindeutiger Timestamp = 1 Kommentar.

Algorithmus (Kurzfassung):
- Für jede Annotation: Typ, Autor, Inhalt, creationDate und modDate auslesen.
- Priorität: creationDate → modDate → Fallback (NO_TIMESTAMP_...).
- Füge Identifier in ein Set ein; daraus ergibt sich die Gesamtanzahl.
- Sammle zusätzlich detailierte Metadaten (Seite, Typ, Inhalt, formatiertes Datum).

---

## Timestamp‑basiertes Zählsystem

PDF‑interne Zeitstempel sehen z. B. so aus:

D:20251114091825+01'00'

Wird im Programm in ein lesbares Format konvertiert:
14.11.2025 09:18:25

Fallback (wenn kein Timestamp): NO_TIMESTAMP_1_[Typ]_[Autor]_[Seite]

Wichtig: Abweichungen gegenüber Adobe können auftreten, weil Adobe oft modDate anzeigt; die Zählgenauigkeit bleibt erhalten.

---

## Sammel‑PDF (Annotation‑Merging)

Zweck: Kommentare aus mehreren PDFs (verschiedene Versionen) in eine Basis‑PDF übernehmen, ohne Seiten zu verdoppeln.

### Voraussetzungen

- Alle PDFs sollten dieselbe Seitenanzahl und -reihenfolge haben.
- Idealerweise handelt es sich um dieselbe Dokumentbasis (Versionen mit Kommentaren).

Wenn Seitenanzahl/‑reihenfolge abweichen, können Kommentare auf falschen Seiten landen.

### Ablauf (technisch)

1. Basis‑PDF = erste Datei in der Liste (liefert alle Seiten).
2. Jede weitere Datei:
   - Seiten lesen, Annotationen extrahieren.
   - Annotationen via pikepdf.copy_foreign() in die Basis kopieren (AP Streams, Popups, Reply‑Threads bleiben erhalten).
3. Referenz‑Reparatur: IDs aus Quell‑PDF → neue IDs mappen und alle internen Referenzen (/IRT, /Parent, /Popup, /Next, /Prev) aktualisieren.
4. Vor dem Hinzufügen: Duplikat‑Prüfung.

### Duplikat‑Erkennung

Ein Kommentar gilt als Duplikat, wenn alle folgenden Kriterien übereinstimmen:
- gleicher Typ
- gleiche Position (Rect)
- gleicher Inhalt (Contents)
- gleiche QuadPoints (bei Markierungen)

Wenn mindestens ein Kriterium abweicht, wird der Kommentar hinzugefügt.

Dateiname der Ausgabe (Standard):
Kommentare_Sammlung_YYYYMMDD_HHMMSS.pdf

---

## Benutzeroberfläche (UI)

- Datei‑Liste mit alternierenden Hintergrundfarben
- Buttons:
  - PDFs hinzufügen (grün)
  - Ausgewählte entfernen (rot)
  - Alle entfernen
  - Kommentare zählen
  - Sammel‑PDF erstellen
- Dark / Light Mode (Toggle)
- Kommentar‑Details in der Konsole (sortiert nach Seite, Inhalte auf 80 Zeichen gekürzt)

Farbwerte sind in LIGHT_MODE und DARK_MODE Dictionaries im Code konfigurierbar.

---

## Technische Details

Verwendete Bibliotheken:
- tkinter (GUI)
- tkinterdnd2 (Drag & Drop)
- PyMuPDF (fitz) — Analyse und Zeitstempel‑Auslese
- pikepdf — Low‑Level PDF‑Manipulation & Annotation‑Merging
- pathlib, datetime, usw.

Warum zwei PDF‑Bibliotheken?
- PyMuPDF: schnell für Lesen/Analysieren von Annotationen
- pikepdf: präzise Manipulation auf Objekt‑/Referenz‑Ebene, nötig für robustes Merging

Beispiel für interne Datenstrukturen:
- unique_timestamps (Set)
- timestamp_details (Dict mit page/type/author/content/date)

---

## Bekannte Besonderheiten & Performance

- Kommentare ohne Zeitstempel → werden mit NO_TIMESTAMP_... versehen und einzeln gezählt.
- Mehrfach‑Annotationen an derselben Stelle (z. B. Highlight + Text) werden separat gezählt.
- Große PDFs (>1000 Seiten) können länger dauern; Laufzeit hängt von PDF‑Komplexität ab.
- Appearance Streams (/AP) werden beim Merging mitkopiert, sodass visuelle Darstellung erhalten bleibt.

---

## FAQ (Kurz)

- Kann ich PDFs mit unterschiedlicher Seitenzahl zusammenführen?
  - Nein, für korrektes Mapping müssen Seitenanzahl und Reihenfolge übereinstimmen.
- Was passiert bei mehrfach importiertem Kommentar?
  - Duplikat‑Erkennung verhindert doppelte Einträge.
- Werden Kommentar‑Threads erhalten?
  - Ja — interne Referenzen werden repariert.
- Kann ich mehr als 2 PDFs zusammenführen?
  - Ja — beliebig viele; erste Datei ist die Basis.
- Werden Zeichnungen, Stempel, Unterschriften kopiert?
  - Ja — alle Annotationstypen werden unterstützt.

---

## Support & Kontakt

Entwickelt von: AW Meta‑Systems  
Version: 2.1 (Stand: November 2025)

Bei Fragen oder Problemen: AW (Technischer Support)

---

## Changelog (Kurz)

- 2.1 — November 2025
  - Intelligente Sammel‑PDF Funktion (Annotation‑Merging)
  - Automatische Duplikat‑Erkennung
  - Drag & Drop
  - Erhaltung von Kommentar‑Threads, AP Streams
- 2.0 — November 2025
  - Timestamp‑basiertes Zählsystem
  - Dark/Light Mode, UI‑Verbesserungen
- 1.0 — Initial Release

---

Wenn du möchtest, übernehme ich diese überarbeitete README.md direkt ins Repository (Branch anlegen + PR öffnen) oder schicke dir nur den aktualisierten Inhalt zur weiteren Anpassung. Welche Option bevorzugst du?
