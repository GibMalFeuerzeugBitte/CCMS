"""
Commentary-Counter/Meta-Systems
Entwicklung: AW
Version: 6.1
Datum: 21.11.2025
Programmiersprache: Python 3.10+

Hauptfunktionen:
- Timestamp-basierte Kommentar-Zählung in PDFs
- Intelligentes Annotation-Merging mit pikepdf
- Automatische Duplikat-Erkennung
- Dark/Light Mode UI
"""

# ===== IMPORTS =====
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD   # DND = Drag & Drop
from pathlib import Path                        # Für Dateipfade
import fitz                                     # PyMuPDF für PDF-Analyse
import pikepdf                                  # pikepdf für Annotation-Merging
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# HILFSFUNKTIONEN FÜR DUPLIKAT-ERKENNUNG
# ═══════════════════════════════════════════════════════════════════════════════

def get_annotation_fingerprint(annot):
    """
    Erstellt einen eindeutigen Fingerprint für eine Annotation zur Duplikat-Erkennung.
    Kombiniert Subtype, Rect, Contents, QuadPoints (falls vorhanden).
    
    Args:
        annot: pikepdf.Dictionary - Die Annotation
    
    Returns:
        tuple: (Subtype, Rect, Contents, QuadPoints) oder None
    """
    if not isinstance(annot, pikepdf.Dictionary):
        return None
    
    try:
        # Basis: Subtype muss vorhanden sein
        subtype = str(annot.get("/Subtype", ""))
        if not subtype:
            return None
        
        # Rect (Position) - standardisiert als Tuple
        rect = annot.get("/Rect")
        rect_tuple = tuple(float(x) for x in rect) if rect else None
        
        # Contents (Text im Kommentar)
        contents = str(annot.get("/Contents", ""))
        
        # QuadPoints (bei Markierungen wie Highlight)
        quad_points = annot.get("/QuadPoints")
        quad_tuple = None
        if quad_points:
            try:
                quad_tuple = tuple(float(x) for x in quad_points)
            except:
                pass
        
        # Erstelle Fingerprint: (Subtype, Rect, Contents, QuadPoints)
        return (subtype, rect_tuple, contents, quad_tuple)
    
    except:
        return None


def is_duplicate(new_annot, existing_annots_on_page, base_pdf):
    """
    Prüft, ob new_annot bereits in existing_annots_on_page existiert.
    
    Args:
        new_annot: pikepdf.Dictionary - Die zu prüfende Annotation
        existing_annots_on_page: Array - Referenzen zu existierenden Annotationen
        base_pdf: pikepdf.Pdf - Die Basis-PDF zum Auflösen der Referenzen
    
    Returns:
        bool: True wenn Duplikat gefunden, False sonst
    """
    new_fingerprint = get_annotation_fingerprint(new_annot)
    if not new_fingerprint:
        return False  # Kann nicht vergleichen → nicht als Duplikat behandeln
    
    # Prüfe gegen alle existierenden Annotationen auf der Seite
    for existing_ref in existing_annots_on_page:
        try:
            if hasattr(existing_ref, 'objgen'):
                existing_annot = base_pdf.get_object(existing_ref.objgen)
            else:
                existing_annot = existing_ref
            
            existing_fingerprint = get_annotation_fingerprint(existing_annot)
            
            if existing_fingerprint and new_fingerprint == existing_fingerprint:
                return True  # Duplikat gefunden!
        except:
            continue
    
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# HAUPTFUNKTION: ANNOTATION-MERGING MIT PIKEPDF
# ═══════════════════════════════════════════════════════════════════════════════

