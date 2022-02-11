# lake_travis_water_level_viewer
![sample image](https://raw.githubusercontent.com/bthaman/lake_travis_water_level_viewer/master/sample_plots/water_level.png)
Python script to download and plot Lake Travis water levels from 1943 to current

Combines historical avg daily water levels from 1943 with observations from LCRA's Hydromet website (https://hydromet.lcra.org/home/GaugeDataList/?siteNumber=3963&siteType=lakelevel)

1. Uses selenium to download a .csv from the hydromet site containing lake levels at 15-minute increments over the preceding 2 weeks.
2. Reads the .csv, converts to daily averages, and appends daily averages to historical data.
3. The historical data is updated every time the script is run.
4. Uses matplotlib to plot the results.
5. Plots water level and percent full. 
