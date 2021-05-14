"""# Loading shapefile into postgresql
    print("Importing Grid to postgres")
    gridPath = temp_shp_path + "/{0}_grid.shp".format(city)
    cmds = 'shp2pgsql -I -s 3035  {0} public.{1}_grid | psql'.format(gridPath, city)
    subprocess.call(cmds, shell=True)

    # Loading shapefile into postgresql
    print("Importing Iteration Grid to postgres")
    gridPath = temp_shp_path + "/{0}_iteration_grid.shp".format(city)
    cmds = 'shp2pgsql -I -s 3035 {0} public.{1}_iteration_grid | psql'.format(gridPath, city)
    subprocess.call(cmds, shell=True)"""
    