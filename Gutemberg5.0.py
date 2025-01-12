import requests
import csv
from bs4 import BeautifulSoup
import copy

base_url = "https://www.gutenberg.org/ebooks/search/?sort_order=downloads&start_index="
#Select the number of results 
number_results = 1000
 
all_titles = []
all_links = []
book_library = {}

#Doing a request depending on the number of results. 
for index in range(1, number_results, 25): 
    #Only changing the index of the URL
    html = requests.get(base_url + str(index)) 
    print("-------------------------------------------------")
    print("SCRAPPING URL " + base_url + str(index))
    print("-------------------------------------------------")
    s = BeautifulSoup(html.content, "html.parser")
    results = s.find(id="content")
    book_titles = results.find_all(class_="title")
    book_links = [results.find_all("")]
    
    #Obtaining the book titles
    if index == 1:
        for title in book_titles[2:]:
            all_titles.append(title.text)
    else:
        for title in book_titles:
            all_titles.append(title.text)

            
    #Obtaining the book links
    for ale in s.find_all("a"):
        link = ale.attrs["href"]
        if len(link) > 8 and "/ebooks/" in link and link[8].isnumeric():
            all_links.append("https://www.gutenberg.org/" + ale.attrs["href"])
            
#Creating a dictionary with the results

for rank in range(1,number_results + 1): 

    book = {}
    book["name"] = all_titles[rank - 1]
    book["url"] = all_links[rank - 1]
    book_library[rank] = book

#Doing a request per scraped book
for rank in range(1,number_results + 1): 
    r = requests.get(book_library[rank]["url"])
    soup = BeautifulSoup(r.text, "html.parser")
    book_table = soup.find("table", class_ = "bibrec")
    wanted_titles = ["Author","Aborn","Adeath", "Translator", "Tborn", "Tdeath","Subject","Language"]
    book_library[rank].update((dict.fromkeys(wanted_titles,"")))
    book_library[rank]["Subject"] = []

    #Obtaining all the rows of the info table
    for row in book_table.find_all("tr"): 
        titles = row.find_all("th")
        contents = row.find_all("td")
        
        #Obtaining all the info titles
        for title in titles: 
            title_text = title.get_text(strip = True)
        #Obtaining the content of the table  
        for content in contents: 
            content_text = content.get_text(strip = True)
            
        #Adding the info to the dictionary if we need it
        if title_text in wanted_titles: 
            
            if title_text == "Subject":
                book_library[rank]["Subject"].append(content_text)
            #elif title_text == "Author" or title_text == "Translator":
                #Dates_obtainer(title_text, content_text)

            else:
                book_library[rank][title_text] = content_text
                
            
           
            print("++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(title_text)
            print(content_text)
            print("++++++++++++++++++++++++++++++++++++++++++++++++++")

    print("")
    print("$$$$$$$$$$$$$$$$$$$$$")
    print(f"Scraping book {rank}/{number_results}")
    print(book_library[rank]["name"])
    print("$$$$$$$$$$$$$$$$$$$$$")

book_library_copy = copy.deepcopy(book_library)

#Function to obtain the dates and clean the names
def Dates_obtainer(typ,content):
    
    #If there is no Author/Translator ir returns nothing
    if book_library_copy[book][typ] == "":
        return
        
    #Changes the variables depending on the type (Author/Translator)
    if typ == "Author":
        born = "Aborn"
        death = "Adeath"
    else:
        born = "Tborn"
        death = "Tdeath"
        
    #Separates the name of the Author/Transaltor by the last comma (Lauridsen, Peter, 1846-1923)
    sep_index = content.rfind(", ")
    name_trimed = content[:sep_index]
    date_trimed = content[sep_index + 2:]
    book_library_copy[book][typ] = name_trimed 
    
    #If the second part has a number, it is a true date
    number_list = [0,1,2,3,4,5,6,7,8,9]
    date_contains_digit = False
    for number in number_list:
        if str(number) in date_trimed:
            date_contains_digit = True
            continue
    
    if date_contains_digit:
        
        #Removes "?" from the date
        date_trimed = date_trimed.replace("?","")
        
        #If the date is a century, simply does nothing
        if "century" in date_trimed:
            return
        BCE = False
        
        #Checks if the date is Befor Christ and removes the letters
        if "BCE" in date_trimed:
            BCE = True
            date_trimed = date_trimed.replace("BCE","")
            
        #Divides by born date and death date depending on the character "-"
        dash_index = date_trimed.rfind("-")
        born_formated = date_trimed[:dash_index]
        death_formated = date_trimed[dash_index + 1:]

        #If the date is befor Christ it makes the date negative
        if BCE:
            born_formated = "-" + born_formated
            death_formated = "-" + death_formated

        #Finally it asigns the values in the correspondig key in the dictionary
        book_library_copy[book][born] = born_formated
        book_library_copy[book][death] = death_formated

    #In the case that the second part has no number, it is a name. So it apends it to the name key
    else:
        book_library_copy[book][typ] = book_library_copy[book][typ] + ", " + date_trimed
        book_library_copy[book][born] = ""
                          
#Creating a list of lists to create the CSV file
book_lists = [["Rank", "Title", "Link", "Author","Aborn","Adeath", "Translator", "Tborn", "Tdeath","Subject","Language"]]
for book in book_library_copy:
    book_list = []
    book_list.append(book)
    for info in list(book_library_copy[book].keys()):
        if info == "Author" or info == "Translator":
            Dates_obtainer(info,book_library_copy[book][info])
            book_list.append(book_library_copy[book][info])
        else:
            book_list.append(book_library_copy[book][info])
    book_lists.append(book_list)
    
print("Titles Scraped: " +  str(len(all_titles)))
print("Links scraped: " + str(len(all_links)))
#Creating the CSV file
with open("1000.csv", "w", encoding = "utf-8", newline = "") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(book_lists)