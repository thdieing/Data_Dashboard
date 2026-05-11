"""
Umfrage-Datenexplorer — Streamlit-Dashboard für uni- und bivariate Analysen.

Verwendung:
    1. Diese Datei in dasselbe Verzeichnis wie survey_raw.rds legen.
    2. Ausführen: streamlit run dashboard.py

Abhängigkeiten:
    pip install streamlit pandas pyreadr plotly
"""
#thiloid@Thilos-MacBook-Pro ~ % conda activate unitenv
#(unitenv) thiloid@Thilos-MacBook-Pro ~ % streamlit run /Users/thiloid/Desktop/zvv_dashboard/dashboard.py  
import os
import tempfile
import warnings

import pandas as pd
import plotly.express as px
import streamlit as st

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# ── KONFIGURATION — hier anpassen ────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

# Dateiname der RDS-Datei (muss im selben Ordner liegen)
DATA_FILE = "survey_raw.rds"

# Welche Spalten sollen in der Analyse verfügbar sein?
INCLUDED_VARIABLES = [
    "Z1",
    "A0WQ",
    "A0Pr",
    "A11EN_a1",
    "A12EN_a1","MK19_a1", "MK19_a2", "MK19_a3","MK19_a5","MK19_a7","MK19_a9","MK19_a10","MK19_a11","MK19_a12","MK19_a13"
    "MK19_a14","MK20_a1","MK20_a2","MK20_a3","MK20_a4","MK20_a5","MK20_a6","MK20_a7","MK20_a8","MK20_a9","MK20_a10","MK20_a11"
    "MK20_a12","MK20_a13", "MK17_a1","MK17_a2", "MK17_a3", "MK17_a4", "MK17_a5", "MK17_a6", "MK17_a7", "MK17_a8","MK17_a9", 
    "MK04_a1","MK12_a1","MK13_a1","A121_a1","A121_a2", "A121_a3", "A121_a4", "A121_a5", "A121_a7", "A121P_a1",
    "A121P_a2", "A121P_a3", "A121P_a4", "A121P_a5", "A121P_a6", "A121P_a7", "HBA121_a1","A122_a1","HBA122_a1","A123_a1","A123_a2"
    "A91_a1", "K1", "K2", "K3", "K4_a1", "K5_a1", "K6Uni_a1","K8P_a1", "K8P_a2", "K8W_a1", "K8W_a2", 
    "AOBer","MK15_a1","MK16_a1"

]
   
