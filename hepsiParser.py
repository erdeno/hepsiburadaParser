from bs4 import BeautifulSoup as soup
import requests, sqlite3

db = sqlite3.connect("HepsiburadaProducts.sqlite")
cur = db.cursor()

cur.execute(
    """CREATE TABLE IF NOT EXISTS Products (
         ID INTEGER  PRIMARY KEY AUTOINCREMENT,
         NAME           TEXT    NOT NULL,
         OLDPRICE            INTEGER     NOT NULL,
         DISCOUNT        INTEGER     NOT NULL,
         FINALPRICE         INTEGER     NOT NULL)"""
)


def addToTable(name, oldPRice, discount, finalPrice):
    sorgu = 'SELECT * FROM Products WHERE NAME = "{}"'.format(name)
    cur.execute(sorgu)
    sonuc = cur.fetchone()
    if not sonuc:
        cur.execute(
            "INSERT INTO Products(NAME, OLDPRICE, DISCOUNT, FINALPRICE) VALUES (?,?,?,?)",
            (name, oldPRice, discount, finalPrice),
        )
        print("Ekleme Başarılı.")
        db.commit()
    elif finalPrice != returnPrice(name):
        print(finalPrice, returnPrice(name))
        updatePrice(name, finalPrice)
    else:
        print("Değişiklik Yok.")


def returnPrice(name):
    sorgu = 'SELECT FINALPRICE FROM Products WHERE NAME = "{}"'.format(name)
    cur.execute(sorgu)
    sonuc = cur.fetchone()
    return sonuc[0]


def updatePrice(name, newprice):
    old_price = returnPrice(name)
    cur.execute(
        'UPDATE Products SET FINALPRICE= {} WHERE NAME= "{}"'.format(newprice, name)
    )
    print(
        """
ALERT ALERT ALERT PRICE HAS CHANGED.
{}
    """.format(
            name
        )
    )
    db.commit()


with requests.Session() as se:
    se.headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "tr",
    }

my_url = "https://www.hepsiburada.com/laptop-notebook-dizustu-bilgisayarlar-c-98?filtreler=isletimsistemi:Windows%E2%82%AC2010%E2%82%AC20Home,Windows%E2%82%AC2010%E2%82%AC20Pro&siralama=coksatan"


def convertToFloat(price: str):
    if "," in price:
        price = price.split(",")
        price = float(".".join(price))
        return price


def sorgu():
    response = se.get(my_url)

    page_soup = soup(response.content, "html.parser")

    products = page_soup.find_all("div", attrs={"class": "product-detail"})
    idno = 0
    for product in products:
        if product.find("div", attrs={"class": "green-text"}):
            title = product.h3.text.strip()
            old_price = (
                product.find("div", attrs={"class": "price-container"})
                .text.strip()
                .split()[3]
            )
            old_price = convertToFloat(old_price)
            discount_rate = (
                product.find("div", attrs={"class": "green-text"})
                .text.strip()
                .split()[1]
                .split("%")[1]
            )
            final_price = (
                product.find("div", attrs={"class": "price-value"})
                .text.strip()
                .split()[0]
            )
            final_price = convertToFloat(final_price)
            addToTable(title, old_price, discount_rate, final_price)


def main():
    sorgu()
    cur.close()


if __name__ == "__main__":
    main()