def merge_annotations_pikepdf(base_pdf_path, source_pdf_paths, output_pdf_path):
    """
    Importiert nur die Annotationen aus source_pdf_paths in die base_pdf.
    Die Seiten werden NICHT kopiert - nur die Kommentare.
    
    Funktionsweise:
    1. Sammle alle Annotationen von den Seiten
    2. Ordne Annotationen den entsprechenden Seiten zu
    3. Kopiere Annotationen mit Duplikat-Prüfung
    4. Repariere interne Referenzen (IRT, Popup, Parent, etc.)
    
    Voraussetzung: Alle PDFs haben identische Seitenzahl und Seitenreihenfolge.
    
    Args:
        base_pdf_path: str - Die Ziel-PDF (z.B. PDF1 mit allen Seiten)
        source_pdf_paths: list - Liste der PDFs, aus denen nur Annotationen kopiert werden
        output_pdf_path: str - Ausgabedatei
    """
    base = pikepdf.Pdf.open(base_pdf_path)

    # global mapping: (pdf_index, old_objgen) → new_objgen
    global_map = {}

    for pdf_index, src_path in enumerate(source_pdf_paths):
        src = pikepdf.Pdf.open(src_path)

        # 1) Sammle erst alle Annotationen direkt von den Seiten
        local_map = {}
        annotations_to_copy = set()  # Set verhindert Duplikate

        # Durchlaufe alle Seiten und sammle deren Annotationen
        for src_page in src.pages:
            if "/Annots" not in src_page:
                continue
            
            for ref in src_page["/Annots"]:
                if hasattr(ref, 'objgen'):
                    try:
                        annot_obj = src.get_object(ref.objgen)
                        if isinstance(annot_obj, pikepdf.Dictionary) and annot_obj.get("/Subtype"):
                            annotations_to_copy.add(annot_obj.objgen)
                    except:
                        pass

        # 2) Annotationen zu den entsprechenden Seiten zuordnen
        page_annotations = {}  # page_idx -> [annotations]
        
        for src_page_idx, src_page in enumerate(src.pages):
            if "/Annots" not in src_page:
                continue
            
            page_annots = []
            for ref in src_page["/Annots"]:
                if hasattr(ref, 'objgen'):
                    # Nur Annotationen die wir vorher gesammelt haben
                    if ref.objgen in annotations_to_copy:
                        try:
                            annot_obj = src.get_object(ref.objgen)
                            page_annots.append(annot_obj)
                        except:
                            pass
            
            if page_annots:
                page_annotations[src_page_idx] = page_annots

        # 3) Kopiere Annotationen und füge sie zu den richtigen Seiten hinzu
        # WICHTIG: Kein Offset mehr, da alle PDFs gleiche Seitenanzahl haben
        for src_page_idx, annots in page_annotations.items():
            # Direkte 1:1 Zuordnung: Seite N aus Source → Seite N in Base
            if src_page_idx >= len(base.pages):
                continue
                
            base_page = base.pages[src_page_idx]

            # Erstelle Annots Array falls nicht vorhanden
            if "/Annots" not in base_page:
                base_page["/Annots"] = pikepdf.Array([])

            for annot in annots:
                # Kopiere die Annotation
                new_annot = base.copy_foreign(annot)
                
                # DUPLIKAT-PRÜFUNG: Überspringe, wenn bereits vorhanden
                if is_duplicate(new_annot, base_page["/Annots"], base):
                    continue  # Diese Annotation bereits vorhanden → nicht erneut hinzufügen
                
                # Speichere Mapping für spätere Referenz-Reparatur
                local_map[annot.objgen] = new_annot.objgen
                global_map[(pdf_index, annot.objgen)] = new_annot.objgen
                
                # KRITISCH: Entferne alte /P Referenz falls vorhanden und setze neue
                if '/P' in new_annot:
                    del new_annot['/P']
                new_annot['/P'] = base_page.obj
                
                # Stelle sicher dass /Rect vorhanden ist (manche Annotationen brauchen das)
                if '/Rect' not in new_annot:
                    new_annot['/Rect'] = pikepdf.Array([0, 0, 0, 0])
                
                # Füge zur Seite hinzu (copy_foreign() kopiert automatisch /AP Appearance Streams)
                base_page["/Annots"].append(new_annot)
        
        # 4) Repariere interne Referenzen (IRT, Popup, etc.)
        for old_objgen, new_objgen in local_map.items():
            annot = base.get_object(new_objgen)

            if not isinstance(annot, pikepdf.Dictionary):
                continue

            for key in ["/IRT", "/Parent", "/Popup", "/Next", "/Prev"]:
                if key in annot:
                    ref = annot[key]
                    if hasattr(ref, 'objgen'):
                        lookup = (pdf_index, ref.objgen)
                        if lookup in global_map:
                            annot[key] = base.get_object(global_map[lookup])

        src.close()

    base.save(output_pdf_path)
    base.close()


