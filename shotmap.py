import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import matplotlib.font_manager as font_manager
import json
import requests
from bs4 import BeautifulSoup
import streamlit as st
import os


class GoalMap:
    def __init__(self, url, season):
        self.df = self.getDf(url, season)
        self.df["X"] = self.df["X"] * 100
        self.df["Y"] = self.df["Y"] * 100
        self.player = self.df["player"].iloc[0]
        self.season = season
        self.total_shots = self.df.shape[0]
        self.total_goals = self.df[self.df["result"] == "Goal"].shape[0]
        self.total_xG = self.df["xG"].sum()
        self.xG_per_shot = self.total_xG / self.total_shots
        self.points_average_distance = self.df["X"].mean()
        self.actual_average_distance = 120 - (self.df["X"] * 1.2).mean()
        self.background_color = "#0f1116"
        self.goal_colour = "#3d7ed9"
        self.font_path = "Arvo-Regular.ttf"

    def getDf(self, url, season):
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")
        scripts = soup.find_all("script")
        strings = scripts[3].string
        ind_start = strings.index("('") + 2
        ind_end = strings.index("')")

        json_data = strings[ind_start:ind_end]
        json_data = json_data.encode("utf-8").decode("unicode_escape")

        data = json.loads(json_data)
        df = pd.DataFrame(data)
        seasonDf = df[df["season"] == season]
        seasonDf.loc[:, "xG"] = seasonDf["xG"].astype(float)
        seasonDf.loc[:, "X"] = seasonDf["X"].astype(float)
        seasonDf.loc[:, "Y"] = seasonDf["Y"].astype(float)
        return seasonDf

    def draw_map(self, save):
        font_props = font_manager.FontProperties(fname=self.font_path)

        pitch = VerticalPitch(
            pitch_type="opta",
            half=True,
            pitch_color=self.background_color,
            pad_bottom=0.5,
            line_color="white",
            linewidth=0.75,
            axis=True,
            label=True,
        )

        # create a subplot with 2 rows and 1 column
        fig = plt.figure(figsize=(8, 12))
        fig.patch.set_facecolor(self.background_color)

        # Top row for the team names and score
        # [left, bottom, width, height]

        ax1 = fig.add_axes([0, 0.7, 1, 0.2])
        ax1.set_facecolor(self.background_color)
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)

        ax1.text(
            x=0.5,
            y=0.85,
            s=f"{self.player}",
            fontsize=20,
            fontproperties=font_props,
            fontweight="bold",
            color="white",
            ha="center",
        )
        ax1.text(
            x=0.5,
            y=0.7,
            s=f"All shots in the {self.season}-{(int(self.season) + 1) % 100} season",
            fontsize=14,
            fontweight="bold",
            fontproperties=font_props,
            color="white",
            ha="center",
        )
        ax1.text(
            x=0.25,
            y=0.5,
            s=f"Low Quality Chance",
            fontsize=12,
            fontproperties=font_props,
            color="white",
            ha="center",
        )

        # add a scatter point between the two texts
        ax1.scatter(
            x=0.37,
            y=0.53,
            s=100,
            color=self.background_color,
            edgecolor="white",
            linewidth=0.8,
        )
        ax1.scatter(
            x=0.42,
            y=0.53,
            s=200,
            color=self.background_color,
            edgecolor="white",
            linewidth=0.8,
        )
        ax1.scatter(
            x=0.48,
            y=0.53,
            s=300,
            color=self.background_color,
            edgecolor="white",
            linewidth=0.8,
        )
        ax1.scatter(
            x=0.54,
            y=0.53,
            s=400,
            color=self.background_color,
            edgecolor="white",
            linewidth=0.8,
        )
        ax1.scatter(
            x=0.6,
            y=0.53,
            s=500,
            color=self.background_color,
            edgecolor="white",
            linewidth=0.8,
        )

        ax1.text(
            x=0.75,
            y=0.5,
            s=f"High Quality Chance",
            fontsize=12,
            fontproperties=font_props,
            color="white",
            ha="center",
        )

        ax1.text(
            x=0.45,
            y=0.27,
            s=f"Goal",
            fontsize=10,
            fontproperties=font_props,
            color="white",
            ha="right",
        )
        ax1.scatter(
            x=0.47,
            y=0.3,
            s=100,
            color=self.goal_colour,
            edgecolor="white",
            linewidth=0.8,
            alpha=0.7,
        )

        ax1.scatter(
            x=0.53,
            y=0.3,
            s=100,
            color=self.background_color,
            edgecolor="white",
            linewidth=0.8,
        )

        ax1.text(
            x=0.55,
            y=0.27,
            s=f"No Goal",
            fontsize=10,
            fontproperties=font_props,
            color="white",
            ha="left",
        )

        ax1.set_axis_off()

        ax2 = fig.add_axes([0.05, 0.25, 0.9, 0.5])
        ax2.set_facecolor(self.background_color)

        pitch.draw(ax=ax2)

        # create a scatter plot at y 100 - average_distance
        ax2.scatter(
            x=90, y=self.points_average_distance, s=100, color="white", linewidth=0.8
        )
        # create a line from the bottom of the pitch to the scatter point
        ax2.plot(
            [90, 90], [100, self.points_average_distance], color="white", linewidth=2
        )

        # Add a text label for the average distance
        ax2.text(
            x=90,
            y=self.points_average_distance - 4,
            s=f"Average Distance\n{self.actual_average_distance:.1f} yards",
            fontsize=10,
            fontproperties=font_props,
            color="white",
            ha="center",
        )

        for x in self.df.to_dict(orient="records"):
            pitch.scatter(
                x["X"],
                x["Y"],
                s=300 * x["xG"],
                color=self.goal_colour if x["result"] == "Goal" else self.background_color,
                ax=ax2,
                alpha=0.7,
                linewidth=0.8,
                edgecolor="white",
            )

        ax2.set_axis_off()

        # add another axis for the stats
        ax3 = fig.add_axes([0, 0.2, 1, 0.05])
        ax3.set_facecolor(self.background_color)
        ax3.set_xlim(0, 1)
        ax3.set_ylim(0, 1)

        ax3.text(
            x=0.25,
            y=0.5,
            s="Shots",
            fontsize=20,
            fontproperties=font_props,
            fontweight="bold",
            color="white",
            ha="left",
        )

        ax3.text(
            x=0.25,
            y=0,
            s=f"{self.total_shots}",
            fontsize=16,
            fontproperties=font_props,
            color=self.goal_colour,
            ha="left",
        )

        ax3.text(
            x=0.38,
            y=0.5,
            s="Goals",
            fontsize=20,
            fontproperties=font_props,
            fontweight="bold",
            color="white",
            ha="left",
        )

        ax3.text(
            x=0.38,
            y=0,
            s=f"{self.total_goals}",
            fontsize=16,
            fontproperties=font_props,
            color=self.goal_colour,
            ha="left",
        )

        ax3.text(
            x=0.53,
            y=0.5,
            s="xG",
            fontsize=20,
            fontproperties=font_props,
            fontweight="bold",
            color="white",
            ha="left",
        )

        ax3.text(
            x=0.53,
            y=0,
            s=f"{self.total_xG:.2f}",
            fontsize=16,
            fontproperties=font_props,
            color=self.goal_colour,
            ha="left",
        )

        ax3.text(
            x=0.63,
            y=0.5,
            s="xG/Shot",
            fontsize=20,
            fontproperties=font_props,
            fontweight="bold",
            color="white",
            ha="left",
        )

        ax3.text(
            x=0.63,
            y=0,
            s=f"{self.xG_per_shot:.2f}",
            fontsize=16,
            fontproperties=font_props,
            color=self.goal_colour,
            ha="left",
        )

        ax3.set_axis_off()

        file_name = f"{(self.player).replace(" ", "_")}_{self.season}.png"
        fig.savefig(
            file_name,
            dpi=300,
            facecolor=self.background_color,
            bbox_inches="tight",
        )
        return file_name


def main():
    # Haaland: 8260, Salah: 1250 max 13053
    st.title("Player Shot Map")
    st.write("By Aiden Lyons")
    st.write("Enter the player's name and season to generate the shot map.")
    player_input = st.text_input("Enter the player's name", placeholder="Erling Haaland")
    season_input = st.text_input("Enter the season", placeholder="2022")
    id = getID(player_input)
    url = f'https://understat.com/player/{id}'
    
    if st.button("Generate Shot Map"):
        if player_input and season_input:
            map = GoalMap(url, season_input)
            file = map.draw_map(save=True)
            
            if os.path.exists(file):
                st.image(file)
        else:
            st.error("Please input both player and season to generate the shot map.")

def getID(name):
    url = f'https://understat.com/main/getPlayersName/{name}'
    headersList = {
        "Accept": "*/*",
        "User-Agent": "Player Name ID",
    }
    try:
        response = requests.request("GET", url, data="", headers=headersList)
        response = response.json()
    except Exception as e:
        print(f"Error {e}: Could not get player ID")
        return None
    player = response["response"]["players"][0]
    player_id = player["id"]
    return player_id

if __name__ == "__main__":
    main()
