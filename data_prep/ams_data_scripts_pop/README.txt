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

Folder Processes:
    1. CleanRawGridCellData --> Cleaning and harmonizing the data at grid cell level 
    2. CleanRawNeighData --> Cleaning and harmonizing the data at neighborhood level
    3. csvTOraster --> Convert excel to raster, sum by regions and merge tiffs
        .csv_to_raster 
            - excel to geojson, summing populations by regions ({0}_dataVectorGrid.geojson, {0}_dataVectorGridSums.geojson)
            - geojson to raster
        .calcPercentages 
            - calc Z0, Z1 in geojson (0}_dataVectorGridDivs.geojson)
            - rasterize Z0, Z1
        .normalise
        .mergeSelectionCoI !->>>>> Needs attention <<<<<-!
    
    4. aggregateGridtoNeigh --> Zonal Statistcs to aggregate the grid cell data to neighborhood level
    
    5. bivariateMaps !->>>>> Needs attention <<<<<-! R
    
    6. correlations --> Checking Correlations among selections and countries based on regions of origin --> returning matrix in EXCEL and PNG
    
    7. randomPoints --> !->>>>> Needs attention <<<<<-! 

    8. tricolore

    9. vizRawData --> Visualizations of raw data in line graphs 
        This folder contains:
            1. lineDiagramCountriesPerRegion.py 
                A. reads the sum geojsons files from PopData
                B. sums the population by geographical region based on variables and saves it to EXCEL files in the EXCEL folder
                C. reads the EXCEL files and produces line diagrams for each region
            2. Visualizations.py --> line diagrams for various groups 
    
    10. PySal -->  

    11. disaggregation