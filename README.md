# Habit Tracker 

Habit Tracker je jednostavna Flask aplikacija sa SQLite bazom podataka koja omogućava korisnicima da unesu navike, 
postave nedeljni cilj, prate napredak i brišu postojeće navike.  

##  Pokretanje aplikacije

Aplikacija se pokreće pomoću Docker Compose-a u terminalu:  

docker compose up --build

Nakon pokretanja, dostupna je na adresi http://localhost:8000
Podaci se čuvaju u Docker volumenu, pa ostaju sačuvani i nakon gašenja kontejnera.
