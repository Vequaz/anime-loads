import sys, json, time, os, re
from datetime import datetime
import animeloads
from animeloads import animeloads
import myjdapi

botfile = "config/ani.json"
botfolder = "config/"

def log(message):
    print(message)

def printException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print("Error:")
    print(exc_type, fname, exc_tb.tb_lineno)

def loadconfig():
    try:
        os.makedirs(os.path.dirname(botfolder), exist_ok=True)
        
        # Standardkonfiguration erstellen, falls Datei nicht existiert
        if not os.path.exists(botfile):
            default_config = {
                "settings": {
                    "hoster": "example",
                    "browserengine": "chrome",
                    "browserlocation": "",
                    "timedelay": 300,
                    "myjd_user": "",
                    "myjd_pw": "",
                    "myjd_device": "",
                    "al_user": "",
                    "al_pass": ""
                },
                "anime": []
            }
            with open(botfile, "w") as outfile:
                json.dump(default_config, outfile, indent=4)
            print(f"Standardkonfiguration wurde erstellt unter {botfile}")
            print("Bitte trage deine Daten ein und starte den Bot erneut")
            sys.exit(0)
        
        with open(botfile, "r") as infile:
            data = json.load(infile)
        
        settings = data['settings']
        hoster = settings['hoster']
        browser = settings['browserengine']
        browserlocation = settings['browserlocation']
        timedelay = settings['timedelay']
        myjd_user = settings['myjd_user']
        myjd_pass = settings['myjd_pw']
        myjd_device = settings['myjd_device']
        
        return hoster, browser, browserlocation, timedelay, myjd_user, myjd_pass, myjd_device, settings
        
    except json.JSONDecodeError as e:
        print(f"Fehler: Die Konfigurationsdatei {botfile} ist ungültig oder beschädigt")
        printException(e)
        sys.exit(1)
    except Exception as e:
        print("Fehler beim Laden der Konfiguration")
        printException(e)
        sys.exit(1)

def startbot():
    try:
        hoster, browser, browserlocation, timedelay, myjd_user, myjd_pass, myjd_device, settings = loadconfig()
    except Exception as e:
        print("Konfiguration konnte nicht geladen werden")
        printException(e)
        sys.exit(1)

    # MyJDownloader Verbindung herstellen
    jd = myjdapi.Myjdapi()
    jd.set_app_key("animeloads")
    
    if not myjd_pass:
        print("MyJDownloader Passwort fehlt in der Konfiguration")
        sys.exit(1)
    
    try:
        jd.connect(myjd_user, myjd_pass)
    except Exception as e:
        print("Verbindung zu MyJDownloader fehlgeschlagen")
        printException(e)
        sys.exit(1)

    # AnimeLoader initialisieren
    al = animeloads(browser=browser, browserloc=browserlocation)
    
    # Anime-Loads Login (wenn in Konfiguration vorhanden)
    al_user = settings.get('al_user')
    al_pass = settings.get('al_pass')
    if al_user and al_pass:
        try:
            al.login(al_user, al_pass)
            print("Erfolgreich bei Anime-Loads angemeldet")
        except Exception as e:
            print("Anmeldung bei Anime-Loads fehlgeschlagen")
            printException(e)
    
    # Hauptschleife
    while True:
        try:
            with open(botfile, "r") as f:
                data = json.load(f)
            
            if 'anime' not in data or not data['anime']:
                print("Keine Anime in der Liste gefunden")
                time.sleep(timedelay)
                continue

            for animeentry in data['anime']:
                try:
                    name = animeentry['name']
                    url = animeentry['url']
                    releaseID = animeentry['releaseID']
                    customPackage = animeentry.get('customPackage', "")
                    missingEpisodes = animeentry['missing']
                    episodes = animeentry['episodes']

                    now = datetime.now()
                    print(f"[{now.strftime('%H:%M:%S')}] Prüfe {name} auf Updates")

                    anime = al.getAnime(url)
                    release = anime.getReleases()[releaseID-1]
                    anime.updateInfo()
                    curEpisodes = release.getEpisodeCount()

                    # Fehlende Episoden verarbeiten
                    if missingEpisodes:
                        print(f"[INFO] {name} hat fehlende Episode(n)")
                        for idx, missingEpisode in enumerate(missingEpisodes):
                            try:
                                dl_ret = anime.downloadEpisode(
                                    missingEpisode, release, hoster, browser, browserlocation,
                                    myjd_user=myjd_user, myjd_pw=myjd_pass, 
                                    myjd_device=myjd_device, pkgName=customPackage
                                )
                                if dl_ret:
                                    log(f"[DOWNLOAD] Episode {missingEpisode} von {name} wurde hinzugefügt")
                                    missingEpisodes[idx] = -1
                                    animeentry['missing'] = [ep for ep in missingEpisodes if ep != -1]
                                else:
                                    log(f"[ERROR] Episode {missingEpisode} konnte nicht hinzugefügt werden")
                            except Exception as e:
                                printException(e)

                    # Neue Episoden verarbeiten
                    if int(episodes) < curEpisodes:
                        log(f"[INFO] {name} hat neue Episode(n), lade herunter...")
                        for i in range(episodes + 1, curEpisodes + 1):
                            try:
                                dl_ret = anime.downloadEpisode(
                                    i, release, hoster, browser, browserlocation,
                                    myjd_user=myjd_user, myjd_pw=myjd_pass, 
                                    myjd_device=myjd_device, pkgName=customPackage
                                )
                                if dl_ret:
                                    log(f"[DOWNLOAD] Episode {i} von {name} wurde hinzugefügt")
                                    animeentry['episodes'] += 1
                                else:
                                    log(f"[ERROR] Episode {i} konnte nicht hinzugefügt werden")
                                    animeentry['missing'].append(i)
                                    animeentry['episodes'] += 1
                            except Exception as e:
                                printException(e)

                    # Konfiguration speichern
                    with open(botfile, "w") as jfile:
                        json.dump(data, jfile, indent=4, sort_keys=True)

                except Exception as e:
                    print(f"Fehler bei der Verarbeitung von {name}")
                    printException(e)
                    continue

            print(f"Warte {timedelay} Sekunden...")
            time.sleep(timedelay)

        except KeyboardInterrupt:
            print("Bot wurde manuell beendet")
            sys.exit(0)
        except Exception as e:
            print("Unbekannter Fehler in der Hauptschleife")
            printException(e)
            time.sleep(60)  # Bei schweren Fehlern 1 Minute warten

if __name__ == "__main__":
    startbot()
