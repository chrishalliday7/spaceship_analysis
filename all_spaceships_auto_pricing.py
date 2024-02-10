import bs4 as bs
import urllib.request
import pandas as pd
import numpy as np
import warnings
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

warnings.filterwarnings(action="ignore", category=DeprecationWarning)


class SpaceshipPrices:
    def __init__(self):
        self.lti_flag = "x"
        self.df_input = pd.read_csv("spaceships.csv", header=None)
        self.df_input.columns = [
            "URL",
            "Game",
            "Item Type",
            "Manufacturer",
            "Item Name",
            "Sub Item",
        ]
        self.urls = self.df_input["URL"]
        self.summary_dict = {}
        self.filters = str
        self.summary_df = pd.DataFrame

        self.lti_flag = input(
            "Do you want lifetime insurance (x) or 10 year insurance (y) - enter x or y\n"
        )
        if self.lti_flag == "x":
            self.filters = "?starcitizen_insurance=8&product_list_order=price_low_to_high&product_list_limit=36"
            try:
                os.remove("summary_lifetime.csv")
                print("Deleted summary_lifetime.csv")
            except OSError:
                pass
        else:
            self.filters = "?starcitizen_insurance=255&product_list_limit=36&product_list_order=price_low_to_high"
            try:
                os.remove("summary_10year.csv")
                print("Deleted summary_10year.csv")
            except OSError:
                pass

    def check_prices(self):
        for i, url in enumerate(self.urls[:2]):
            if url.count("/") == 7:
                ship_split = url[:-5].split("/")[-2:]
                ship = "_".join(str(x) for x in ship_split)
            elif url.count("/") == 6:
                ship = ship_split = url[:-5].split("/")[-1:][0]
            else:
                raise ValueError(
                    'URL of wrong format, needs to be (e.g.) \n"https://star-hangar.com/star-citizen/spaceships/aegis-dynamics/avenger/renegade.html" \nor "https://star-hangar.com/star-citizen/spaceships/aegis-dynamics/eclipse.html" style...'
                )

            # ship_split = url[:-5].split('/')[-2:]

            # ship = "_".join(str(x) for x in ship_split)

            print("Checking {} of {} - {}".format(i + 1, len(self.urls), ship))

            source = urllib.request.urlopen(url + self.filters).read()

            soup = bs.BeautifulSoup(source, "lxml")

            sellers = soup.find_all("div", class_="seller-details")
            prices = soup.find_all("div", class_="price-final_price")

            sellers = []
            for seller in soup.find_all("div", class_="seller-details"):
                sellers.append(seller.text.strip("\n"))

            prices = []
            for price in soup.find_all("div", class_="price-final_price"):
                prices.append(price.text.strip("\n"))

            info = {"sellers": sellers, "prices": prices}

            df = pd.DataFrame(info)
            df.index += 1

            # concrete foundry has more than one product on the page
            if sellers.count("Seller: Concrete Foundry") > 1:
                locs = []
                second = []
                diff = []
                cf_prices = []
                for j, loc in enumerate(
                    df[df["sellers"] == "Seller: Concrete Foundry"].index.values
                ):
                    top_price = float(
                        df["prices"].iloc[0].replace("$", "").replace(",", "")
                    )
                    # concrete foundry at top
                    if loc == 1:
                        cf_price = float(
                            df["prices"][
                                df[
                                    df["sellers"] == "Seller: Concrete Foundry"
                                ].index.values[0]
                            ]
                            .replace("$", "")
                            .replace(",", "")
                        )
                        price_to_second = (
                            float(
                                df["prices"].iloc[1].replace("$", "").replace(",", "")
                            )
                            - cf_price
                        )
                        second.append(round(price_to_second, 2))
                        price_diff = 0
                        diff.append(price_diff)
                        cf_prices.append(cf_price)
                    # concrete foundry not at top
                    else:
                        cf_price = float(
                            df["prices"][
                                df[
                                    df["sellers"] == "Seller: Concrete Foundry"
                                ].index.values[j]
                            ]
                            .replace("$", "")
                            .replace(",", "")
                        )
                        price_diff = top_price - cf_price
                        diff.append(round(price_diff, 2))
                        price_to_second = "n/a"
                        second.append(price_to_second)
                        cf_prices.append(cf_price)
                    locs.append(loc)
                self.summary_dict[i] = [
                    url,
                    locs,
                    second,
                    diff,
                    top_price,
                    cf_prices,
                    ship,
                ]
            # concrete foundry has one item and is at the top, return price to second place
            elif df[df["sellers"] == "Seller: Concrete Foundry"].index.values == 1:
                if len(sellers) > 1:
                    top_price = float(
                        df["prices"][
                            df[
                                df["sellers"] == "Seller: Concrete Foundry"
                            ].index.values[0]
                        ]
                        .replace("$", "")
                        .replace(",", "")
                    )
                    price_to_second = (
                        float(df["prices"].iloc[1].replace("$", "").replace(",", ""))
                        - top_price
                    )
                    price_to_second = round(price_to_second, 2)
                else:
                    price_to_second = "No competition on page"
                self.summary_dict[i] = [
                    url,
                    [1],
                    [price_to_second],
                    "n/a",
                    top_price,
                    [top_price],
                    ship,
                ]
            # concrete foundry has no items in first 36 products listed low to high
            elif "Seller: Concrete Foundry" not in sellers:
                self.summary_dict[i] = [
                    url,
                    "Not on first page",
                    ["n/a"],
                    "n/a",
                    "n/a",
                    "n/a",
                    ship,
                ]
            # concrete foundry has one item in first 36 products but is not at the top
            # logic here to automate price change
            else:
                cf_price = float(
                    df["prices"][
                        df[df["sellers"] == "Seller: Concrete Foundry"].index.values[0]
                    ]
                    .replace("$", "")
                    .replace(",", "")
                )
                top_price = float(
                    df["prices"].iloc[0].replace("$", "").replace(",", "")
                )
                price_diff = top_price - cf_price
                cf_pos = df[df["sellers"] == "Seller: Concrete Foundry"].index.values
                self.summary_dict[i] = [
                    url,
                    cf_pos,
                    ["n/a"],
                    [round(price_diff, 2)],
                    top_price,
                    [cf_price],
                    ship,
                ]
            with open("all_price_lists.txt", "a") as f:
                f.write(url + "\n")
                dfAsString = df.to_string(header=False, index=True)
                f.write(dfAsString)
                f.write("\n")
                f.write("\n")

    def output_results(self):
        self.summary_df = pd.DataFrame.from_dict(self.summary_dict, orient="index")
        self.summary_df.columns = [
            "URL",
            "CF position",
            "Price to second place",
            "Price to top",
            "Top price",
            "CF price",
            "Ship name",
        ]
        summary_to_save = self.summary_df.copy()
        summary_to_save["URL"] = (
            '=HYPERLINK("' + summary_to_save["URL"] + self.filters + '")'
        )

        saved = False
        while saved == False:
            try:
                if self.lti_flag == "x":
                    summary_to_save.to_csv("summary_lifetime.csv")
                    saved = True
                else:
                    summary_to_save.to_csv("summary_10year.csv")
                    saved = True
            except PermissionError:
                print("Close the fucking excel sheet")


