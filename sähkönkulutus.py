# Copyright (c) 2025 Severi Joki
# License: MIT

from datetime import datetime
import calendar

VIIKONPAIVAT = {
    0:"Maanantai",
    1:"Tiistai",
    2:"Keskiviikko",
    3:"Torstai",
    4:"Perjantai",
    5:"Lauantai",
    6:"Sunnuntai"
}
KUUKAUDET = {
    0:"Tammikuu",
    1:"Helmikuu",
    2:"Maaliskuu",
    3:"Huhtikuu",
    4:"Toukokuu",
    5:"Kesäkuu",
    6:"Heinäkuu",
    7:"Elokuu",
    8:"Syyskuu",
    9:"Lokakuu",
    10:"Maaliskuu",
    11:"Joulukuu"
}
def muunna_sahkotiedot(sahkotunti: list) -> list:
    """muutetaan tiedot oikeisiin muotoon. Valmistellaan datetime myös oikeaaseen formaattiin."""
    #sahkonkulutus rivin formaatti == [datetime, kulutus, tuotanto, vuorokauden keskilämpötila]
    a = sahkotunti[0].replace("T", " ")
    date = datetime.fromisoformat(a)
    date = date.replace(tzinfo=None)
    
    kulutus = sahkotunti[1].replace(",",".")
    tuotanto = sahkotunti[2].replace(",",".")
    keskilampotila = sahkotunti[3].replace(",",".")

    muutettu_sahkotunti = []
    muutettu_sahkotunti.append(date)
    muutettu_sahkotunti.append(float(kulutus))
    muutettu_sahkotunti.append(float(tuotanto))
    muutettu_sahkotunti.append(float(keskilampotila))
    return muutettu_sahkotunti

def hae_sahkonkulutus2(start_date:datetime, end_date:datetime, file: str) -> list[str]:
    """
    Hankkii sähkönkulutuksen kahden aikavälin välistä.
    Palauttaa tiedon summattuna ja ottaa lämpötilan keskiarvon.
    Voi tarvittaessa myös palauttaa datan kuukausimuodossa.
    """
    sahkonkulutus = []
    with open(file, "r", encoding="utf-8") as f:
        next(f)
        for tiedot in f:
            tiedot = tiedot.strip()
            sahkotunti = tiedot.split(';')

            #skipataan tieto joka ei ole ajan sisällä
            a = sahkotunti[0].replace("T", " ")
            date = datetime.fromisoformat(a)
            date = date.replace(tzinfo=None)
            if date.date() < start_date.date():
                continue
            if date.date() > end_date.date():
                continue
            sahkonkulutus.append(muunna_sahkotiedot(sahkotunti))

    #sahkonkulutus rivin formaatti == [datetime, kulutus, tuotanto, vuorokauden keskilämpötila]
    result = []
    lampotila = 0
    for row in sahkonkulutus:
        values = row[1:-1]  
        lampotila += row[-1] 

        if not result:
            result = values.copy()  
        else:
            for i, val in enumerate(values):
                result[i] += val

    #lisätään arvot resultsiin. muutetaan ->str ja piste pilkuksi
    result = [format(round(v, 2), ".2f").replace(".",",")for v in result]
    lampotila = lampotila / len(sahkonkulutus)
    result.append(str(round(lampotila, 2)).replace('.', ','))

    return result

def tasoita_lista(nested: list[list[list[str]]])->list[list[str]]:
    """
    Palautta tasoitetun listan sukeltaa sublistoihin tarvittaessa.
    
    """
    
    tulos = []

    def sukella(lista: list):
        """
        Kulkee yhden iteraation alaspäin nested listassa ja tarvittaessa enemmän.
        Palauttaa kaikki muuttujat ryhmiteltynä listoissa "tulos" listaan.
        """
        current = []
        for obj in lista:
            if isinstance(obj, list): #jos osutaan listaan ja currentissa on dataa tallennetaan ne "tulos" muuttujaan
                if current:
                    tulos.append(current)
                    current = []
                sukella(obj) #uusi lista löytyi mennään syvemmälle
            else:
                current.append(obj)
        #listat käyty läpi, tallennetaan viimeiset muuttujat "tulos" muuttujaan
        if current:
            tulos.append(current)

    sukella(nested)
    return tulos

