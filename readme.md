# IPK - Počítačové komunikace a sítě
## HTTP resolver doménových jmen
Zadanie projektu spočívalo vo vytvorení serveru, ktorý zaistí preklad doménových mien a bude komunikovať prokotolom HTTP.

Ako prvé som implementoval server pomocou SocketServeru, ktorý s pomocou triedy BaseRequestHandler spracuje prichádzajúce požiadavky, ktoré ďalej spracujeme my pomocou funkcií popísaných nižšie.

#### editRequestedString(data):
	 Táto funkcia plní hlavnú úlohu, rozparsuje prichádzajúcu hlavičku na základe požiadavku
	 (GET/POST/neexistujúca metóda) a na základe týchto poznatkov zavolá príslušné 
	 funkcie pre GET(checkForRequestGET) alebo POST(checkforRequestPOST).
#### checkForRequest[GET/POST]:
	Obe tieto funkcie už vykonávajú (resp. volajú funkcie), ktoré zabezpečia preklad domény  
	prípadne zadanej IP adresy v tvare IPv4 (v opačnom prípade sa jedná o chybu 400 Bad Request).
	V týchto funkciách tiež prebehnú práce so stringom, tak, aby mohli byť bezpečne zavolané
	funkcie gethostbyaddr (pre IP) alebo gethostbyname (pre doménové mená).
#### FindIP / checkForPostIP:
	Tieto funkcie zabezpečia samotný preklad [doména => IP] prípadne [IP => doména],
	a v prípade, že preklad prebehne neúspešne funkcia vracia prázdny reťazec, ktorý je neskôr
	spracovaný vo funkcii, ktorá volala práve jednu z týchto funkcií.
## DODATOK K IMPLEMENTÁCII
Moja implementácia počíta s faktom, že  za predpokladu, že ***aspoň JEDEN dotaz je správny*** a v správnom tvare, všetky ZLÉ dotazy sú v tom momente odignorované a ***je navrátené 200 OK + výpis správneho dotazu***.
+ V prípade, že sú ***všetky dotazy v zlom tvare***, vracia sa ***400 Bad Request***.
+ V prípade, že sú ***dotazy v správnom tvare ale nenájdené***, vracia sa ***404 Not Found***.
+ V prípade, že sú dotazy v ***správnom tvare ale nenájdenéa zároveň sú tu aj dotazy v zlom tvare***, vracia sa ***400 Bad Request***.
+ Prázdne riadky sú považované za ***400 Bad Request***, ale v prípade, že je tu ***aspoň jeden dobrý dotaz,*** ***sú*** podobne ako ostatné chybné dotazy ***ignorované***.