def filter_commented_pages_only(source_pdf_path, output_pdf_path):
    """
    Erstellt eine neue PDF mit nur den Seiten, die Kommentare enthalten.
    
    Funktionsweise:
    1. Öffnet die Quell-PDF
    2. Prüft jede Seite auf /Annots
    3. Behält nur Seiten mit Annotationen
    4. Speichert neue PDF mit gefilterten Seiten
    
    Args:
        source_pdf_path: str - Die Quell-PDF
        output_pdf_path: str - Die Ausgabe-PDF
    
    Returns:
        int: Anzahl der behaltenen Seiten
    """
    src = pikepdf.Pdf.open(source_pdf_path)
    output = pikepdf.Pdf.new()
    
    pages_kept = 0
    
    # Durchlaufe alle Seiten und kopiere nur die mit Annotationen
    for page_num, page in enumerate(src.pages):
        # Prüfe ob Seite Annotationen hat
        if "/Annots" in page and page["/Annots"]:
            # Prüfe ob das Annots-Array nicht leer ist
            if len(page["/Annots"]) > 0:
                # Seite hat Kommentare → behalten
                output.pages.append(page)
                pages_kept += 1
    
    # Speichere nur wenn mindestens eine Seite Kommentare hat
    if pages_kept > 0:
        output.save(output_pdf_path)
    
    src.close()
    output.close()
    
    return pages_kept


# ═══════════════════════════════════════════════════════════════════════════════
# HAUPTKLASSE: COMMENTARY COUNTER
# ═══════════════════════════════════════════════════════════════════════════════

