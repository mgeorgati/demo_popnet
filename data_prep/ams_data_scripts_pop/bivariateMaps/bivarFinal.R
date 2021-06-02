cat("
library(rstudioapi)
library(tidyverse) # ggplot2, dplyr, tidyr, readr, purrr, tibble
library(magrittr) # pipes
library(lintr) # code linting
library(sf) # spatial data handling
library(raster) # raster handling (needed for relief)
library(viridis) # viridis color scale
library(cowplot) # stack ggplots
library(rmarkdown)
library(rasterVis)
library(rgdal)",
    file = "manifest.R")

install.packages("raster")
library(raster)
r <- raster("C:/FUME/PopNetV2/data_prep/ams_ProjectData/temp_tif/corine/water_ams_CLC_2012_2018.tif")
# convert to a df for plotting in two steps,
# First, to a SpatialPointsDataFrame
water_pts <- rasterToPoints(r, spatial = TRUE)
# Then to a 'conventional' dataframe
water_df  <- data.frame(water_pts)
rm(water_pts, r)

waterPlot <- ggplot() +
  geom_raster(data = water_df ,alpha = 3/10, aes(x = x, y = y, fill = water_ams_CLC_2012_2018 )) +
  scale_fill_continuous(guide = FALSE) +
  scale_alpha_continuous(guide = FALSE) +
  theme(axis.text        = element_blank(),
        axis.ticks       = element_blank(),
        axis.title       = element_blank(),
        panel.background = element_blank(),
        legend.background = element_blank())


theme_map <- function(...) {
  theme_minimal() +
    theme(
      text = element_text(color = "#666666"),
      # remove all axes
      axis.line = element_blank(),
      axis.text.x = element_blank(),
      axis.text.y = element_blank(),
      axis.ticks = element_blank(),
      # add a subtle grid
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank(),
      # background colors
      plot.background = element_rect(fill = "#FFFFFF",
                                     color = NA),
      panel.background = element_rect(fill = "#FFFFFF",
                                      color = NA),
      legend.background = element_rect(fill = "#FFFFFF",
                                       color = NA),
    
      # borders and margins (I have commented these as these generate an error with the plotly, else it works perfect)
      # plot.margin = unit(c(.5, .5, .2, .5), "cm"),
      # panel.border = element_blank(),
      # panel.spacing = unit(c(-.1, 0.2, .2, 0.2), "cm"),
      # titles
      legend.title = element_text(size = 11),
      legend.text = element_text(size = 9, hjust = 0,
                                 color = "#666666"),
      plot.title = element_text(size = 15, hjust = 0.5,
                                color = "#666666"),
      plot.subtitle = element_text(size = 10, hjust = 0.5,
                                   color = "#666666",
                                   margin = margin(b = -0.1,
                                                   t = -0.1,
                                                   l = 2,
                                                   unit = "cm"),
                                   debug = F),
      # captions
      plot.caption = element_text(size = 7,
                                  hjust = .5,
                                  margin = margin(t = 0.2,
                                                  b = 0,
                                                  unit = "cm"),
                                  color = "#939184"),
      ...
    )
}


sf <- read_sf("C:/FUME/PopNetV2/data_prep/ams_ProjectData/AncillaryData/adm/districts.geojson") 

listNames <- c("Z0_totalMigmean" ,"Z0_Oceaniamean"  ,"Z0_EuropeNotEUmean" ,  "Z0_EuropeEUnoLocalmean")

for (i in listNames){
  print(paste("The year is", i))
  # create 3 buckets for migrant group
  sf[[i]] %>%
    quantile(probs = seq(0, 1, length.out = 4)) -> groupA
  groupA
  
  # create 3 buckets for total population
  sf$l1_totalpopmean %>%
    quantile(probs = seq(0, 1, length.out = 4)) -> total
  total
  
  bivariate_color_scale <- tibble(
    "3 - 3" = "#3F2949", # high inequality, high income
    "2 - 3" = "#435786",
    "1 - 3" = "#4885C1", # low inequality, high income
    "3 - 2" = "#77324C",
    "2 - 2" = "#806A8A", # medium inequality, medium income
    "1 - 2" = "#89A1C8",
    "3 - 1" = "#AE3A4E", # high inequality, low income
    "2 - 1" = "#BC7C8F",
    "1 - 1" = "#CABED0" # low inequality, low income
  ) %>%
    gather("group", "fill")
  
  # cut into groups defined above and join fill
  sf %<>%
    mutate(
      Group_quantiles = cut(
        sf[[i]],
        breaks = groupA,
        include.lowest = TRUE
      ),
      POP_quantiles = cut(
        l1_totalpopmean,
        breaks = total,
        include.lowest = TRUE
      )
      ,
      # by pasting the factors together as numbers we match the groups defined
      # in the tibble bivariate_color_scale
      
      group = paste(
        as.numeric(Group_quantiles), "-",
        as.numeric(POP_quantiles)
      )
    ) %>%
    # we now join the actual hex values per "group"
    # so each municipality knows its hex value based on the his gini and avg
    # income value
    left_join(bivariate_color_scale, by = "group")
  
  map <- ggplot(
    # use the same dataset as before
    data = sf
  ) +
    # color municipalities according to their gini / income combination
    geom_sf(
      aes(
        fill = sf$fill
      ),
      # use thin white stroke for municipalities
      color = "white",
      size = 0.1
    ) +
    
    scale_fill_identity()+
    # add titles
    labs(x = NULL,
         y = NULL,
         title = paste("Population Density and Share of ",i,", 2018"),
         caption = "Amsterdam")+
    
    # add the theme
    theme_map() 
  
  # separate the groups
  bivariate_color_scale %<>%
    separate(group, into = c("MigGroup", "Pop"), sep = " - ") %>%
    mutate(MigGroup = as.integer(MigGroup),
           Pop = as.integer(Pop))
  
  legend <- ggplot() +
    geom_tile(
      data = bivariate_color_scale,
      mapping = aes(
        x = MigGroup,
        y = Pop,
        fill = fill)
    ) +
    scale_fill_identity() +
    labs(x = "Larger Migration--->",
         y = "Higher Population--->") +
    theme_map() +
    # make font small enough
    theme(
      axis.title = element_text(size = 6)
    ) +
    # quadratic tiles
    coord_fixed()
  
  ggplot(map, waterPlot)
  
  ggdraw() +
    
    #draw_plot(map, 0, 0, 1, 1) +
    draw_plot(waterPlot, 0, 0, 1, 1) +
    draw_plot(legend, 0.75, 0.07, 0.25, 0.25) -> Biharbivariate
  
  Biharbivariate + draw_plot(map)
  save_plot(paste("C:/FUME/PopNetV2/data_prep/ams_ProjectData/AncillaryData/",i,".png"), Biharbivariate)
  
  
  }



