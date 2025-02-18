

base_url = "https://ingress.pressreader.com/se2skyservices"

get_id_url = f"{base_url}/catalog/v1/routes/publication?publication=proceso"
# REQUIRES BEARER TOKEN
# cid

base_1 = f"{base_url}/IssueInfo/GetIssueInfoByCid"
params_1 = {
    "cid": "24em",
    "issueDate": "20250201"
}
issue_url = f"{base_1}?cid=24em&issueDate=20250201"
# REQUIRES BEARER TOKEN
# se obtiene Issue.Issue  -> issue
# se obtiene Layout.LayoutVersion -> version

base_2 = f"{base_url}/pagesMetadata"
params_2 = {
    "issue": "24em2025020100000051001001"
}
articles_url = f"{base_2}/?issue=24em2025020100000051001001"
# REQUIRES BEARER TOKEN
# Se obtienen los títulos y las páginas de todos los artículos

base_3 = f"{base_url}/Articles/GetItems"
params_3 = {
    "articles[]": "281947433539351",
}
article_url = f"{base_3}?articles%5B%5D=281947433539351"
# REQUIRES BEARER TOKEN

base_4 = f"{base_url}/IssueInfo/GetPageKeys"
params_4 = {
    "issue": "24em2025020100000051001001",
    "pageNumber": 0,
    "preview": True
}
keys_url = f"{base_4}?issue=24em2025020100000051001001&pageNumber=0&preview=true"
# De allí se obtiene, para cada una de las páginas:
# Key -> ticket
# PageNumber -> page
# La escala se puede mantener constante en 300

image_base = "https://i.prcdn.co/img"
params_image = {
    "file": "24em2025020100000051001001",
    "page": 53,
    "scale": 300,
    "ticket": "AJJRugzQQsgZCNpOvQmC1to%3D"
}
image_url = f"{image_base}?file=24em2025020100000051001001&page=53&scale=300&ticket=AJJRugzQQsgZCNpOvQmC1to%3D"

