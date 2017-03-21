# Fototuvastus
TTU meeskonnatöö projekt dokumendifotode kvaliteedi hindamiseks.

Pythoni (3.5.2) kood, õpitud dataset nägude tuvastamiseks ja mõningad näitepildid.

Keskkond arendamisel - Spyder 3.0.0 (https://pythonhosted.org/spyder/installation.html)
Anaconda 4.2.0 (https://www.continuum.io/downloads)
Vajalik paigaldada pakett dlib ('pip install dlib' käivitada nt kaustas ..\Anaconda3\Scripts).

Käesolevalt toimuvad järgmised kontrollid (True/False):

# Foto üldised kontrollid:
1. Foto miinimumõõtude kontroll (600x750px)
2. Kas on tegu värvifotoga
3. Leitud nägude arv (Kui leitakse rohkem nägusid kui üks, siis praegu uuritakse neid edasi, reaalses projektis on otstarbekas edasine uurimine lõpetada).

# Näo kontrollid:
1. Kas nägu on keskel
2. Kas nägu on vertikaalne
3. Kas nägu on otse (vaatab kaamerasse otse)
4. Kas silmade kõrgus pildi kõrguse suhtes on OK (50-70%)
5. Kas suu on suletud
6. Kas nägu on liiga väike
7. Kas nägu on liiga suur

