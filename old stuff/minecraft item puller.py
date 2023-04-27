import requests 
URL = "https://www.digminecraft.com/lists/item_id_list_pc.php"
page = requests.get(URL)

print(page.text)