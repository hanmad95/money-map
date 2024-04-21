
from typing import Dict, List

TRANSACTION_CATEGORIES : Dict[str,Dict[str,List[str]]]= {
    "Einnahmen": {
        "Hauptjob": ["Gehalt", "Bonuse", "Reisekostenerstattung"],
        "Nebenjob": ["Gehalt"],
        "Staat": ["Zuschuesse"],
        "Privat": ["Verkauf von Gegenstand", "Kindergeld"],
        "Sonstiges": ["Kautionen", "Gutschriften", "Umlagerung"]
    },
    "Fixe Ausgaben": {
        "Wohnen Deutschland": [
            "Miete",
            "Nebenkosten",
            "Telefon & Internet",
            "Rundfunk",
            "Sonstiges"
        ],
        "Wohnen Oesterreich": [
            "Miete",
            "Nebenkosten",
            "Telefon & Internet",
            "Rundfunk",
            "Sonstiges"
        ],
        "Versicherungen": [
            "Krankenversicherung",
            "Krankenzusatz",
            "Private Haftpflicht",
            "Rechtsschutz",
            "Berufsunfaehigkeit",
            "Hausrat",
            "Sonstiges"
        ],
        "Finanzausgaben": [
            "ETF Sparplaene",
            "Sonstige Sparplaene",
            "Lebensversicherungen",
            "Kreditraten",
            "Kontofuehrung"
        ],
        "Mobilitaet": [
            "KFZ-Versicherungen",
            "KFZ-Steuer",
            "Oeffentliche Verkehrsmittel"
        ],
        "Sonstige Vertraege": ["Handy", "Abos", "Vereinsmitgliedschaften"]
    },
    "Variable Ausgaben": {
        "Lebenshaltung": [
            "Lebensmittel",
            "Getraenke",
            "Essensbestellungen",
            "Pflege",
            "Mode",
            "Kantine"
        ],
        "Gesundheit": ["Medikamente", "Arztkosten"],
        "Wohnen": [
            "Moebel",
            "Geraete",
            "Wartungen",
            "Gegenstaende",
            "Kautionen"
        ],
        "Mobilitaet": [
            "Fahrzeuganschaffung",
            "Tanken",
            "Instandhaltung",
            "Oeffentliche Verkehrsmittel"
        ],
        "Entertainment": ["Klettern", "Kino/Heimkino", "Urlaub", "Ausgehen"],
        "Bildung": ["Gebueren"],
        "Sonstiges": [
            "Geschenke",
            "Fuer Eltern",
            "Gegenstaende",
            "Guthaben",
            "Bargeldabhebungen",
            "Umlagerungen"
        ]
    }
}
