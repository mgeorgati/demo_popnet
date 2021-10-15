The present folder contains scripts for the preprocessing of the population data of Amsterdam
1. The raw data at 100x100m grid cells derive from the municipality of Amsterdam (through NIDI) and got delivered in EXCEL format. 
You need : 
    - a folder: ams_ProjectData/PopData/rawData : stores raw data as delivered from NIDI (EXCEL) for even years from 1992-2018, 
    for total population, countries of origin, movements among cells, age groups, housing
    - Data Cleaning (Part 1-3), to transform the data in a way to correspond to DST/UNSD abbreviations and plot various line diagrams.
    - Preprocessing to convert EXCEL to TIFF (main,process,csv_to_raster,variables) & calculate percentages of migrants by region of origin for each year in question

2. The raw data at neighborhood level deriving from Statistics Netherlands after processing from NIDI (EXCEL) without geometry
You need: 
    - a folder: ams_ProjectData/PopData/rawDataNeighborhoods to include the
        demographic data (1995-2019) + codebook : 106 attributes 
        education (2019) : UNDEFINED
        income (2014,2016,2018) : UNDEFINED
    - NeighborhoodDemoDataPreparation : assign geometry to neighborhoods

    How to downscale?
