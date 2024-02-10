import os
import pandas as pd
from babel import numbers
import decimal
import dash
from dash.dependencies import Input, Output
from dash import dcc, html, ctx
from all_spaceships_auto_pricing import SpaceshipPrices, AutoUpdate

app = dash.Dash()


class RunApp:
    def __init__(self):
        self.graph_df = pd.DataFrame
        self.prices = SpaceshipPrices()
        self.not_top = None
        self.auto = None

    def instantiate_checkers(self):
        self.prices.check_prices()
        self.prices.output_results()

        self.prices.summary_df = self.prices.summary_df
        self.not_top = self.prices.summary_df.loc[
            self.prices.summary_df["CF position"].str.get(0) != 1
        ]

    def create_graph(self):
        graph_dict = {}

        for i, val in enumerate(self.prices.summary_df["CF position"]):
            if (len(val) == 1) & (val[0] != 1) & (not isinstance(val[0], str)):
                if len(val) == 1:
                    graph_dict[
                        self.prices.summary_df["Ship name"].iloc[i].title()
                    ] = self.prices.summary_df["Price to top"].iloc[i][0]
                elif len(val) > 1:
                    for j in range(len(val)):
                        graph_dict[
                            self.prices.summary_df["Ship name"].iloc[i].title()
                            + " "
                            + str(j + 1)
                        ] = self.prices.summary_df["Price to top"].iloc[i][j]
            elif (
                (len(val) > 0)
                & (len([x for x in val if x != 1]) > 0)
                & (not isinstance(val, str))
            ):
                for j in range(len([x for x in val if x != 1])):
                    ind_list = [p for p, e in enumerate(val) if e != 1]
                    graph_dict[
                        self.prices.summary_df["Ship name"].iloc[i].title()
                        + " "
                        + str(ind_list[j] + 1)
                    ] = self.prices.summary_df["Price to top"].iloc[i][ind_list[j]]

        self.graph_df = pd.DataFrame.from_dict(
            graph_dict, orient="index", columns=["Price to top"]
        )
        self.graph_df["Ship name"] = self.graph_df.index
        self.graph_df.reset_index(inplace=True)
        self.graph_df.drop("index", axis=1, inplace=True)

        x = self.graph_df["Ship name"]
        y = self.graph_df["Price to top"] * -1

        return x, y


run_app = RunApp()
run_app.instantiate_checkers()
x, y = run_app.create_graph()

run_app.auto = AutoUpdate(run_app.prices.summary_df, run_app.prices.lti_flag)

app.layout = html.Div(
    children=[
        html.H1(children="Conrad's Star Hangar Dashboard"),
        dcc.Graph(
            id="not_top_graph",
            figure={
                "data": [
                    {"x": x, "y": y, "type": "bar", "name": "Spaceships"},
                ],
                "layout": {
                    "title": "Ships Not in First Place: Price Difference to the Top"
                },
            },
        ),
        html.Div(
            id="login",
            children=[html.Button("Login", id="login_button", n_clicks=0)],
            style={"display": "block", "margin-bottom": "50px"},
        ),
        html.Div(
            [
                "Select your maximum price difference to the top for automatic price updating (in US$00.00 format)...",
                html.Br(),
                dcc.Input(
                    id="threshold",
                    type="number",
                    placeholder="Enter maximum difference...",
                    style={
                        "width": "25%",
                        "marginRight": "10px",
                        "display": "inline-block",
                        "margin-top": "10px",
                    },
                ),
                html.Button(
                    "Confirm auto update", id="confirm_auto_button", n_clicks=0
                ),
                html.Div(id="auto_update_confirmed"),
            ],
            style={"width": "50%", "display": "block", "margin-bottom": "50px"},
        ),
        html.Div(
            [
                dcc.Dropdown(
                    id="fig_dropdown",
                    options=[{"label": s.title(), "value": s} for s in x],
                    value=None,
                )
            ],
            style={"width": "10%", "display": "inline-block", "height": "25px"},
        ),
        html.Div(
            id="ship_name",
            style={
                "width": "25%",
                "display": "inline-block",
                "margin-left": "15px",
                "vertical-align": "middle",
                "height": "20px",
            },
        ),
        html.Div(
            id="confirm_div",
            children=[html.Button("Confirm update", id="confirm_button", n_clicks=0)],
            style={"display": "none"},
        ),
        html.Div(
            id="confirmation",
            style={"width": "25%", "display": "inline-block", "margin-left": "15px"},
        ),
    ],
)


@app.callback(
    Output(component_id="login_button", component_property="n_clicks"),
    [Input(component_id="login_button", component_property="n_clicks")],
)
def login(clicks):
    if clicks > 0:
        run_app.auto.login("cwbeckman@gmail.com")