def laske_lista(x:list) -> int:
    """
    palauttaa listan "rivien" lukumäärän.
    jos lista on muotoa list[str] palauttaa 1.
    jos lista on muotoa list[list[str]] palauttaa ala listojen lukumäärän
    """

    if isinstance(x, list) and all(isinstance(i, list) for i in x):
        return len(x)
    
    elif isinstance(x, list):
        return 1
    else:
        return 0 
    
def tasoita_sarakkeet(*listat: list) -> list:
    """
    Ottaa useita listoja ja tasoittaa sarakkeet yhtä leveiksi.
    Tämä varmistaa listojen tulostaessa olevan samoissa sijainneissa.
    luo myös kaikkien syötettyjen paremetrien väliin jakaja viivan.
    """
    
    tasoitetut_listat = []
    for lista in listat:
        tasoitetut_listat.extend(tasoita_lista(lista))
      
    sarakkeiden_suurimmat_leveydet =  [0] * (len(tasoitetut_listat[0]))
    padding = " "

    for lista in tasoitetut_listat:
        for i, item in enumerate(lista):
            if len(str(item)) > sarakkeiden_suurimmat_leveydet[i]:
                sarakkeiden_suurimmat_leveydet[i] = len(str(item))
    for lista in tasoitetut_listat:
        for i,item in enumerate(lista):
            if sarakkeiden_suurimmat_leveydet[i] > len(str(item)):
                lisattava_pituus = sarakkeiden_suurimmat_leveydet[i] - len(str(item))
                lista[i] = item + padding * lisattava_pituus

    for lista in tasoitetut_listat:
        for i, item in enumerate(lista):
            lista[i] = lista[i] + padding*3
                
    

    #Luodaan jakaja viiva laitetaan se oikeaaseen sijaintiin
    viiva = "-"
    jakaja_viiva = ""
    for solu_pituus in sarakkeiden_suurimmat_leveydet:
        jakaja_viiva += viiva * solu_pituus + viiva * 3

    sektion_korkeudet = []
    for sektio in listat:
        sektion_korkeudet.append(laske_lista(sektio))
    for sijainti in sektion_korkeudet[:-1]:
        tasoitetut_listat.insert(sijainti, jakaja_viiva)


    return tasoitetut_listat

def luo_yhteenveto(output_file:str, tiedot:list[str]):
    """
    Docstring for luo_yhteenveto
    Luo tiedoston joka sisältää pääotsikon ja tulostaa tiedot otsikon alle riveittäin
    jokainen list[str] 'tiedot' parametrissä on yksi tulostettava rivi
    """
    with open(output_file, "w", encoding="utf-8") as output_file:

        for row in tiedot:
            for index in row:
                output_file.write(index)
            output_file.write("\n")


    return

def tulosta_tiedot(otsikko:str, tiedot:list[list[str], list[str]]):
    #katsotaan onko tiedot yksi lista vai onko se useita listoja listan sisällä
    if len(tiedot) == 1 and isinstance(tiedot[0], list) and all(isinstance(l, list) for l in tiedot[0]):
        return
    
    print(otsikko)
    for row in tiedot:
        if isinstance(row, list):
            print(*row)
        else:
            print(row)
    print("")
    return

def paivakohtainen_yhteenveto() -> list[list[str]]:
    """
    Kysyy käyttäjältä 2 päivämäärää ja hankkii sähkönkulutuksen datan näiden päivämäärien väliltä
    Palauttaa listan joka sisältää otsikon datalle ja itse datan.
    """
    while True: 
        user_input = input("Anna ensimmäinen päivämäärä (pv.kk.vvvv):")
        try:
            start_date = datetime.strptime(user_input, "%d.%m.%Y")
            break
        except:
            print("Päivämäärä ei ole oikeassa formaatissa.")

    while True: 
        user_input = input("Anna toinen päivämäärä (pv.kk.vvvv):")
        try:
            end_date = datetime.strptime(user_input, "%d.%m.%Y")
            
            break
        except:
            print("Päivämäärä ei ole oikeassa formaatissa.")

    otsikko=f"Yhteenveto päivien {start_date} ja {end_date} välillä."

    yhteenveto = hanki_data_alueelta(start_date,end_date,otsikko)

    return yhteenveto

