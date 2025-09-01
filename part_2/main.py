import pandas as pd
import plotly.express as px
import streamlit as st

#Keeping the layout wide and sidebar state expanded
st.set_page_config(page_title="LoL Dashboard",
                   layout="wide", 
                   initial_sidebar_state="expanded")

#Creating head title
st.title("LPL regional finals 2024")

#Decorating the data to optimise performance
@st.cache_data
def load_data(path: str):
    data = pd.read_csv(path, delimiter=";")
    return data 


df = load_data("LPL_regionalFinals_2024.csv")

def select_all_button(name_for_button: str, on_or_off_from_start:bool, name_for_filter:str, default_value, column ):
    """ 
    Creating  a function to create new filters to the sidebar with an option to select all the filters at once
    """
    select_all_button_pressed = st.sidebar.checkbox(label=name_for_button, value=on_or_off_from_start)
    if select_all_button_pressed == True:
        all_in_filter = st.sidebar.multiselect(
            label=name_for_filter, 
            options=sorted(column.unique()),
            default=sorted(column.unique())
        )
    else:
        all_in_filter = st.sidebar.multiselect(
            label=name_for_filter, 
            options=sorted(column.unique()),
            default=default_value     
        )
    return all_in_filter

#Creating filters to sidebar
st.sidebar.header("Pick a filter:")

player = select_all_button(
    name_for_button="Select all players",
    on_or_off_from_start=False, 
    name_for_filter="Select player(s)", 
    default_value=["Tarzan"], column=df["Player"]
    )
role = select_all_button(
    name_for_button="Select all roles", 
    on_or_off_from_start=False, 
    name_for_filter="Select role(s)", 
    default_value=["JUNGLE"], 
    column=df["Role"] 
    )
team = select_all_button(
    name_for_button="Select all teams",
    on_or_off_from_start=False, 
    name_for_filter="Select team(s)",
    default_value=["WBG"], 
    column=df["Team"] 
    )
outcome = select_all_button(
    name_for_button="Select both",
    on_or_off_from_start=True, 
    name_for_filter="Select win or loss",
    default_value=["Win"], 
    column=df["Outcome"] 
    )

#Query the columns based on the selection (combining our options with our dataframe)
df_selection = df.query(
    "Player == @player & Role == @role & Team == @team & Outcome == @outcome"
)

#Gets all the total wins and losses for red and blue side
win_rate_red_side = df_selection[df_selection["Side"] == "Red"]["Outcome"].value_counts().reset_index()
win_rate_blue_side = df_selection[df_selection["Side"] == "Blue"]["Outcome"].value_counts().reset_index()


#Creating pie charts that shows win rate for red and blue side of the map
pie_chart_blue = px.pie(
    data_frame=win_rate_blue_side, 
    names="Outcome", 
    values="count",
    title="Win rate based on Blue side",
    color="Outcome",
    width=250,
    color_discrete_map={"Win": "royalblue",
                        "Loss": "darkblue" }
    )

pie_chart_red = px.pie(
    data_frame=win_rate_red_side, 
    names="Outcome", 
    values="count",
    title="Win rate based on Red side",
    color="Outcome",
    width=250,
    color_discrete_map={"Win": "red",
                        "Loss": "darkred" }
    )

#Counts the wins and losses from blue side and making it to a data frame
most_picked_champion = df_selection["Pick"].value_counts().head().reset_index()
most_picked_champion.columns = ["Pick", "Count"]

#Creating bar chart with most picked champion
bar_chart_most_picked_champions = px.bar(
    title="Top picks",
    orientation="h",
    data_frame=most_picked_champion,
    y="Pick",
    x="Count",
    template="plotly",
    width=600,
    height=250
)

#Counts the wins and losses from blue side and making it to a data frame
most_banned_champion = df_selection["Ban"].value_counts().head().reset_index()
most_banned_champion.columns = ["Ban", "Count"]

#Creating bar chart with most picked champion
bar_chart_most_banned_champions = px.bar(
    title="Most banned",
    orientation="h",
    data_frame=most_banned_champion,
    y="Ban",
    x="Count",
    template="plotly",
    width=600,
    height=250
)

#Calculate average kills for all players and select top 5
avg_kills_all_games = df_selection.groupby(["Player"])["Kills"].mean().reset_index().sort_values(by="Kills", ascending=False).head()

#Create line chart for top 5 players by average kills
kills_chart = px.line(
    avg_kills_all_games,
    x="Player",
    y="Kills",
    title="Top 5 Players by Average Kills (All Games)",
    line_shape="linear",  # Optional: shape of the line
    markers=True,  # Shows markers at each data point in the chart
    template="plotly_white",
)
#Set the color of the markers to blue
kills_chart.update_traces(marker=dict(color="yellow")) 


#Calculate average assists for all players and select top 5
avg_assists_all_games = df_selection.groupby(["Player"])["Assists"].mean().reset_index().sort_values(by="Assists", ascending=False).head()

#Create line chart for top 5 players by average assists
assists_chart = px.line(
    avg_assists_all_games,
    x="Player",
    y="Assists",
    title="Top 5 Players by Average Assists (All Games)",
    line_shape="linear",
    markers=True,
    template="plotly_white",
)
#Update the line chart to have a specific color for assists
assists_chart.update_traces(marker=dict(color="green"))


#Calculate average deaths for all players and select top 5
avg_deaths_all_games = df_selection.groupby(["Player"])["Deaths"].mean().reset_index().sort_values(by="Deaths", ascending=False).head()

#Create line chart for top 5 players by average deaths
deaths_chart = px.line(
    avg_deaths_all_games,
    x="Player",
    y="Deaths",
    title="Top 5 Players by Average Deaths (All Games)",
    line_shape="linear",
    markers=True,
    template="plotly",
)
#Update the line chart to have a specific color for deaths
deaths_chart.update_traces(marker=dict(color="red"))

#Placeing the pie charts next to each other by creating two new columns
left_column, right_column = st.columns([0.7, 0.3])
with left_column:
    st.dataframe(df_selection, width=1100, height=700)
    st.plotly_chart(kills_chart, use_container_width=True)
    st.plotly_chart(assists_chart, use_container_width=True)
    st.plotly_chart(deaths_chart, use_container_width=True)
with right_column:
    st.plotly_chart(figure_or_data=pie_chart_blue, theme="streamlit", key="blue_pie_chart")
    st.plotly_chart(figure_or_data=pie_chart_red, theme="streamlit", key="red_pie_chart")
    st.plotly_chart(bar_chart_most_picked_champions, key="most_picked_bar_chart")
    st.plotly_chart(bar_chart_most_banned_champions, key="most_banned_bar_chart")

    