# Spaltenerklärungen: Variablenname → deutsche Beschreibung
COLUMN_DESCRIPTIONS = {
    "Z1": {
        "label": "Beschäftigungsgruppe",
        "Frage Item": "Im Folgenden werden Ihnen Ihrer beruflichen Beschäftigtengruppe entsprechende Fragen gestellt. Um den für Sie passenden Fragebogen zu erhalten, ordnen Sie sich bitte zunächst einer der Beschäftigtengruppen zu. In der TU Darmstadt gibt es vielfältige Arbeitskontexte. Daher werden Ihnen in diesem Fragebogen Themen begegnen, von denen Sie nicht betroffen sind. Bitte nutzen Sie bei diesen Fragen das Feld „keine Angabe“. Wenn Sie mehreren Beschäftigtengruppen angehören, entscheiden Sie sich bitte für die Beschäftigtengruppe, die für Ihre Arbeitssituation die größte Bedeutung hat.",
        "werte": "Professor:innen; Wissenschaftliche Mitarbeiter:innen; Mitarbeiter:in in Administration und Technik (ATM) in einem Fachbereich; Mitarbeiter:in in Administration und Technik (ATM) in einer zentralen Einheit (ZV, ZE, etc.)",
        "filter":"",
    },

     "A0WQ": {
        "label": "Qualifikationsziel",
        "Frage Item": "Welches wissenschaftliche Qualifikationsziel verfolgen Sie / in welcher Qualifikationsphase befinden Sie sich?",
        "werte": "ohne Qualifikationsziel; Promotion; Postdoc (z. B. Habilitation); keine Angabe",
        "filter":"Z1: Nur Wissenschaftliche Mitarbeiter:innen",
    },
       "A0Pr": {
        "label": "Karriereziel",
        "Frage Item": "Welches Karriereziel verfolgen Sie?",
        "werte": "Karriere in wissenschaftlichen Einrichtungen; Karriere außerhalb wissenschaftlicher Einrichtungen; Ich bin noch nicht sicher; keine Angabe",
        "filter":"A0WQ: Promotion",
    },
       "A11EN_a1": {
        "label": "Arbeitszufriedenheit insgesamt",
        "Frage Item": "Wenn Sie an alles denken, was für Ihre Arbeit an der TU Darmstadt eine Rolle spielt, wie zufrieden sind Sie dann insgesamt mit Ihrer Arbeitssituation?",
        "werte": "sehr zufrieden; eher zufrieden; teils / teils; eher nicht zufrieden; gar nicht zufrieden; keine Angabe",
        "filter":"",
    },
        "A12EN_a1": {
        "label": "Anerkennung insgesamt",
        "Frage Item": "Wenn ich an meine erbrachten Leistungen und Anstrengungen denke, halte ich die erfahrene Anerkennung für angemessen.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK19_a1": {
        "label": "Organisationale Bindung Item 1",
        "Frage Item": "Ich empfinde es als angenehm, bei der TU Darmstadt zu arbeiten.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },

        "MK19_a2": {
        "label": "Organisationale Bindung Item 2",
        "Frage Item": "Ich fühle mich mit der TU Darmstadt persönlich verbunden.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK19_a3": {
        "label": "Organisationale Bindung Item 3",
        "Frage Item": "Ich fände es persönlich schade, wenn die Beschäftigung bei der TU Darmstadt enden würde.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK19_a5": {
        "label": "Organisationale Bindung Item 4",
        "Frage Item": "Meine persönlichen Kontakte zu meinem Arbeitsumfeld sind für mich von Bedeutung.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK19_a7": {
        "label": "Organisationale Bindung Item 5",
        "Frage Item": "Ich bin auf die TU Darmstadt angewiesen, weil es zurzeit keine gleichwertigen Alternativen am Markt gibt.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK19_a9": {
        "label": "Organisationale Bindung Item 6",
        "Frage Item": "Ich fühle mich an die TU Darmstadt gebunden, weil ein Wechsel mit Wechselkosten einhergehen würde.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK19_a10": {
        "label": "Organisationale Bindung Item 7",
        "Frage Item": "Es wäre nicht fair, die Beziehung zur TU Darmstadt aufzukündigen, weil sie sich stets um mich als Arbeitnehmer:in bemüht hat.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK19_a11": {
        "label": "Organisationale Bindung Item 8",
        "Frage Item": "Aufgrund der langen Beziehung mit der TU Darmstadt fühle ich mich zu einer gewissen Rücksichtnahme verpflichtet.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK19_a12": {
        "label": "Organisationale Bindung Item 9",
        "Frage Item": "Ich fühle mich in der Angestelltenbeziehung mit der TU Darmstadt zur Fairness verpflichtet.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK19_a13": {
        "label": "Organisationale Bindung Item 10",
        "Frage Item": "Moralische Verpflichtungen gegenüber der TU Darmstadt spielen für mich auch eine Rolle.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK19_a14": {
        "label": "Organisationale Bindung Item 11",
        "Frage Item": "Ich bin über meinen Arbeitsvertrag hinaus vertraglich an die TU Darmstadt gebunden.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },

        "MK20_a1": {
        "label": "Zusammenarbeit Item 1",
        "Frage Item": "Insgesamt gibt es eine gute Zusammenarbeit mit anderen Organisationseinheiten in der Verwaltung.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK20_a2": {
        "label": "Zusammenarbeit Item 2",
        "Frage Item": "Insgesamt gibt es eine gute Zusammenarbeit mit Organisationseinheiten in der Wissenschaft.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK20_a3": {
        "label": "Zusammenarbeit Item 3",
        "Frage Item": "Relevante Informationen von anderen Bereichen erreichen unsere Organisationseinheit rechtzeitig.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK20_a4": {
        "label": "Zusammenarbeit Item 4",
        "Frage Item": "Mir sind die relevanten Themen und Projekte in anderen Organisationseinheiten, die meine Arbeit betreffen, bekannt.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK20_a5": {
        "label": "Zusammenarbeit Item 5",
        "Frage Item": "Unsere Ziele stimmen mit denen anderer Organisationseinheiten überein.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK20_a6": {
        "label": "Zusammenarbeit Item 6",
        "Frage Item": "Absprachen mit anderen Organisationseinheiten werden zuverlässig eingehalten.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK20_a7": {
        "label": "Zusammenarbeit Item 7",
        "Frage Item": "Ich weiß genau, welche Einheit bei welchem Thema die richtige Ansprechpartnerin ist.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK20_a8": {
        "label": "Zusammenarbeit Item 8",
        "Frage Item": "Mir sind die Abläufe in Organisationseinheiten, mit denen ich zusammenarbeite, bekannt.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK20_a9": {
        "label": "Zusammenarbeit Item 9",
        "Frage Item": "Themen und Projekte in verschiedenen Organisationseinheiten werden bei uns zusammengedacht.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK20_a10": {
        "label": "Zusammenarbeit Item 10",
        "Frage Item": "Irritationen, Unklarheiten und Konflikte mit anderen Organisationseinheiten werden sachlich und lösungsorientiert geklärt.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK20_a11": {
        "label": "Zusammenarbeit Item 11",
        "Frage Item": "Unsere Beiträge werden von anderen Organisationseinheiten als hilfreich und wertvoll anerkannt.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK20_a12": {
        "label": "Zusammenarbeit Item 12",
        "Frage Item": "Es herrscht ein wertschätzendes und lösungsorientiertes Miteinander, wenn wir mit anderen Organisationseinheiten zusammenarbeiten.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK20_a13": {
        "label": "Zusammenarbeit Item 13",
        "Frage Item": "Eine gute Zusammenarbeit mit anderen Organisationseinheiten ist uns wichtig und wird regelmäßig von uns reflektiert.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK17_a1": {
        "label": "Alltägliche Zusammenarbeit Item 1",
        "Frage Item": "Wie nehmen Sie die TU Darmstadt und die Zusammenarbeit innerhalb der TU Darmstadt in Ihrer alltäglichen Arbeit war? An der TU Darmstadt arbeiten wir: vernetzt",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },

        "MK17_a2": {
        "label": "Alltägliche Zusammenarbeit Item 2",
        "Frage Item": "Wie nehmen Sie die TU Darmstadt und die Zusammenarbeit innerhalb der TU Darmstadt in Ihrer alltäglichen Arbeit war? An der TU Darmstadt arbeiten wir: auf Augenhöhe",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK17_a3": {
        "label": "Alltägliche Zusammenarbeit Item 3",
        "Frage Item": "Wie nehmen Sie die TU Darmstadt und die Zusammenarbeit innerhalb der TU Darmstadt in Ihrer alltäglichen Arbeit war? An der TU Darmstadt arbeiten wir: pragmatisch",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK17_a4": {
        "label": "Alltägliche Zusammenarbeit Item 4",
        "Frage Item": "Wie nehmen Sie die TU Darmstadt und die Zusammenarbeit innerhalb der TU Darmstadt in Ihrer alltäglichen Arbeit war? An der TU Darmstadt arbeiten wir: lösungsorientiert",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK17_a5": {
        "label": "Alltägliche Zusammenarbeit Item 5",
        "Frage Item": "Wie nehmen Sie die TU Darmstadt und die Zusammenarbeit innerhalb der TU Darmstadt in Ihrer alltäglichen Arbeit war? An der TU Darmstadt arbeiten wir: an einem Ingenieurgeist ausgerichtet",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK17_a6": {
        "label": "Alltägliche Zusammenarbeit Item 6",
        "Frage Item": "Wie nehmen Sie die TU Darmstadt und die Zusammenarbeit innerhalb der TU Darmstadt in Ihrer alltäglichen Arbeit war? An der TU Darmstadt arbeiten wir: kreativ",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK17_a7": {
        "label": "Alltägliche Zusammenarbeit Item 7",
        "Frage Item": "Wie nehmen Sie die TU Darmstadt und die Zusammenarbeit innerhalb der TU Darmstadt in Ihrer alltäglichen Arbeit war? An der TU Darmstadt arbeiten wir: gestaltungswillig",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK17_a8": {
        "label": "Alltägliche Zusammenarbeit Item 8",
        "Frage Item": "Wie nehmen Sie die TU Darmstadt und die Zusammenarbeit innerhalb der TU Darmstadt in Ihrer alltäglichen Arbeit war? An der TU Darmstadt arbeiten wir: zuversichtlich",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK17_a9": {
        "label": "Alltägliche Zusammenarbeit Item 9",
        "Frage Item": "Wie nehmen Sie die TU Darmstadt und die Zusammenarbeit innerhalb der TU Darmstadt in Ihrer alltäglichen Arbeit war? An der TU Darmstadt arbeiten wir: innovativ",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "MK04_a1": {
        "label": "Meinungen TU Darmstadt",
        "Frage Item": "Wie gut sind Ihre Meinungen und Ideen an der TU Darmstadt vertreten?",
        "werte": "sehr gut; eher gut; neutral; eher nicht; überhaupt nicht; keine Angabe",
        "filter":"",
    },
        "MK12_a1": {
        "label": "Arbeitsplatz Empfehlung",
        "Frage Item": "Würden Sie die Universität als guten Arbeitsplatz weiterempfehlen?",
        "werte": "stimme voll zu; stimme eher zu; teils/teils; stimme eher nicht zu; stimme eher nicht zu; keine Angabe",
        "filter":"",
    },
        "MK13_a1": {
        "label": "Zukunft an der TUDA",
        "Frage Item": "Sehen Sie sich in einem Jahr noch an der TU Darmstadt?",
        "werte": "sehr wahrscheinlich; eher wahrscheinlich; neutral; eher unwahrscheinlich; sehr unwahrscheinlich; keine Angabe",
        "filter":"",
    },
        "A121_a1": {
        "label": "Information, Entscheidungen und Arbeit der Hochschulleitung Item 1",
        "Frage Item": "Über wichtige Vorgänge in der TU Darmstadt wird informiert.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"Z1: Alle bis auf Professor:innen",
    },
        "A121_a2": {
        "label": "Information, Entscheidungen und Arbeit der Hochschulleitung Item 2",
        "Frage Item": "Wichtige Entscheidungen der Hochschulleitung sind transparent.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"Z1: Alle bis auf Professor:innen",
    },
        "A121_a3": {
        "label": "Information, Entscheidungen und Arbeit der Hochschulleitung Item 3",
        "Frage Item": "Entscheidungen der Hochschulleitung sind nachvollziehbar.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"Z1: Alle bis auf Professor:innen",
    },
        "A121_a4": {
        "label": "Information, Entscheidungen und Arbeit der Hochschulleitung Item 4",
        "Frage Item": "Die Hochschulleitung trifft wichtige Entscheidungen in angemessener Zeit.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"Z1: Alle bis auf Professor:innen",
    },
        "A121_a5": {
        "label": "Information, Entscheidungen und Arbeit der Hochschulleitung Item 5",
        "Frage Item": "Die Schwerpunktsetzungen der TU Darmstadt sind für die Entwicklung der Universität insgesamt sinnvoll.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"Z1: Alle bis auf Professor:innen",
    },
        "A121_a7": {
        "label": "Information, Entscheidungen und Arbeit der Hochschulleitung Item 6",
        "Frage Item": "Alles in allem leistet die Hochschulleitung gute Arbeit.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"Z1: Alle bis auf Professor:innen",
    },
        "A121P_a1": {
        "label": "Information, Entscheidungen und Arbeit der Hochschulleitung Item 1 (Professor:innen)",
        "Frage Item": "Über wichtige Vorgänge in der TU Darmstadt wird informiert.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"Z1: Alle bis auf Professor:innen",
    },
        "A121P_a2": {
        "label": "Information, Entscheidungen und Arbeit der Hochschulleitung Item 2 (Professor:innen)",
        "Frage Item": "Wichtige Entscheidungen der Hochschulleitung sind transparent.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"Z1: Alle bis auf Professor:innen",
    },
        "A121P_a3": {
        "label": "Information, Entscheidungen und Arbeit der Hochschulleitung Item 3 (Professor:innen)",
        "Frage Item": "Entscheidungen der Hochschulleitung sind nachvollziehbar.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"Z1: Alle bis auf Professor:innen",
    },
        "A121P_a4": {
        "label": "Information, Entscheidungen und Arbeit der Hochschulleitung Item 4 (Professor:innen)",
        "Frage Item": "Die Hochschulleitung trifft wichtige Entscheidungen in angemessener Zeit.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"Z1: Alle bis auf Professor:innen",
    },
        "A121P_a5": {
        "label": "Information, Entscheidungen und Arbeit der Hochschulleitung Item 5 (Professor:innen)",
        "Frage Item": "Die Schwerpunktsetzungen der TU Darmstadt sind für die Entwicklung der Universität insgesamt sinnvoll.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"Z1: Alle bis auf Professor:innen",
    },
        "A121P_a6": {
        "label": "Information, Entscheidungen und Arbeit der Hochschulleitung Item 5 (Professor:innen)",
        "Frage Item": "Die Schwerpunktsetzungen der TU Darmstadt unterstützen meine wissenschaftliche Arbeit.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"Z1: Alle bis auf Professor:innen",
    },
        "A121P_a7": {
        "label": "Information, Entscheidungen und Arbeit der Hochschulleitung Item 7 (Professor:innen)",
        "Frage Item": "Alles in allem leistet die Hochschulleitung gute Arbeit.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"Z1: Professor:innen",
    },
        "HBA121_a1": {
        "label": "Handlungsbedarf Hochschulleitung",
        "Frage Item": "Bitte bewerten Sie den Handlungsbedarf bezogen auf Informationen, Entscheidungen und Arbeit der Hochschulleitung. Es besteht ...",
        "werte": "sehr großer Handlungsbedarf; eher großer Handlungsbedarf; mittlerer Handlungsbedarf; eher geringer Handlungsbedarf; überhaupt kein Handlungsbedarf; keine Angabe",
        "filter":"",
    },
        "A122_a1": {
        "label": "Gemeinsame Vorstellungen zur Weiterentwicklung",
        "Frage Item": "In der TU Darmstadt gibt es gemeinsame Vorstellungen darüber, wie sich die Universität weiterentwickeln soll.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "HBA122_a1": {
        "label": "Handlungsbedarf Weiterentwicklung",
        "Frage Item": "Bitte bewerten Sie den Handlungsbedarf bezogen auf gemeinsame Vorstellungen zur Weiterentwicklung der TU Darmstadt. Es besteht ...",
        "werte": "sehr großer Handlungsbedarf; eher großer Handlungsbedarf; mittlerer Handlungsbedarf; eher geringer Handlungsbedarf; überhaupt kein Handlungsbedarf; keine Angabe",
        "filter":"",
    },
        "A123_a1": {
        "label": "Kommunikationskultur und gelebte Kultur Item 1",
        "Frage Item": "Was in der TU Darmstadt auf „Hochglanzpapier“ steht, wird im Alltag auch gelebt.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "A123_a2": {
        "label": "Kommunikationskultur und gelebte Kultur Item 1",
        "Frage Item": "In der TU Darmstadt wird insgesamt eine offene Kommunikationskultur gelebt.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
        "A91_a1": {
        "label": "Befristeter Arbeitsvertrag",
        "Frage Item": "Mein Arbeitsvertrag ist befristet.",
        "werte": "ja; nein; keine Angabe",
        "filter":"",
    },
        "K1": {
        "label": "Geschlecht",
        "Frage Item": "Geschlecht",
        "werte": "weiblich; männlich; divers; keine Angabe",
        "filter":"",
    },
        "K2": {
        "label": "Familienaufgaben",
        "Frage Item": "Ich habe folgende Familienaufgaben …",
        "werte": "Ich kümmere mich um ein Kind oder um mehrere Kinder.; Ich kümmere mich um pflegebedürftige Angehörige.; keine Angabe",
        "filter":"",
    },
        "K3": {
        "label": "Alter",
        "Frage Item": "Ich gehöre folgender Altersgruppe an:",
        "werte": "16-35 Jahre; 36-49 Jahre; 50 Jahre oder älter; keine Angabe",
        "filter":"",
    },
        "K4_a1": {
        "label": "Internationale Mitarbeitende",
        "Frage Item": "Ich bin internationale*r Mitarbeiter*in (keine deutsche Staatsbürgerschaft).",
        "werte": "ja; nein; keine Angabe",
        "filter":"",
    },
        "K5_a1": {
        "label": "Wochenarbeitszeit",
        "Frage Item": "Mein vertraglicher Beschäftigungsumfang beträgt …",
        "werte": "bis 50%; über 50% bis 75%; über 75% bis 99%; Vollzeit; keine Angabe",
        "filter":"",
    },
        "K6Uni_a1": {
        "label": "Lehrverpflichtung",
        "Frage Item": "Ich habe eine Lehrverpflichtung im Umfang von … Semesterwochenstunden.",
        "werte": "0; 1-6; 7-9; 10 oder mehr; keine Angabe",
        "filter":"Z1: Professor:innen; Wissenschaftliche Mitarbeiter:innen",
    },
        "K8P_a1": {
        "label": "Lehrverpflichtun Professor:innen 1",
        "Frage Item": "Mein Aufgabenschwerpunkt liegt …",
        "werte": "... in der Lehre.; … in der Forschung.; … in Forschung und Lehre gleichermaßen.; … in Management- / Leitungsaufgaben.; keine Angabe",
        "filter":"Z1: Professor:innen",
    },
        "K8P_a2": {
        "label": "Lehrverpflichtun Professor:innen 2",
        "Frage Item": "Meine persönliche Schwerpunktsetzung liegt …",
        "werte": "... in der Lehre.; … in der Forschung.; … in Forschung und Lehre gleichermaßen.; … in Management- / Leitungsaufgaben.; keine Angabe",
        "filter":"Z1: Professor:innen",
    },
        "K8W_a1": {
        "label": "Lehrverpflichtung Wissenschaftliche Mitarbeiter:innen 1",
        "Frage Item": "Mein Aufgabenschwerpunkt liegt …",
        "werte": "... in der Lehre.; … in der Forschung.; … in anderen Aufgabenfeldern (z. B. QM).; keine Angabe",
        "filter":"Z1: Wissenschaftliche Mitarbeiter:innen",
    },
        "K8W_a2": {
        "label": "Lehrverpflichtung Wissenschaftliche Mitarbeiter:innen 2",
        "Frage Item": "Meine persönliche Schwerpunktsetzung liegt …",
        "werte": "... in der Lehre.; … in der Forschung.; … in anderen Aufgabenfeldern (z. B. QM).; keine Angabe",
        "filter":"Z1: Wissenschaftliche Mitarbeiter:innen",
    },
        "AOBer": {
        "label": "Organisationsbereich",
        "Frage Item": "Die Auswertung der Ergebnisse erfolgt hochschulübergreifend. Wenn Sie hier angeben, welchem Organisationsbereich Sie angehören, können die Ergebnisse bei ausreichendem Rücklauf auch für Ihren Bereich ausgewertet werden.",
        "werte": "Organisationsbereich TUDA",
        "filter":"",
    },
        "MK15_a1": {
        "label": "Zufriedenheit Umfrage",
        "Frage Item": "Wie zufrieden sind Sie mit dieser Umfrage?",
        "werte": "sehr zufrieden; eher zufrieden; teils / teils; eher nicht zufrieden; gar nicht zufrieden; keine Angabe",
        "filter":"",
    },
        "MK16_a1": {
        "label": "Umfragedauer",
        "Frage Item": "Die Umfragedauer war für mich zu lang.",
        "werte": "trifft sehr zu; trifft eher zu; teils/teils; trifft eher nicht zu; trifft gar nicht zu; keine Angabe",
        "filter":"",
    },
}

#══════════════════════════════════════════════════════════════════════════════
# ── SEITEN-KONFIGURATION ──────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Zuhören. Verstehen. Verändern. TU im Dialog (Welle1) -- Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
    h1, h2, h3 { font-family: 'IBM Plex Mono', monospace; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #2b2b2b !important;
        border-right: 3px solid #c0392b;
    }
    [data-testid="stSidebar"] * { color: #f0f0f0 !important; }

    /* ── Metrics ── */
    [data-testid="stMetric"] {
        background: #f5f5f5;
        border: 1px solid #dddddd;
        border-left: 4px solid #c0392b;
        border-radius: 6px;
        padding: 12px 18px;
    }
    [data-testid="stMetricLabel"] { font-size: 0.75rem; color: #666666 !important; }
    [data-testid="stMetricValue"] {
        font-family: 'IBM Plex Mono', monospace;
        color: #c0392b !important;
    }

    .section-header {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #c0392b;
        border-bottom: 2px solid #c0392b;
        padding-bottom: 6px;
        margin-bottom: 16px;
    }

    [data-testid="stDataFrame"] { border: 1px solid #dddddd; border-radius: 6px; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 2px solid #dddddd; }
    .stTabs [data-baseweb="tab"] {
        background: #f0f0f0;
        border-radius: 6px 6px 0 0;
        padding: 6px 20px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        color: #555555;
    }
    .stTabs [aria-selected="true"] { background: #c0392b !important; color: #ffffff !important; }

    /* ── Glossar-Karten ── */
    .glossar-card {
        background: #fafafa;
        border: 1px solid #e0e0e0;
        border-left: 4px solid #c0392b;
        border-radius: 6px;
        padding: 18px 22px;
        margin-bottom: 14px;
    }
    .glossar-card h4 {
        font-family: 'IBM Plex Mono', monospace;
        color: #c0392b;
        margin: 0 0 4px 0;
        font-size: 1rem;
    }
    .glossar-card h5 {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        color: #999999;
        margin-bottom: 10px;
        font-weight: 400;
    }
    .glossar-card p { margin: 4px 0; font-size: 0.88rem; color: #333333; }
    .glossar-badge {
        display: inline-block;
        background: #f0f0f0;
        color: #c0392b;
        border: 1px solid #c0392b;
        border-radius: 4px;
        padding: 2px 10px;
        font-size: 0.72rem;
        font-family: 'IBM Plex Mono', monospace;
        margin-bottom: 10px;
    }

    /* ── NaN-Hinweis ── */
    .nan-info {
        font-size: 0.82rem;
        color: #888888;
        font-style: italic;
        margin: 4px 0 12px 0;
    }

    /* ── Datenquelle ── */
    .datasource-box {
        background: #f5f5f5;
        border: 1px solid #dddddd;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .datasource-active { border-color: #c0392b; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# ── HILFSFUNKTIONEN ───────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

PLOTLY_THEME = dict(
    template="plotly_white",
    paper_bgcolor="#ffffff",
    plot_bgcolor="#f5f5f5",
    font_family="IBM Plex Sans",
    font_color="#333333",
)
COLOR_SEQ = ["#c0392b", "#e74c3c", "#888888", "#aaaaaa", "#cccccc", "#555555", "#ff6b6b", "#b03a2e"]

def get_defined_order(varname: str) -> list[str] | None:
    """
    Parse the semicolon-separated 'werte' string for a variable and return
    the list of category labels in that order.
    Returns None if no description exists for this variable.
    """
    info = COLUMN_DESCRIPTIONS.get(varname)
    if info is None:
        return None
    werte_str = info.get("werte", "")
    if not werte_str:
        return None
    # Split on semicolons, strip whitespace from each entry
    return [w.strip() for w in werte_str.split(";") if w.strip()]
 
 
def apply_defined_order(series: pd.Series, varname: str) -> pd.Series:
    """
    Convert a string series to an ordered Categorical whose level order
    follows the 'werte' definition in COLUMN_DESCRIPTIONS.
 
    - Categories present in the data but absent from the definition are
      appended at the end (so nothing is silently dropped).
    - If no definition exists the series is returned as-is (plain strings).
    """
    defined = get_defined_order(varname)
    if defined is None:
        return series.astype(str)
 
    # Find any data values not covered by the definition and append them
    actual_vals = set(series.dropna().astype(str).unique())
    extra = [v for v in sorted(actual_vals) if v not in defined]
    ordered_cats = defined + extra
 
    cat_series = pd.Categorical(series.astype(str), categories=ordered_cats, ordered=True)
    return pd.Series(cat_series, index=series.index, name=series.name)
 
 


def load_rds(path: str) -> pd.DataFrame:
    """Lädt eine .rds-Datei als pandas DataFrame (via pyreadr)."""
    try:
        import pyreadr
    except ImportError:
        st.error(
            "**pyreadr** ist nicht installiert. "
            "Bitte `pip install pyreadr` ausführen und App neu starten."
        )
        st.stop()
    result = pyreadr.read_r(path)
    key = list(result.keys())[0]
    return result[key]


def load_rds_from_bytes(file_bytes: bytes) -> pd.DataFrame:
    """Lädt eine .rds-Datei aus einem Bytes-Objekt (Upload) via pyreadr."""
    try:
        import pyreadr
    except ImportError:
        st.error(
            "**pyreadr** ist nicht installiert. "
            "Bitte `pip install pyreadr` ausführen und App neu starten."
        )
        st.stop()
    with tempfile.NamedTemporaryFile(suffix=".rds", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        result = pyreadr.read_r(tmp_path)
        key = list(result.keys())[0]
        return result[key]
    finally:
        os.unlink(tmp_path)


def count_nan(series: pd.Series) -> int:
    return int(series.isna().sum())


def nan_sentence(n_nan: int, n_total: int, label: str) -> str:
    if n_nan == 0:
        return ""
    pct = round(n_nan / n_total * 100, 1)
    return (
        f"{n_nan} von {n_total} Beobachtungen ({pct} %) "
        f"haben für **{label}** keinen gültigen Wert (fehlend) und wurden "
        f"aus Tabelle und Diagramm ausgeschlossen."
    )


def nan_sentence_biv(n_nan: int, n_total: int, lbl1: str, lbl2: str) -> str:
    if n_nan == 0:
        return ""
    pct = round(n_nan / n_total * 100, 1)
    return (
        f"{n_nan} von {n_total} Beobachtungen ({pct} %) wurden ausgeschlossen, "
        f"da mindestens einer der Werte für **{lbl1}** oder **{lbl2}** fehlt."
    )


def maybe_bin(series: pd.Series, varname: str | None = None, max_cats: int = 20) -> pd.Series:
    """
    For numeric variables with many unique values: bin into quantiles.
    For everything else: apply the defined category order from COLUMN_DESCRIPTIONS
    (if available), otherwise return plain strings.
    """
    if pd.api.types.is_numeric_dtype(series):
        n_unique = series.nunique()
        if n_unique > max_cats:
            binned = pd.qcut(series, q=min(8, n_unique), duplicates="drop")
            result = binned.astype(str)
            result.name = series.name
            return result
        # Numeric but few levels — still apply defined order if present
        str_series = series.astype(str)
        str_series.name = series.name
    else:
        str_series = series.astype(str)
        str_series.name = series.name
 
    if varname is not None:
        return apply_defined_order(str_series, varname)
    return str_series
 



def freq_table(series: pd.Series) -> pd.DataFrame:
    """
    Build a frequency table that respects the category order of an ordered
    Categorical series.  Plain string series fall back to value_counts order.
    """
    if hasattr(series, "cat") and series.cat.ordered:
        # Preserve defined order; include only categories that actually appear
        present_cats = [c for c in series.cat.categories if c in series.values]
        counts = series.value_counts().reindex(present_cats, fill_value=0)
    else:
        counts = series.value_counts(dropna=True)
 
    pct = (counts / counts.sum() * 100).round(2)
    out = pd.DataFrame({"Anzahl": counts, "Anteil (%)": pct})
    out.index.name = series.name
    return out.reset_index()
 
 
def crosstab_tables(s1: pd.Series, s2: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    ct_counts = pd.crosstab(s1, s2, margins=False, dropna=True)
    ct_pct    = (pd.crosstab(s1, s2, normalize="index", dropna=True) * 100).round(2)
    return ct_counts, ct_pct
 
 
def var_label(varname: str) -> str:
    return COLUMN_DESCRIPTIONS.get(varname, {}).get("label", varname)
 
 
# ══════════════════════════════════════════════════════════════════════════════
# ── SIDEBAR & DATENQUELLE ─────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
 
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_FILE_PATH = os.path.join(SCRIPT_DIR, DATA_FILE)
 
 
@st.cache_data(show_spinner="Lokale Datei wird geladen …")
def cached_load_local(path: str) -> pd.DataFrame:
    return load_rds(path)
 
 
@st.cache_data(show_spinner="Hochgeladene Datei wird geladen …")
def cached_load_upload(file_bytes: bytes) -> pd.DataFrame:
    return load_rds_from_bytes(file_bytes)
 
 
with st.sidebar:
    st.markdown("## ZVV -- Dashboard")
 
    # Logo
    for ext in ("logo.png", "logo.jpg", "logo.svg", "tu_logo.png", "tu_logo.jpg"):
        _lp = os.path.join(SCRIPT_DIR, ext)
        if os.path.exists(_lp):
            st.image(_lp, width=160)
            break
 
    st.markdown(
        '''<div style="font-family:'Roboto Condensed',Tahoma,sans-serif;font-size:1.3rem;
        font-weight:700;color:#005AA9;border-bottom:2px solid #005AA9;
        padding-bottom:8px;margin-bottom:8px;margin-top:8px">Datenexplorer</div>''',
        unsafe_allow_html=True,
    )
 
    # ── Datenquelle auswählen ─────────────────────────────────────────────────
    st.markdown("**Datenquelle**")
 
    local_available = os.path.exists(LOCAL_FILE_PATH)
 
    data_source = st.radio(
        "Datenquelle auswählen",
        options=["Lokale Datei", "Datei hochladen"],
        label_visibility="collapsed",
        key="data_source",
    )
 
    df_full = None
 
    if data_source == "Lokale Datei":
        if local_available:
            st.success(f"✓ `{DATA_FILE}` gefunden")
            df_full = cached_load_local(LOCAL_FILE_PATH)
        else:
            st.error(
                f"`{DATA_FILE}` nicht gefunden.\n\n"
                "Bitte Datei in denselben Ordner wie dieses Skript legen "
                "oder Datei hochladen wählen."
            )
 
    else:  # Upload
        uploaded_file = st.file_uploader(
            "RDS-Datei hochladen",
            type=["rds"],
            help="Wählen Sie eine .rds-Datei von Ihrem Computer.",
            key="rds_upload",
        )
        if uploaded_file is not None:
            st.success(f"✓ `{uploaded_file.name}` hochgeladen")
            file_bytes = uploaded_file.read()
            df_full = cached_load_upload(file_bytes)
        else:
            st.info("Bitte eine .rds-Datei auswählen.")
 
    if df_full is None:
        st.stop()
 
    st.markdown("---")
 
    seite = st.radio(
        "Navigation",
        ["Univariate Analyse", "Bivariate Analyse", "Variablen-Glossar"],
        label_visibility="collapsed",
    )
 
    st.markdown("---")
 
 
# ══════════════════════════════════════════════════════════════════════════════
# ── DATEN FILTERN ─────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
 
available_vars = [v for v in INCLUDED_VARIABLES if v in df_full.columns]
df = df_full[available_vars].copy()
 
# ── Übersichts-Kennzahlen ─────────────────────────────────────────────────────
st.title("Zuhören. Verstehen. Verändern. TU im Dialog (Welle1) -- Dashboard")
 
m1, m2, m3, m4 = st.columns(4)
m1.metric("Beobachtungen", f"{df.shape[0]:,}")
m2.metric("Variablen", f"{df.shape[1]:,}")
m3.metric(
    "Numerische Var.",
    sum(pd.api.types.is_numeric_dtype(df[c]) for c in df.columns),
)
m4.metric(
    "Kategoriale Var.",
    sum(not pd.api.types.is_numeric_dtype(df[c]) for c in df.columns),
)
 
st.markdown("---")
 
# ══════════════════════════════════════════════════════════════════════════════
# ── SEITE 1: UNIVARIATE ANALYSE ───────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
 
if seite == "Univariate Analyse":
    st.markdown('<p class="section-header">Univariate Analyse</p>', unsafe_allow_html=True)
 
    uni_col, uni_chart_col = st.columns([1, 2])
 
    with uni_col:
        uni_var = st.selectbox(
            "Variable auswählen",
            options=available_vars,
            format_func=var_label,
            key="uni_var",
        )
        show_chart = st.checkbox("Balkendiagramm anzeigen", value=True, key="uni_chart")
 
    n_total   = len(df[uni_var])
    n_nan     = count_nan(df[uni_var])
    valid_ser = df[uni_var].dropna()
 
    # ── KEY CHANGE: pass varname so category order is applied ─────────────────
    uni_series = maybe_bin(valid_ser, varname=uni_var)
    uni_series.name = uni_var
 
    ft  = freq_table(uni_series)
    lbl = var_label(uni_var)
 
    # Preserve the order for the bar chart x-axis
    if hasattr(uni_series, "cat") and uni_series.cat.ordered:
        cat_order = [c for c in uni_series.cat.categories if c in uni_series.values]
    else:
        cat_order = ft[uni_var].tolist()
 
    with uni_col:
        st.markdown(f"**Verteilung: {lbl}**")
 
        msg = nan_sentence(n_nan, n_total, lbl)
        if msg:
            st.markdown(f'<p class="nan-info"> {msg}</p>', unsafe_allow_html=True)
 
        st.dataframe(ft, use_container_width=True, hide_index=True)
 
    with uni_chart_col:
        if show_chart:
            fig_uni = px.bar(
                ft,
                x=uni_var,
                y="Anteil (%)",
                text="Anteil (%)",
                color=uni_var,
                color_discrete_sequence=COLOR_SEQ,
                title=f"Verteilung: {lbl}",
                labels={"Anteil (%)": "Anteil (%)", uni_var: lbl},
                range_y=[0, 100],
                # ── KEY CHANGE: enforce defined category order on x-axis ──────
                category_orders={uni_var: cat_order},
            )
            fig_uni.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_uni.update_layout(showlegend=False, xaxis_tickangle=-35, yaxis_ticksuffix="%", **PLOTLY_THEME)
            st.plotly_chart(fig_uni, use_container_width=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# ── SEITE 2: BIVARIATE ANALYSE ────────────────────────────────────════════════
# ══════════════════════════════════════════════════════════════════════════════
 
elif seite == "Bivariate Analyse":
    st.markdown('<p class="section-header">Bivariate Analyse</p>', unsafe_allow_html=True)
 
    bl, br = st.columns(2)
    with bl:
        biv_var1 = st.selectbox(
            "Hauptvariable (Zeilen)",
            options=available_vars,
            format_func=var_label,
            key="biv_var1",
        )
    with br:
        remaining = [v for v in available_vars if v != biv_var1]
        biv_var2 = st.selectbox(
            "Gruppierungsvariable (Spalten)",
            options=remaining,
            format_func=var_label,
            key="biv_var2",
        )
 
    lbl1 = var_label(biv_var1)
    lbl2 = var_label(biv_var2)
 
    pair_df = df[[biv_var1, biv_var2]].copy()
    n_total = len(pair_df)
    n_nan   = int(pair_df.isna().any(axis=1).sum())
 
    # ── KEY CHANGE: apply defined order to both variables ─────────────────────
    full_s1 = maybe_bin(df[biv_var1].dropna(), varname=biv_var1)
    full_s1.name = biv_var1
    full_s2 = maybe_bin(df[biv_var2].dropna(), varname=biv_var2)
    full_s2.name = biv_var2
 
    # Collect ordered category lists for reindex and chart
    if hasattr(full_s1, "cat") and full_s1.cat.ordered:
        all_cats1 = list(full_s1.cat.categories)
    else:
        all_cats1 = sorted(full_s1.unique())
 
    if hasattr(full_s2, "cat") and full_s2.cat.ordered:
        all_cats2 = list(full_s2.cat.categories)
    else:
        all_cats2 = sorted(full_s2.unique())
 
    pair_df = pair_df.dropna()
 
    s1 = maybe_bin(pair_df[biv_var1], varname=biv_var1)
    s1.name = biv_var1
    s2 = maybe_bin(pair_df[biv_var2], varname=biv_var2)
    s2.name = biv_var2
 
    ct_counts, ct_pct = crosstab_tables(s1, s2)
 
    ct_counts = ct_counts.reindex(index=all_cats1, columns=all_cats2, fill_value=0)
    ct_pct    = ct_pct.reindex(index=all_cats1, columns=all_cats2, fill_value=0.0)
 
    msg_biv = nan_sentence_biv(n_nan, n_total, lbl1, lbl2)
    if msg_biv:
        st.markdown(f'<p class="nan-info"> {msg_biv}</p>', unsafe_allow_html=True)
 
    diagrammtyp = st.radio(
        "Diagrammtyp",
        ["Gruppierte Balken", "Heatmap"],
        horizontal=True,
        key="biv_chart_type",
    )
 
    tab_anz, tab_pct_tab = st.tabs(["Häufigkeiten", "Zeilenprozente (%)"])
    with tab_anz:
        st.markdown(f"**{lbl1} × {lbl2} — Häufigkeiten**")
        st.dataframe(ct_counts, use_container_width=True)
    with tab_pct_tab:
        st.markdown(f"**{lbl1} × {lbl2} — Zeilenprozente**")
        st.dataframe(ct_pct, use_container_width=True)
 
    ct_melted = ct_pct.reset_index().melt(
        id_vars=biv_var1, var_name=biv_var2, value_name="Anteil (%)"
    )
 
    if diagrammtyp == "Heatmap":
        fig_biv = px.imshow(
            ct_pct, text_auto=True, aspect="auto",
            color_continuous_scale="Blues", title=f"{lbl1} × {lbl2}",
        )
        fig_biv.update_layout(**PLOTLY_THEME)
    else:
        fig_biv = px.bar(
            ct_melted, x=biv_var1, y="Anteil (%)", color=biv_var2,
            barmode="group", color_discrete_sequence=COLOR_SEQ,
            title=f"Verteilung von {lbl1} nach {lbl2}",
            labels={"Anteil (%)": "Anteil (%)", biv_var1: lbl1, biv_var2: lbl2},
            # ── KEY CHANGE: enforce defined order on both axes ────────────────
            category_orders={biv_var1: all_cats1, biv_var2: all_cats2},
        )
        fig_biv.update_layout(xaxis_tickangle=-35, legend_title=lbl2, yaxis_ticksuffix="%", **PLOTLY_THEME)
        fig_biv.update_yaxes(range=[0, 100], autorange=False)
    st.plotly_chart(fig_biv, use_container_width=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# ── SEITE 3: VARIABLEN-GLOSSAR ────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
 
elif seite == "Variablen-Glossar":
    st.markdown('<p class="section-header">Variablen-Glossar</p>', unsafe_allow_html=True)
    st.markdown("Erläuterungen zu allen eingeschlossenen Variablen des Datensatzes.")
    st.markdown("")
 
    suche = st.text_input(
        "Variable suchen …",
        placeholder="z. B. Alter, Bildung, Region …",
    )
    st.markdown("---")
 
    gefunden = 0
    for var in available_vars:
        info   = COLUMN_DESCRIPTIONS.get(var, {})
        label  = info.get("label",        var)
        beschr = info.get("Frage Item", "Keine Beschreibung vorhanden.")
        werte  = info.get("werte",        "–")
        filter = info.get("filter",        "–")
 
        if suche and suche.lower() not in label.lower() and suche.lower() not in var.lower():
            continue
 
        gefunden += 1
        st.markdown(
            f"""
            <div class="glossar-card">
                <h4>{label}</h4>
                <h5>{var}</h5>
                <p><strong style="color:#8b8fa8">Mögliche Filter:&nbsp;</strong>{filter}</p>
                <hr style="border: none; border-top: 1px solid #8b8fa8; margin: 8px 0;">
                <p><strong style="color:#8b8fa8">Ausprägungen:&nbsp;</strong>{werte}</p>
                <hr style="border: none; border-top: 1px solid #8b8fa8; margin: 8px 0;">
                <p><strong style="color:#8b8fa8">Frage Item:&nbsp;</strong><i>{beschr}</i></p>
            </div>
            """,
            unsafe_allow_html=True,
        )
 
    if gefunden == 0:
        st.info("Keine passende Variable gefunden.")
 
# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Zuhören. Verstehen. Verändern. TU im Dialog (Welle1) -- Dashboard")
 
