#' @title Count points contained in polygons
#' @description The function takes longitude-latitude columns from df to create
#' a SpatialPointDataframe
#' @param df df containing geographical information (lat-log cols) about points
#' @param lat_col name of the column containing latitude
#' @param lon_col name of the column containing longitude
#' @return a SpatialPolygonDataframe with @data df containing point counts
#' @importFrom purrr map
counts_pts_in_polygons <- function(df, polygons_df,
                                   lat_col = "decimalLatitude",
                                   lon_col = "decimalLongitude",
                                   crs = "+init=epsg:4326") {
  wgs_84 <- "+init=epsg:4326"

  # if we are working with WGS84(EPSG: 4326) coordinates system
  if (crs == wgs_84) {

    # polygon coordinates in WGS84(EPSG: 4326)
    if (grepl("towgs84=0,0,0", proj4string(polygons_df)) == TRUE) {
      # set up the CRS in projargs
      cat(proj4string(polygons_df), "\n")
      cat("Setting up the CRS...\n")
      proj4string(polygons_df) <- wgs_84
      cat(proj4string(polygons_df), "\n")
    }

    # poly coordinates arn't in WGS84(EPSG: 4326)
    else {
      # reprojection needed
      print("Transforming polygon CRS...")
      spTransform(polygons_df, CRS(wgs_84))
      }
  }

  # make SpatialPointDataFrame
  pts_df <- SpatialPointsDataFrame(coords = df %>% select(lon_col, lat_col),
                                   data = df,
                                   proj4string = CRS(wgs_84))

  # Spatial Join: points over polygons
  pts_square <- over(polygons_df, pts_df, returnList = TRUE)

  # count how many points are in each polygon
  n_of_pts_square <- purrr:::map(pts_square, ~ nrow(.))
  n_of_pts_square <- data.frame(id = names(n_of_pts_square),
                                           value = unlist(n_of_pts_square))

  #add counts on data attribute of SpatialPolygonDataFrame
  polygons_df@data <- bind_cols(polygons_df@data, n_of_pts_square)

  return(polygons_df)
}
