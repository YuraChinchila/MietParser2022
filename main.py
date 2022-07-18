from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import pandas as pd
import time
import os

os.makedirs("csv", exist_ok=True)
os.makedirs("xlsx", exist_ok=True)
os.makedirs("txt", exist_ok=True)

driver = webdriver.Chrome(ChromeDriverManager().install())

urls = {
    "Прикладная информатика": "https://abit.miet.ru/lists/list-all/list.php?c=09.03.03&d=000001853&fo=o&fin=b",
    "Программная инженерия": "https://abit.miet.ru/lists/list-all/list.php?c=09.03.04&d=000001861&fo=o&fin=b",
    "Информатика и вычислительная техника": "https://abit.miet.ru/lists/list-all/list.php?c=09.03.01&d=000001823&fo=o&fin=b",
    "Радиотехника": "https://abit.miet.ru/lists/list-all/list.php?c=11.03.01&d=000001868&fo=o&fin=b",
}

for name, url in urls.items():
    driver.get(url)
    time.sleep(1)

    total_height = int(driver.execute_script("return document.body.scrollHeight"))
    for i in range(1, total_height, 40):
        driver.execute_script("window.scrollTo(0, {});".format(i))

    page = driver.page_source
    soup = BeautifulSoup(page, "lxml")

    tables = soup.find_all("table", {"class": "table table-bordered table-hover dataTable no-footer".split()})
    rows = tables[1].find_all("tr")
    header = [c.get_text() for c in rows[0].find_all("th")]
    d = {h: [] for h in header}

    txt = PrettyTable(header)
    txt.align[header[0]] = "l"
    txt.padding_width = 1

    ag = PrettyTable(header)
    ag.align[header[0]] = "l"
    ag.padding_width = 1

    for row in rows[1:]:
        row_data = []
        flag = True
        for h, c in zip(header, row.find_all("td")):
            text = c.get_text()
            d[h].append(text)
            row_data.append(text)
            if h == "Оригинал" or h == "Согласие":
                flag = flag and (text == "+")
        row_data[0] = int(row_data[0])
        txt.add_row(row_data)
        if flag:
            ag.add_row(row_data)

    pd.DataFrame.from_dict(d).to_csv(f"csv/{name}.csv", index=False, header=True)
    pd.DataFrame.from_dict(d).to_excel(f"xlsx/{name}.xlsx", index=None, header=True)

    with open(f"txt/{name}.txt", "w", encoding="utf-8") as f:
        f.write(str(txt))

    with open(f"txt/{name}(согласие+оригинал).txt", "w", encoding="utf-8") as f:
        f.write(ag.get_string(sortby="#"))

driver.close()
