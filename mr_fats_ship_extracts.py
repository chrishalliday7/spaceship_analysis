"""
need to find the market price of upgrade FROM 300i TO 135c within last month
then extend search to previous 6 months
"""

# %%
import requests
import bs4 as bs
import pandas as pd
from datetime import datetime, timedelta

ccus = pd.read_csv(r"required_inputs/ccus_2023-01-16.csv", header=0)

unique_ships = ccus["to"].unique().tolist()
print(unique_ships)

# %%
summary_list = []
# start loop through all ships here
for ship in unique_ships[:10]:
    summary_df = pd.DataFrame(
        columns=["To", "From", "Lowest Price", "Two Week Lowest", "Six Month Lowest"]
    )

    url = "http://mrfats.mobiglas.com/search?q={}&f=ccu&h=true&s=price".format(ship)
    get_url = requests.get(url, timeout=120)
    get_text = get_url.text
    soup = bs.BeautifulSoup(get_text, "lxml")
    numbers = soup.find_all("span", class_="other_page_num")
    number_values = [number.text for number in numbers if number]
    number_vals = [
        int(item) for sublist in number_values for item in sublist if item.isdigit()
    ]

    print("Discovering prices of all upgrades to {}".format(ship))

    if len(number_vals) > 0:
        pages = []
        for page in range(max(number_vals)):
            print("Checking page {} of {}...".format(page + 1, max(number_vals)))
            df_page = pd.DataFrame(columns=["To / From", "Price", "Seller", "Dates"])
            # maybe use threading here to obtain all page results simultaneously
            # eg urls = [url&page=1,2,3 etc]
            # instead of pages.append, may need to be ship_dict[ship].append?
            url = "http://mrfats.mobiglas.com/search?q={}&f=ccu&h=true&s=price&page={}".format(
                ship, page + 1
            )
            get_url = requests.get(url)

            get_text = get_url.text
            soup = bs.BeautifulSoup(get_text, "lxml")

            divs = soup.find_all("div", class_="row")
            tags = [tag for tag in divs if "search-result" not in "".join(tag["class"])]

            to_from = [tag.find("h1") for tag in tags]
            to_from_values = [
                " ".join(header.text.split()) for header in to_from if header
            ]

            prices = [tag.find("div", class_="price nobr") for tag in tags]
            price_values = [price.text for price in prices if price]

            sellers = [tag.find("div", class_="clickable nobr") for tag in tags]
            seller_values = [seller.text for seller in sellers if seller]

            dates = [tag.select("div.nobr") for tag in tags]
            if len(dates) != 0:
                dates.pop(0)
            date_values = [dates[i][2].text for i in range(len(dates))]
            date_format = "%d-%b %Y"
            date_objects = list(
                map(lambda x: datetime.strptime(x, date_format).date(), date_values)
            )

            df_page["To / From"] = to_from_values
            df_page["Price"] = price_values
            df_page["Seller"] = seller_values
            df_page["Dates"] = date_objects

            pages.append(df_page)

        df = pd.concat(pages)
        df.columns = ["To / From", "Price", "Seller", "Dates"]

        grouped = df.groupby(["To / From"])
        unique = df["To / From"].unique()

        df_dict = {}

        for i, val in enumerate(unique):
            df_dict[val] = grouped.get_group(val)
            date_seller = [
                "{} {}".format(b_, a_)
                for a_, b_ in zip(df_dict[val]["Seller"], df_dict[val]["Dates"])
            ]
            summary_df.loc[i] = [
                val.split(" ")[0],
                (val.split("(from "))[1].split(")")[0],
                min(df_dict[val]["Price"]),
                df_dict[val]
                .loc[
                    (
                        df_dict[val]["Dates"]
                        >= (datetime.now() - timedelta(days=14)).date()
                    )
                ]["Price"]
                .min(),
                df_dict[val]
                .loc[
                    (
                        df_dict[val]["Dates"]
                        >= (datetime.now() - timedelta(days=180)).date()
                    )
                ]["Price"]
                .min(),
            ]
        summary_list.append(summary_df)


output_df = pd.concat(summary_list)

output_df["Two Week Lowest"].fillna("Price not changed in last 2 weeks.", inplace=True)
output_df["Six Month Lowest"].fillna(
    "Price not changed in last 6 months.", inplace=True
)

saved = False
while saved == False:
    try:
        output_df.to_csv("mr_fats_prices.csv", index=False)
        saved = True
    except:
        print("Close the csv...")