class AutoUpdate:
    def __init__(self, summary_df, lti_flag):
        self.auto_price_df = summary_df
        self.lti_flag = lti_flag
        self.undercut_price = 0.00  # change this number to change the undercut price

        self.ship_lookup = pd.read_csv("ship_lookup.csv")
        options = webdriver.EdgeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Edge(options=options)

    def show_df(self):
        print(self.auto_price_df.head())

    def login(self, email):
        self.driver.get(
            "https://star-hangar.com/customer/account/login/referer/aHR0cHM6Ly9zdGFyLWhhbmdhci5jb20v"
        )
        username = self.driver.find_element(By.NAME, "login[username]")
        username.send_keys(email)
        print("You now have 15 seconds to enter your password...")
        time.sleep(15)

    def single_update(self, ship_name: str):
        ship_split = ship_name.split(" ")
        url = self.auto_price_df.loc[
            self.auto_price_df["Ship name"] == ship_split[0].lower(), "URL"
        ].item()

        price_change_url = "https://star-hangar.com/starhangar_marketplaceexpansion/product/editprice/id/"
        if self.lti_flag == "x":
            flag = "LTI"
        else:
            flag = "Ten"

        try:
            product_code = self.ship_lookup.loc[
                self.ship_lookup["URL"] == url, flag
            ].item()

            top_price = float(
                self.auto_price_df.loc[
                    self.auto_price_df["Ship name"] == ship_split[0].lower(),
                    "Top price",
                ].item()
            )
            if len(ship_split) > 1:
                ind = int(ship_split[-1]) - 1
                cf_price = self.auto_price_df.loc[
                    self.auto_price_df["Ship name"] == ship_split[0].lower(), "CF price"
                ].tolist()[0][ind]
            else:
                cf_price = self.auto_price_df.loc[
                    self.auto_price_df["Ship name"] == ship_split[0].lower(), "CF price"
                ].tolist()[0][0]
            print(
                "Product {} ({}) costs {}. The top price is {}. Therefore, price changed to {}.".format(
                    ship_name,
                    product_code,
                    cf_price,
                    top_price,
                    round(top_price - self.undercut_price, 2),
                )
            )
        except ValueError:
            print("{} is causing a problem...".format(url))

        self.driver.get(price_change_url + str(product_code))
        time.sleep(1)
        self.driver.find_element(By.NAME, "product[price]").clear()
        price = self.driver.find_element(By.NAME, "product[price]")
        price.send_keys(top_price - self.undercut_price)
        time.sleep(1)
        self.driver.find_element(By.ID, "save-btn").click()
        time.sleep(1)


if __name__ == "__main__":
    try:
        os.remove("all_price_lists.txt")
        print("Deleted all_price_lists.txt")
    except OSError:
        pass

    prices = SpaceshipPrices()

    prices.check_prices()
    prices.output_results()

    auto = AutoUpdate(prices.summary_df, prices.lti_flag)

    # print(auto.auto_price_df.head())

    auto.login("cwbeckman@gmail.com")

    # auto.single_update('Titan 1',0.01)
