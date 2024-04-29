import requests
from bs4 import BeautifulSoup
import os

def get_soup_from_url(url):
    """ Effettua una richiesta HTTP all'URL fornito e restituisce un oggetto BeautifulSoup. """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lancia un'eccezione per risposte HTTP non riuscite (es. 404, 500, ecc.)
        # Crea un oggetto BeautifulSoup con il contenuto della pagina
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.RequestException as e:
        print(f"Errore nella richiesta HTTP: {e}")
        return None

def get_lecture_data(soup):
    items = []
    div_tags = soup.find_all('div', class_='resource-item resource-list-page')
    for parent_div in div_tags:
        t = []
        details_div = parent_div.find('div', class_='resource-list-item-details')
        if details_div:
            a_tag_details = details_div.find('a')
            if a_tag_details:
                details_text = a_tag_details.text.strip()  # Estrae il testo del link
                t.append(details_text)

        thumbnail_a_tag = parent_div.find('a', class_='resource-thumbnail')
        if thumbnail_a_tag:
            thumbnail_href = thumbnail_a_tag.get('href')  # Estrae l'href del link thumbnail
            t.append(f"https://ocw.mit.edu{thumbnail_href}")
        items.append(t)

    return items

def filter_pdf(items):
    out = []
    for i in items:
        if(".pdf" in i[1]):
            out.append(i)
    return out

def create_folder_if_not_exists(folder_name):
    """ Crea una cartella se non esiste già. """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Cartella '{folder_name}' creata.")
    else:
        print(f"La cartella '{folder_name}' esiste già.")

def download_pdfs(pdf_list, folder="out"):
    """ Scarica e salva i file PDF da una lista di tuple (title, link). """
    create_folder_if_not_exists("out")
    create_folder_if_not_exists(f"out/{folder}")
    for title, link in pdf_list:
        try:
            response = requests.get(link)
            response.raise_for_status()  # Assicurati che la richiesta sia andata a buon fine
            # Formatta il titolo per creare un nome di file valido
            filename = f"out/{folder}/{title.replace('/', '_').replace(' ', '_')}.pdf"
            # Salva il file nel percorso corrente
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"File '{filename}' scaricato e salvato con successo.")
        except requests.RequestException as e:
            print(f"Errore nel download del file da {link}: {e}")
        except Exception as e:
            print(f"Errore nel salvare il file '{filename}': {e}")

if __name__ == "__main__":
    url = input("Inserisci l'URL della pagina del corso di MIT OpenCourseWare: ")
    url = f"{url}resources/lecture-notes/"
    splitted_url = url.split("/")
    title_index = [n for n,_ in enumerate(splitted_url[1:]) if splitted_url[n-1] == "courses"][0]
    course_name = splitted_url[title_index]
    soup = get_soup_from_url(url)
    if soup is not None:
        items = get_lecture_data(soup)
        items = filter_pdf(items)
        download_pdfs(items, course_name)
    else:
        print("Impossibile ottenere l'oggetto BeautifulSoup.")