def kuukausittainen_yhteenveto() -> list[list[str]]:
    """
    Kysyy käyttäjältä yhtä kuukautta ja palauttaa tiedot tästä yhdestä kuukaudesta
    """
    while True: 
        user_input = input("Anna kuukauden numero (1-12):")

        if 0 > int(user_input) or int(user_input) > 12:
            print("Numeron täytyy olla 1-12")
            continue
        month_w_dots = "." + user_input + "."
        start_date = "1"+month_w_dots+"2025"
        start_date = datetime.strptime(start_date, "%d.%m.%Y")
        break
        #except Exception as e:
           # print(e)
            #print("Kuukausi ei ole oikeassa formaatissa.")

    last_day = calendar.monthrange(2025, int(user_input))[1]
    last_day = str(last_day)
    end_date = datetime.strptime(last_day+month_w_dots+"2025","%d.%m.%Y")
    kuukausi = KUUKAUDET[int(user_input)-1]
    otsikko=f"Yhteenveto {kuukausi}n sähkönkulutuksesta."
    yhteenveto = hanki_data_alueelta(start_date,end_date,otsikko)

    return yhteenveto

def vuosittainen_yhteenveto():
    start_date = datetime.strptime("1.1.2025", "%d.%m.%Y")
    end_date = datetime.strptime("31.12.2025", "%d.%m.%Y")
    otsikko="Yhteenveto koko vuoden sähkönkulutuksesta"
    yhteenveto = hanki_data_alueelta(start_date,end_date,otsikko)

    return yhteenveto

def hanki_data_alueelta(start_date:datetime, end_date:datetime, otsikko:str) -> list[list[str]]:
    """
    Lukee datan csv tiedostosta 2 päivämäärän välissä.
    Tulostaa terminaaliin yhteenvedon tiedoista
    Palauttaa tiedot parametri otsikko lisättynä dataan
    """
    data = hae_sahkonkulutus2(start_date,end_date,"2025.csv")
    headerit = ["Kulutus kWh", "Tuotanto", "Keskilämpötila"]
    tasoitetut_tiedot = tasoita_sarakkeet(headerit,data)
    print("")

    tulosta_tiedot(otsikko,tasoitetut_tiedot)

    yhteenveto = []
    yhteenveto.append(otsikko)
    for i in tasoitetut_tiedot:
        yhteenveto.append(i)
    return yhteenveto
def paa_valikko() -> int:
    """
    Kysyy mitä tehdään ohjelmassa ja palauttaa käyttäjän inputin
    Käyttäjän inputti palautuu int 1-4
    """
    while True:
        try:
            print("Valitse raporttityyppi")
            print("1) Päiväkohtainen yhteenveto aikaväliltä")
            print("2) Kuukausikohtainen yhteenveto yhdelle kuukaudelle")
            print("3) Vuoden 2025 kokonaisyhteenveto")
            print("4) Lopeta ohjelma")
            valikko_valinta = int(input("Valitse valintasi (numero):"))
            if not 0 < valikko_valinta < 5:
                print("Numeron täytyy olla 1-4")
                continue
            break
        except:
            print("Virhe. Input ei ollut numero")
    return valikko_valinta

def loppu_valikko() -> int:
    """
    Kysyy mitä tehdään ohjelmassa ensimmäisen valinnan jälkeen ja palauttaa käyttäjän inputin
    Käyttäjän inputti palautuu int 1-3
    """
    while True:
        try:
            print("Mitä haluat tehdä seuraavaksi?")
            print("1) Kirjoita raportti tiedostoon raportti.txt")
            print("2) Luo uusi raportti")
            print("3) Lopeta")
            valikko_valinta = int(input("Numero:"))
            if not 0 < valikko_valinta < 4:
                print("Numeron täytyy olla 1-3")
                continue
            break
        except:
            print("Virhe. Input ei ollut numero")
    return valikko_valinta

def main():
    """
    Hankitaan sähkönkulutuksesta tiedot käyttäjän inputeiden perusteella.
    tulostetaan terminaaliin tai tallennetaan tiedostoon.
    """
    while True:
        first_choice = paa_valikko()
        current_data = []

        if first_choice == 1:
            current_data = paivakohtainen_yhteenveto()
        if first_choice == 2:
            current_data = kuukausittainen_yhteenveto()
        if first_choice == 3:
            current_data = vuosittainen_yhteenveto()
        if first_choice == 4:
            break

        second_choice = loppu_valikko()
        if second_choice == 1:
            luo_yhteenveto("Yhteenveto.txt",current_data)
        if second_choice == 2:
            continue
        if second_choice == 3:
            break

if __name__ == "__main__":
    main()