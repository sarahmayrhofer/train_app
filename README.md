# PR-DKE
## ANLEITUNG ZUM AUSFÜHREN
Grundsätzliches:
Im abgegebenen ZIP-Ordner ist auch eine Anleitung zum Ausführen vorhanden. (mit Bildern) 

Im Git Repo ist für jede Applikation ein eigener Unterordner angelegt. („route“ für das Streckensystem, etc.)
Jede Applikation hat auch einen eigenen venv-Ordner.
Wichtig: Jede Applikation muss auf einem anderen, genau festgelegten Port laufen. Das wird später noch genauer beschrieben.
Zum Ausführen der Applikationen muss zuerst das Git Repo lokal heruntergeladen und z. B. in einem Ordner auf C:\ abgespeichert werden: (Anleitung für Windows)
 
 

Im Unterordner des jeweiligen Systems einen Ordner „venv“ erstellen:
 

In der Kommandozeile in den Unterordner des jeweiligen Systems wechseln und auf Basis der mitgelieferten requirements.txt das venv erstellen: (die requirements.txt befindet sich im Unterordner von jeder Applikation)
Wenn notwendig: Das Modul für venv installieren:
 
 

Ausführen des Streckensystems:
In der Kommandozeile im Unterordner routes folgenden Befehl eingeben: (das venv des Streckensystems muss bereits aktiviert sein, ausführen auf Port 5001)
flask run -p 5001
 
Anschließend im Webbrowser die angezeigte URL aufrufen.
Anmeldedaten für den Admin im Streckensystem:
Benutzername: admin_test
Passwort: admin_test

Anmeldedaten für den Employee im Streckensystem:
Benutzername: employee_test
Passwort: employee_test

# Hier die anderen Systeme beschreiben.

Ausführen des Flottensystems:
In der Kommandozeile im Unterordner routes folgenden Befehl eingeben: (das venv des Flottensystems muss bereits aktiviert sein, ausführen auf Port 5002)
flask run -p 5002
 
Anschließend im Webbrowser die angezeigte URL aufrufen.
Anmeldedaten für den Admin:
Benutzername: tobi_schwap
Passwort: 123

Ausführen des Fahrplansystem:
In der Kommandozeile im Unterordner routes folgenden Befehl eingeben: (das venv des Fahrplansystems muss bereits aktiviert sein, ausführen auf Port 5001)
flask run -p 5000
 
Anschließend im Webbrowser die angezeigte URL aufrufen.
Anmeldedaten für den Admin im Fahrplansystem:
Benutzername: BigBoss
Passwort: admin

Anmeldedaten für den Employee im Streckensystem:
Benutzername: Susi
Passwort: test


## Protokolle:
- [Protokoll LVA am 2023-11-03](https://jkulinz-my.sharepoint.com/:w:/r/personal/k12043350_students_jku_at/_layouts/15/Doc.aspx?sourcedoc=%7B5B114373-C146-44DA-BEBF-F56F17647E81%7D&file=Protokoll%20LVA%20am%202023-11-03.docx&action=default&mobileredirect=true)
- [Protokoll LVA am 2023-11-24](https://jkulinz-my.sharepoint.com/:w:/r/personal/k12043350_students_jku_at/_layouts/15/Doc.aspx?sourcedoc=%7B9D29063B-9DE0-4758-90DA-2F09541D9204%7D&file=Protokoll%20LVA%20am%202023-11-24.docx&action=default&mobileredirect=true)
- [Protokoll Teammeeting am 2023-11-12](https://jkulinz-my.sharepoint.com/:w:/r/personal/k12043350_students_jku_at/_layouts/15/Doc.aspx?sourcedoc=%7B19A234E5-14E7-42F9-BB67-8BBA423D6E68%7D&file=Protokoll%20Teammeeting%20am%202023-11-12.docx&action=default&mobileredirect=true)

# Link zum geteilten Onedrive-Ordner
Wichtig: Ihr müsst mit euren JKU-Account eingeloggt sein.
https://jkulinz-my.sharepoint.com/:f:/r/personal/k12043350_students_jku_at/Documents/Geteilte%20Ordner/PR%20DKE%202023%20Gruppenordner?csf=1&web=1&e=jtnWJZ

# Zeitaufzeichnung
https://jkulinz-my.sharepoint.com/:x:/g/personal/k12043350_students_jku_at/EU7D3YJeRBdNsA3LX3SLlP0BxeUkhurGTyd3nW3sq_-76A?e=NufeLn

# Useful commands
## Git:
`git pull`

`git commit -m "beschreibung"`

`git push origin main`

## Migrations: (Wichtig: man muss das venv aktiviert haben, die ganze Sache ist auch im Mega Tutorial beschrieben)
flask db migrate -m "Beschreibung"
flask db upgrade


# Benutzer zum Login:
Streckensystem:
Admin: admin_test
Passwort: admin_test

Mitarbeiter: employee_test
Passwort: employee_test

#Hinweise Tipps und Tricks
Wenn der migrate-Befehl nicht funktioniert, kann es hilfreich sein, die inhalte der Tabelle "alembic_Version" zu löschen. Dazu braucht man eventuell die sqlite-tools: https://sqlite.org/2023/sqlite-tools-win-x64-3440000.zip




