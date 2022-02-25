library(tidyverse)
library(magrittr)
library(sf)
library(viridis)
library(cowplot)
library(plotly)
library(ggiraph)
library(biscale)

read_sf("C:/Users/NM12LQ/OneDrive - Aalborg Universitet/PopNetV2/data_prep/crc_ProjectData/PopData/2019/temp_shp/2019_dataVectorGrid.shp") -> sf
data <- bi_class(sf, x = MigPerTota, y = totalPop, style = "quantile", dim = 3)
names(Districtshapes)
Districtshapes$geometry

# create 3 buckets for Area
Districtshapes$MigPop %>%
  quantile(probs = seq(0, 1, length.out = 4)) -> quantiles_Area

# create 3 buckets for Area
Districtshapes$totalPop %>%
  quantile(probs = seq(0, 1, length.out = 4)) -> quantiles_Pop

# create color scale that encodes two variables
# red for Area and blue for POP
# the special notation with gather is due to readibility reasons
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
Districtshapes %<>%
  mutate(
    Area_quantiles = cut(
      MigPop,
      breaks = quantiles_Area,
      include.lowest = TRUE
    ),
    POP_quantiles = cut(
      totalPop,
      breaks = quantiles_Pop,
      include.lowest = TRUE
    ),
    # by pasting the factors together as numbers we match the groups defined
    # in the tibble bivariate_color_scale
    group = paste(
      as.numeric(Area_quantiles), "-",
      as.numeric(POP_quantiles)
    )
  ) %>%
  # we now join the actual hex values per "group"
  # so each municipality knows its hex value based on the his gini and avg
  # income value
  left_join(bivariate_color_scale, by = "group")

map <- ggplot(
  # use the same dataset as before
  data = Districtshapes
) +
  
  # color municipalities according to their gini / income combination
  geom_sf(
    aes(
      fill = Districtshapes$fill
    ),
    # use thin white stroke for municipalities
    color = "white",
    size = 0.1
  ) +
  scale_fill_identity()+
  # add titles
  labs(x = NULL,
       y = NULL,
       title = "Population Density for Districts of Bihar",
       caption = "by :Ayush Patel\n inspired from Timo Grossenbacher") +
  # add the theme
  #theme_map()
  
  # separate the groups
  bivariate_color_scale %<>%
  separate(group, into = c("Area", "Pop"), sep = " - ") %>%
  mutate(Area = as.integer(Area),
         Pop = as.integer(Pop))

legend <- ggplot() +
  geom_tile(
    data = bivariate_color_scale,
    mapping = aes(
      x = Area,
      y = Pop,
      fill = fill)
  ) +
  scale_fill_identity() +
  labs(x = "Larger Area--->",
       y = "Higher Population--->") +
  #theme_map() +
  # make font small enough
  theme(
    axis.title = element_text(size = 6)
  ) +
  # quadratic tiles
  coord_fixed()

ggdraw() +
  draw_plot(map, 0, 0, 1, 1) +
  draw_plot(legend, 0.75, 0.07, 0.15, 0.15) -> Biharbivariate

Biharbivariate