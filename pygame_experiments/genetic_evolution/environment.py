# Temperature:
#   quadratic function of y, representing temp at poles and equator
#   perlin noise for regional and weather variation
#   simple offset for seasonal variation
#   simple offset for time of day
#   simple offset for altitude

# Map:
#   numpy pixel array
#   perlin noise for terrain
#   normal map generated from terrain
#   biome dependent on initial temperature
#   biome dependent on altitude and normal
#   zooming in renders perlin noise at higher resolution and frequency