@app.callback(
    Output(component_id="ship_name", component_property="children"),
    [Input(component_id="fig_dropdown", component_property="value")],
)
def print_ship(input_data):
    if input_data is not None:
        input = input_data.split(" ")
        if len(input) > 1:
            ind = int(input[-1]) - 1
            price_diff = run_app.prices.summary_df.loc[
                run_app.prices.summary_df["Ship name"] == input[0].lower(),
                "Price to top",
            ].tolist()[0][ind]
            top_price = run_app.prices.summary_df.loc[
                run_app.prices.summary_df["Ship name"] == input[0].lower(), "Top price"
            ].iloc[0]
            current_price = run_app.prices.summary_df.loc[
                run_app.prices.summary_df["Ship name"] == input[0].lower(), "CF price"
            ].tolist()[0][ind]
            url = run_app.prices.summary_df.loc[
                run_app.prices.summary_df["Ship name"] == input[0].lower(), "URL"
            ].iloc[0]
        else:
            price_diff = run_app.prices.summary_df.loc[
                run_app.prices.summary_df["Ship name"] == input_data.lower(),
                "Price to top",
            ].tolist()[0][0]
            top_price = run_app.prices.summary_df.loc[
                run_app.prices.summary_df["Ship name"] == input_data.lower(),
                "Top price",
            ].iloc[0]
            current_price = run_app.prices.summary_df.loc[
                run_app.prices.summary_df["Ship name"] == input[0].lower(), "CF price"
            ].tolist()[0][0]
            url = run_app.prices.summary_df.loc[
                run_app.prices.summary_df["Ship name"] == input_data.lower(), "URL"
            ].iloc[0]
        if run_app.prices.lti_flag == "x":
            lti_filter = "?starcitizen_insurance=8&product_list_order=price_low_to_high&product_list_limit=36"
        else:
            lti_filter = "?starcitizen_insurance=255&product_list_limit=36&product_list_order=price_low_to_high"
        return "The CF price for the {} is {}. This is {} from the top. Suggested update price is {}. URL: {}".format(
            input_data,
            numbers.format_currency(decimal.Decimal(current_price), "USD"),
            numbers.format_currency(decimal.Decimal(abs(price_diff)), "USD"),
            numbers.format_currency(
                decimal.Decimal(round(top_price, 2) - run_app.auto.undercut_price),
                "USD",
            ),
            url + lti_filter,
        )
    else:
        return "Select a ship to individually update..."


@app.callback(
    [
        Output(component_id="auto_update_confirmed", component_property="children"),
        Output(component_id="confirm_auto_button", component_property="n_clicks"),
    ],
    [
        Input(component_id="threshold", component_property="value"),
        Input(component_id="confirm_auto_button", component_property="n_clicks"),
    ],
)
def auto_update(price_delta, clicks):
    def update(delta):
        updated_ships = []
        for ship in x:
            ship_split = ship.split(" ")
            if len(ship_split) > 1:
                ind = int(ship_split[-1]) - 1
                price_diff = run_app.prices.summary_df.loc[
                    run_app.prices.summary_df["Ship name"] == ship_split[0].lower(),
                    "Price to top",
                ].tolist()[0][ind]
                if abs(price_diff) < delta:
                    run_app.auto.single_update(ship)
                    updated_ships.append(ship)
            else:
                price_diff = run_app.prices.summary_df.loc[
                    run_app.prices.summary_df["Ship name"] == ship.lower(),
                    "Price to top",
                ].tolist()[0][0]
                if abs(price_diff) < delta:
                    run_app.auto.single_update(ship)
                    updated_ships.append(ship)
        return "{} are all less than {} from the top and have been automatically updated.".format(
            ", ".join(str(x) for x in updated_ships),
            numbers.format_currency(decimal.Decimal(delta), "USD"),
        )

    if clicks == 1:
        careful = False
        if (price_delta > 5) & (careful == False):
            careful = True
            return (
                "${} is a large price difference - click confirm again if you're sure.".format(
                    price_delta
                ),
                1,
            )
        else:
            return update(price_delta), 0
    elif clicks == 2:
        return update(price_delta), 0
    else:
        return "", 0


@app.callback(
    Output(component_id="confirm_div", component_property="style"),
    [Input(component_id="fig_dropdown", component_property="value")],
)
def show_confirm_button(_):
    if "fig_dropdown" == ctx.triggered_id:
        return {
            "width": "10%",
            "display": "inline-block",
            "height": "20px",
            "margin-left": "15px",
        }
    else:
        return {"display": "none"}


@app.callback(
    [
        Output(component_id="confirmation", component_property="children"),
        Output(component_id="confirm_button", component_property="n_clicks"),
    ],
    [
        Input(component_id="fig_dropdown", component_property="value"),
        Input(component_id="confirm_button", component_property="n_clicks"),
    ],
)
def update_on_click(ship, clicks):
    if ship is None:
        return "", 0
    else:
        if clicks == 1:
            run_app.auto.single_update(ship)
            return "Success! {} price updated.".format(ship), 0
        else:
            return "", 0


if __name__ == "__main__":
    app.run_server(debug=True)