class CommentaryCounter:
    """
    Hauptklasse für den Commentary Counter.
    
    Features:
    - Timestamp-basierte Kommentar-Zählung
    - Annotation-Merging ohne Seiten-Duplizierung
    - Drag & Drop Unterstützung
    - Dark/Light Mode
    """
    
    # ─────────────────────────────────────────────────────────────────────────
    # FARBSCHEMATA
    # ─────────────────────────────────────────────────────────────────────────
    
    LIGHT_MODE = {
        'bg_main': '#CDCDCD',           # Haupthintergrund
        'bg_frame': '#E8E8E8',          # Frame-Hintergrund
        'bg_listbox': '#DDD7D7',        # Listbox-Hintergrund
        'bg_console': '#DDD7D7',        # Konsolen-Hintergrund
        'fg_text': '#000000',           # Textfarbe
        'fg_label': '#000000',          # Label-Textfarbe
        'btn_primary': '#4CAF50',       # Primäre Buttons (Grün)
        'btn_primary_hover': '#45A049', # Primäre Buttons Hover
        'btn_add': '#4CAF50',           # Hinzufügen-Button
        'btn_danger': '#f44336',        # Löschen-Buttons (Rot)
        'select_bg': '#4CAF50',         # Auswahl-Hintergrund
        'listbox_alt1': '#E8E8E8',      # Alternierende Farbe 1
        'listbox_alt2': '#F5F5F5'       # Alternierende Farbe 2
    }
    
    DARK_MODE = {
        'bg_main': '#2b2b2b',           # Haupthintergrund
        'bg_frame': '#3c3c3c',          # Frame-Hintergrund
        'bg_listbox': '#1e1e1e',        # Listbox-Hintergrund
        'bg_console': '#1a1a1a',        # Konsolen-Hintergrund
        'fg_text': '#e0e0e0',           # Textfarbe
        'fg_label': '#ffffff',          # Label-Textfarbe
        'btn_primary': '#2a4d7c',       # Primäre Buttons (dunkles Blau)
        'btn_primary_hover': '#2a4d7c', # Primäre Buttons Hover
        'btn_add': '#2a4d7c',           # Hinzufügen-Button (dunkelgrün)
        'btn_danger': '#5f1e1e',        # Löschen-Buttons (dunkelrot)
        'select_bg': '#4a5f7f',         # Auswahl-Hintergrund (mittleres Blau)
        'listbox_alt1': '#252525',      # Alternierende Farbe 1
        'listbox_alt2': '#2d2d2d'       # Alternierende Farbe 2
    }
    
    # ─────────────────────────────────────────────────────────────────────────
    # INITIALISIERUNG
    # ─────────────────────────────────────────────────────────────────────────
    
    def __init__(self, root):
        """Initialisiert die Anwendung mit allen notwendigen Variablen"""
        self.root = root
        self.root.title("Commentary-Counter/Meta-Systems")
        self.root.geometry("800x850")
        
        # Setze Fenster-Icon (falls vorhanden)
        try:
            import sys
            # Wenn als .exe gepackt, liegt das Icon im temporären _MEIPASS Ordner
            if getattr(sys, 'frozen', False):
                # PyInstaller erstellt einen temporären Ordner und speichert den Pfad in _MEIPASS
                base_path = Path(sys._MEIPASS)
            else:
                base_path = Path(__file__).parent
            
            icon_path = base_path / "Logo" / "favicon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass  # Falls Icon nicht gefunden, einfach weitermachen
        
        self.pdf_files = []                             # Liste aller ausgewählten PDF-Dateien
        self.total_comments = 0                         # Gesamtanzahl der gezählten Kommentare
        self.dark_mode = False                          # Standard: Light Mode
        self.colors = self.LIGHT_MODE                   # Aktives Farbschema
        self.setup_ui()
    
    # ─────────────────────────────────────────────────────────────────────────
    # UI-AUFBAU
    # ─────────────────────────────────────────────────────────────────────────
    
    def setup_ui(self):
        """Erstellt die komplette Benutzeroberfläche"""
        # Hintergrundfarbe setzen
        self.root.configure(bg=self.colors['bg_main'])

        # BEREICH 1: PDF-Datei-Auswahl
        # Frame für PDF-Auswahl
        self.file_frame = tk.LabelFrame(
            self.root, 
            text="PDF-Dateien", 
            padx=10, 
            pady=10,
            bg=self.colors['bg_frame'],
            fg=self.colors['fg_label'],
            font=('Arial', 10, 'bold')
        )
        self.file_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Listbox mit Scrollbar
        self.file_scrollbar = tk.Scrollbar(self.file_frame)
        self.file_scrollbar.pack(side="right", fill="y")
        
        self.file_listbox = tk.Listbox(
            self.file_frame, 
            yscrollcommand=self.file_scrollbar.set,
            selectmode=tk.EXTENDED,
            font=("Verdana", 12),                        # Größere Schrift
            activestyle='none',                          # Deaktiviert den Fokus-Rahmen
            bg=self.colors['bg_listbox'],
            fg=self.colors['fg_text'],
            selectbackground=self.colors['select_bg'],
            selectforeground='white',
            highlightthickness=0
        )
        self.file_listbox.pack(fill="both", expand=True)
        self.file_scrollbar.config(command=self.file_listbox.yview)
        
        # Bind für alternierenden Hintergrund
        self.file_listbox.bind('<<ListboxSelect>>', self.update_selection_colors)
        
        # === DRAG & DROP FUNKTIONALITÄT ===
        # Aktiviere Drag & Drop für die Listbox
        self.file_listbox.drop_target_register('DND_Files')
        self.file_listbox.dnd_bind('<<Drop>>', self.drop_files)
        
        # Aktions-Buttons für Dateiverwaltung (Hinzufügen, Entfernen, Löschen)
        # Buttons für Dateiauswahl
        self.button_frame = tk.Frame(self.file_frame, bg=self.colors['bg_frame'])
        self.button_frame.pack(fill="x", pady=5)
        
        self.add_button = tk.Button(
            self.button_frame, 
            text="PDFs hinzufügen", 
            command=self.add_pdfs,
            bg=self.colors['btn_add'],
            fg="white",
            padx=10
        )
        self.add_button.pack(side="left", padx=5)
        
        self.remove_button = tk.Button(
            self.button_frame, 
            text="Ausgewählte entfernen", 
            command=self.remove_selected,
            bg=self.colors['btn_danger'],
            fg="white",
            padx=10
        )
        self.remove_button.pack(side="left", padx=5)
        
        self.clear_button = tk.Button(
            self.button_frame, 
            text="Alle entfernen", 
            command=self.clear_all,
            bg=self.colors['btn_danger'],
            fg="white",
            padx=10
        )
        self.clear_button.pack(side="left", padx=5)
        
        # BEREICH 2: Ergebnis-Anzeige
        # Zeigt die Gesamtanzahl der gezählten Kommentare an
        # Ergebnis-Frame
        self.result_frame = tk.LabelFrame(
            self.root, 
            text="Zählung", 
            padx=10, 
            pady=10,
            bg=self.colors['bg_frame'],
            fg=self.colors['fg_label'],
            font=('Arial', 10, 'bold')
        )
        self.result_frame.pack(fill="x", padx=10, pady=5)
        
        self.result_label = tk.Label(
            self.result_frame, 
            text="Warte auf Zählung...",
            font=("Arial", 12),
            bg=self.colors['bg_frame'],
            fg=self.colors['fg_text']
        )
        self.result_label.pack(pady=5)
        
        # BEREICH 3: Detail-Konsole
        # Zeigt detaillierte Informationen zu jedem gefundenen Kommentar
        # Konsole für Details
        self.console_frame = tk.LabelFrame(
            self.root, 
            text="Kommentar-Details", 
            padx=10, 
            pady=10,
            bg=self.colors['bg_frame'],
            fg=self.colors['fg_label'],
            font=('Arial', 10, 'bold')
        )
        self.console_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.console_scrollbar = tk.Scrollbar(self.console_frame)
        self.console_scrollbar.pack(side="right", fill="y")
        
        self.console_text = tk.Text(
            self.console_frame,
            height=10,
            yscrollcommand=self.console_scrollbar.set,
            font=("Courier", 9),
            wrap=tk.WORD,
            bg=self.colors['bg_console'],
            fg=self.colors['fg_text'],
            insertbackground=self.colors['fg_text'],
            selectbackground=self.colors['select_bg'],
            highlightthickness=0
        )
        self.console_text.pack(fill="both", expand=True)
        self.console_scrollbar.config(command=self.console_text.yview)
        
        # BEREICH 4: Hauptaktionen
        # Buttons für Kommentar-Zählung, PDF-Merge, Kommentar-Filterung
        # Aktions-Buttons
        self.action_frame = tk.Frame(self.root, bg=self.colors['bg_main'])
        self.action_frame.pack(fill="x", padx=10, pady=10)
        
        self.count_button = tk.Button(
            self.action_frame, 
            text="Kommentare zählen", 
            command=self.count_comments,
            bg=self.colors['btn_primary'],
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        self.count_button.pack(side="left", padx=5, expand=True, fill="x")
        
        self.export_button = tk.Button(
            self.action_frame, 
            text="Sammel-PDF erstellen",
            command=self.export_comments,
            bg=self.colors['btn_primary'],
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        self.export_button.pack(side="left", padx=5, expand=True, fill="x")
        
        self.filter_button = tk.Button(
            self.action_frame, 
            text="Kommentierte Seiten",
            command=self.filter_commented_pages,
            bg=self.colors['btn_primary'],
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        self.filter_button.pack(side="left", padx=5, expand=True, fill="x")
        
        # Dark/Light Mode Toggle Button (im action_frame rechts)
        self.toggle_button = tk.Button(
            self.action_frame,
            text="🌙 Dark Mode",
            command=self.toggle_theme,
            bg=self.colors['bg_frame'],
            fg=self.colors['fg_text'],
            font=("Arial", 10),
            padx=10,
            pady=10
        )
        self.toggle_button.pack(side="right", padx=5)
    
    # ─────────────────────────────────────────────────────────────────────────
    # UI-HILFSFUNKTIONEN
    # ─────────────────────────────────────────────────────────────────────────
    
    def update_selection_colors(self, event=None):
        """Aktualisiert die Hintergrundfarben bei Selektion"""
        pass  # Event-Handler für zukünftige Erweiterungen
    
    def update_listbox_colors(self):
        """Fügt alternierende Hintergrundfarben hinzu"""
        for i in range(self.file_listbox.size()):
            if i % 2 == 0:
                self.file_listbox.itemconfig(i, bg=self.colors['listbox_alt1'], selectbackground=self.colors['select_bg'])
            else:
                self.file_listbox.itemconfig(i, bg=self.colors['listbox_alt2'], selectbackground=self.colors['select_bg'])
    
    def toggle_theme(self):
        """Wechselt zwischen Dark Mode und Light Mode"""
        self.dark_mode = not self.dark_mode
        self.colors = self.DARK_MODE if self.dark_mode else self.LIGHT_MODE
        
        # Aktualisiere alle UI-Elemente mit neuen Farben
        self.root.configure(bg=self.colors['bg_main'])
        
        # Frames
        self.file_frame.configure(bg=self.colors['bg_frame'], fg=self.colors['fg_label'])
        self.button_frame.configure(bg=self.colors['bg_frame'])
        self.result_frame.configure(bg=self.colors['bg_frame'], fg=self.colors['fg_label'])
        self.console_frame.configure(bg=self.colors['bg_frame'], fg=self.colors['fg_label'])
        self.action_frame.configure(bg=self.colors['bg_main'])
        
        # Listbox
        self.file_listbox.configure(
            bg=self.colors['bg_listbox'],
            fg=self.colors['fg_text'],
            selectbackground=self.colors['select_bg']
        )
        self.update_listbox_colors()
        
        # Labels
        self.result_label.configure(bg=self.colors['bg_frame'], fg=self.colors['fg_text'])
        
        # Console
        self.console_text.configure(
            bg=self.colors['bg_console'],
            fg=self.colors['fg_text'],
            insertbackground=self.colors['fg_text'],
            selectbackground=self.colors['select_bg']
        )
        
        # Buttons
        self.add_button.configure(bg=self.colors['btn_add'])
        self.remove_button.configure(bg=self.colors['btn_danger'])
        self.clear_button.configure(bg=self.colors['btn_danger'])
        self.count_button.configure(bg=self.colors['btn_primary'])
        self.export_button.configure(bg=self.colors['btn_primary'])
        self.filter_button.configure(bg=self.colors['btn_primary'])
        
        # Toggle Button Text und Farbe
        if self.dark_mode:
            self.toggle_button.configure(text="☀️ Light Mode", bg=self.colors['bg_frame'], fg=self.colors['fg_text'])
        else:
            self.toggle_button.configure(text="🌙 Dark Mode", bg=self.colors['bg_frame'], fg=self.colors['fg_text'])
    
    def format_pdf_date(self, pdf_date):
        """Konvertiert PDF-Datumsformat in lesbares Format: DD.MM.YYYY HH:MM:SS"""
        try:
            # PDF-Format: D:20251114091825+01'00'
            # Extrahiere nur die relevanten Zeichen
            if pdf_date.startswith('D:'):
                pdf_date = pdf_date[2:]
            
            # Entferne Zeitzone und andere Zeichen
            date_part = pdf_date.split('+')[0].split('-')[0].split('Z')[0]
            
            # Parse: YYYYMMDDHHMMSS
            if len(date_part) >= 14:
                year = date_part[0:4]
                month = date_part[4:6]
                day = date_part[6:8]
                hour = date_part[8:10]
                minute = date_part[10:12]
                second = date_part[12:14]
                return f"{day}.{month}.{year} {hour}:{minute}:{second}"
            elif len(date_part) >= 8:
                year = date_part[0:4]
                month = date_part[4:6]
                day = date_part[6:8]
                return f"{day}.{month}.{year}"
            else:
                return pdf_date
        except:
            return pdf_date  # Bei Fehler Original zurückgeben
    
    # ─────────────────────────────────────────────────────────────────────────
    # DATEIVERWALTUNG
    # ─────────────────────────────────────────────────────────────────────────
    
    def drop_files(self, event):
        """Verarbeitet Drag & Drop von Dateien"""
        # Hole die gedroppten Dateien
        files = self.file_listbox.tk.splitlist(event.data)
        
        for file_path in files:
            # Bereinige den Pfad (entferne geschweifte Klammern falls vorhanden)
            file_path = file_path.strip('{}')
            
            # Prüfe ob es eine PDF-Datei ist
            if file_path.lower().endswith('.pdf'):
                if file_path not in self.pdf_files:
                    self.pdf_files.append(file_path)
                    self.file_listbox.insert(tk.END, Path(file_path).name)
        
        self.update_listbox_colors()
    
    def add_pdfs(self):
        files = filedialog.askopenfilenames(
            title="PDF-Dateien auswählen",
            filetypes=[("PDF-Dateien", "*.pdf")]
        )
        for file in files:
            if file not in self.pdf_files:
                self.pdf_files.append(file)
                self.file_listbox.insert(tk.END, Path(file).name)
        self.update_listbox_colors()
    
    def remove_selected(self):
        selected = self.file_listbox.curselection()
        for index in reversed(selected):
            self.file_listbox.delete(index)
            self.pdf_files.pop(index)
        self.update_listbox_colors()
    
    def clear_all(self):
        self.file_listbox.delete(0, tk.END)
        self.pdf_files.clear()
        self.result_label.config(text="Warte auf Zählung...")
    
    # ─────────────────────────────────────────────────────────────────────────
    # KOMMENTAR-ZÄHLUNG (HAUPTFUNKTION 1)
    # ─────────────────────────────────────────────────────────────────────────
    
    def count_comments(self):
        """EINFACHE EINDEUTIGE ZÄHLUNG: Zählt ALLE physischen Annotationen in PDFs"""
        if not self.pdf_files:
            messagebox.showwarning("Keine Dateien", "Bitte fügen Sie zuerst PDF-Dateien hinzu.")
            return
        
        self.total_comments = 0
        comments_per_file = []
        self.console_text.delete(1.0, tk.END)
        self.console_text.insert(tk.END, "=== KOMMENTAR-ZÄHLUNG (Physische Annotationen) ===\n\n")
        
        try:
            # Durchlaufe alle ausgewählten PDF-Dateien
            for pdf_path in self.pdf_files:
                doc = fitz.open(pdf_path)
                file_comments = 0
                filename = Path(pdf_path).name
                
                self.console_text.insert(tk.END, f"📄 {filename}\n")    #Dieser Emoji ist nicht KI-generiert, er soll in der Konsolenausgabe angezeigt werden
                self.console_text.insert(tk.END, "-" * 60 + "\n")
                
                # Zähle wie Adobe: NUR Haupt-Kommentare, IRT-Antworten werden NICHT mitgezählt
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    annotations = page.annots()
                    
                    if not annotations:
                        continue
                    
                    for annot in annotations:
                        annot_type = annot.type[1] if annot.type else "Unknown"
                        annot_info = annot.info
                        author = annot_info.get("title", "Unbekannt")
                        content = annot_info.get("content", "")
                        creation_date = annot_info.get("creationDate", "")
                        mod_date = annot_info.get("modDate", "")
                        
                        # Prüfe ob es eine Antwort ist (hat /IRT Referenz)
                        is_reply = False
                        try:
                            xref = annot.xref
                            if xref > 0:
                                annot_dict = doc.xref_object(xref)
                                if "/IRT" in annot_dict:
                                    is_reply = True
                        except:
                            pass
                        
                        # Zähle NUR wenn es KEINE Antwort ist (wie Adobe)
                        if not is_reply:
                            file_comments += 1
                            
                            # Zeig nur Haupt-Kommentare
                            indent = "  "
                            self.console_text.insert(tk.END,
                                f"{indent}S.{page_num + 1} | {annot_type} | {author}\n")
                            
                            if content:
                                preview = content[:80] + "..." if len(content) > 80 else content
                                self.console_text.insert(tk.END, f"{indent}  → {preview}\n")
                            
                                date = creation_date or mod_date
                                if date:
                                    formatted_date = self.format_pdf_date(date)
                                    self.console_text.insert(tk.END, f"{indent}  📅 {formatted_date}\n") #Dieser Emoji ist nicht KI-generiert
                                
                                self.console_text.insert(tk.END, "\n")
                
                self.console_text.insert(tk.END, f"  ✓ Gesamt: {file_comments} Kommentare\n\n")
                comments_per_file.append((filename, file_comments))
                self.total_comments += file_comments
                doc.close()
                
                self.console_text.see(tk.END)
                self.root.update_idletasks()
            
            result_text = f"Gesamtanzahl: {self.total_comments} Kommentare\n\nDetails:\n"
            for filename, count in comments_per_file:
                result_text += f"  • {filename}: {count}\n"
            
            self.result_label.config(text=f"Gesamt: {self.total_comments} Kommentare")
            messagebox.showinfo("Zählergebnis", result_text)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Zählen:\n{str(e)}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # SAMMEL-PDF ERSTELLEN (HAUPTFUNKTION 2)
    # ─────────────────────────────────────────────────────────────────────────
    
    def export_comments(self):
        """Erstellt eine Sammel-PDF: PDF1 als Basis + Kommentare aus PDF2, PDF3, ... (ohne deren Seiten)"""
        if not self.pdf_files:
            messagebox.showwarning("Keine Dateien", "Bitte fügen Sie zuerst PDF-Dateien hinzu.")
            return

        if len(self.pdf_files) < 2:
            messagebox.showwarning("Zu wenige Dateien", "Bitte fügen Sie mindestens 2 PDF-Dateien hinzu.\n\nDie erste PDF dient als Basis (mit allen Seiten),\naus den weiteren PDFs werden nur die Kommentare importiert.")
            return

        output_file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF-Dateien", "*.pdf")],
            initialfile=f"Kommentare_Sammlung_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        if not output_file:
            return

        try:
            self.console_text.insert(tk.END, "\n" + "=" * 60 + "\n")
            self.console_text.insert(tk.END, "SAMMEL-PDF WIRD ERSTELLT …\n")
            self.console_text.insert(tk.END, "=" * 60 + "\n\n")
            self.console_text.insert(tk.END, f"Basis-PDF: {Path(self.pdf_files[0]).name}\n")
            self.console_text.insert(tk.END, f"Importiere Kommentare aus {len(self.pdf_files) - 1} weiteren PDF(s)\n\n")

            # ==========================
            # ANNOTATION-MERGE
            # ==========================
            # PDF1 = Basis (alle Seiten)
            # PDF2, PDF3, ... = nur Kommentare importieren
            
            base_path = self.pdf_files[0]
            source_paths = self.pdf_files[1:]  # Alle außer der ersten
            
            merge_annotations_pikepdf(base_path, source_paths, output_file)

            self.console_text.insert(tk.END, f"Fertig! Datei gespeichert:\n{output_file}\n")
            self.console_text.insert(tk.END, "=" * 60 + "\n\n")
            self.console_text.see(tk.END)

            messagebox.showinfo("Erfolg", f"Sammel-PDF erstellt:\n{Path(output_file).name}")

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen:\n{str(e)}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # KOMMENTIERTE SEITEN FILTERN (HAUPTFUNKTION 3)
    # ─────────────────────────────────────────────────────────────────────────
    
    def filter_commented_pages(self):
        """Erstellt eine neue PDF mit nur den Seiten, die Kommentare enthalten"""
        if not self.pdf_files:
            messagebox.showwarning("Keine Dateien", "Bitte fügen Sie zuerst eine PDF-Datei hinzu.")
            return
        
        if len(self.pdf_files) > 1:
            response = messagebox.askyesno(
                "Mehrere Dateien",
                "Sie haben mehrere PDFs ausgewählt.\n\nNur die ERSTE PDF wird gefiltert.\n\nFortfahren?"
            )
            if not response:
                return
        
        source_pdf = self.pdf_files[0]
        
        # Ausgabedatei auswählen
        suggested_name = Path(source_pdf).stem + "_Kommentierte_Seiten.pdf"
        output_file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF-Dateien", "*.pdf")],
            initialfile=suggested_name
        )
        
        if not output_file:
            return
        
        try:
            self.console_text.insert(tk.END, "\n" + "=" * 60 + "\n")
            self.console_text.insert(tk.END, "KOMMENTIERTE SEITEN WERDEN EXTRAHIERT …\n")
            self.console_text.insert(tk.END, "=" * 60 + "\n\n")
            self.console_text.insert(tk.END, f"Quelle: {Path(source_pdf).name}\n")
            self.console_text.see(tk.END)
            self.root.update_idletasks()
            
            # Filtere Seiten
            pages_kept = filter_commented_pages_only(source_pdf, output_file)
            
            if pages_kept > 0:
                self.console_text.insert(tk.END, f"\n✔ {pages_kept} Seite(n) mit Kommentaren behalten\n")
                self.console_text.insert(tk.END, f"✔ Fertig! Datei gespeichert:\n{output_file}\n")
                self.console_text.insert(tk.END, "=" * 60 + "\n\n")
                self.console_text.see(tk.END)
                
                messagebox.showinfo(
                    "Erfolg", 
                    f"Kommentierte Seiten extrahiert:\n\n{pages_kept} Seite(n) behalten\n\nGespeichert als:\n{Path(output_file).name}"
                )
            else:
                self.console_text.insert(tk.END, "⚠ Keine Seiten mit Kommentaren gefunden!\n") #Nein. auch dieser Emoji ist nicht KI-generiert
                self.console_text.insert(tk.END, "=" * 60 + "\n\n")
                self.console_text.see(tk.END)
                
                messagebox.showwarning(
                    "Keine Kommentare",
                    "Die PDF enthält keine Seiten mit Kommentaren.\n\nEs wurde keine Datei erstellt."
                )
        
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Filtern:\n{str(e)}")


# ═══════════════════════════════════════════════════════════════════════════════
# PROGRAMM-START
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # TkinterDnD Root für Drag & Drop Support
    app = CommentaryCounter(root)
    root.mainloop()

""" 
Support ist kein Mord, also ünterstützt mein PayPal ;)
Während des Erstellungsprozesses, habe ich einen Bug in Adobe gefunden,
welcher bei meinem PDF-Merge nicht auftritt. "Beweis Screenshot unter Bildschirmfotos"
Vielleicht zahlt mir Adobe ja eine Prämie für das melden, außer ihr seit schneller.
Wünsche viel Spaß mit dem Tool!
"""