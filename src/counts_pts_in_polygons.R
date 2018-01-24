#' @title Count points contained in polygons
#' @description The function takes longitude-latitude columns from df to create
#' a SpatialPointsDataframe ane make a spatial join over the
#' SpatialPolygonsDataFrame in order to count how many points are in each
#' polygon. A previous CRS transformation of the polygon's CRS is performed
#' in order to match the CRS given as input.
#' @param df df containing geographical information (lat-log cols) about points
#' @param lat_col name of the column containing latitude
#' @param lon_col name of the column containing longitude
#' @return a SpatialPolygonDataframe with @data df containing point counts
#' @importFrom purrr map
#' @importFrom dplyr bind_cols select
#' @importFrom assertthat assert_that
#' @importFrom sp SpatialPointsDataFrame over proj4string spTransform
counts_pts_in_polygons <- function(df, polygons_df,
                                   lat_col = "decimalLatitude",
                                   lon_col = "decimalLongitude",
                                   crs = "+init=epsg:4326",
                                   verbose = FALSE) {

  # check input parameters
  assert_that(is.data.frame(df))
  assert_that(is.element(lat_col, colnames(occ_Vanessa_BE)))
  assert_that(is.element(lon_col, colnames(occ_Vanessa_BE)))

  # CRS input
  proj4str_str<- proj4string(polygons_df)
  if (!isTRUE(verbose)) {
    # extract short CRS name (+init=...) from CRS string
    poly_crs_str <- substr(proj4str_str,
                           start = str_locate(proj4str_str, "\\+init=")[[1]][1],
                           stop = str_locate(proj4str_str, " ")[[1]][1]-1)
    ifelse(test = is.na(poly_crs_str),
           yes = print(paste("Polygons have no CRS")),
           no = print(paste("Polygons CRS: ", poly_crs_str)))
  } else {
    print(paste("Polygon CRS: ", proj4str_str))
  }

  # CRS transformation
  print("Transforming polygon CRS...")
  polygons_df <- spTransform(polygons_df, CRS(crs))

  # CRS output
  proj4str_str<- proj4string(polygons_df)
  if (!isTRUE(verbose)) {
    # extract short CRS name (+init=...) from CRS string
    poly_crs_str <- substr(proj4str_str,
                           start = str_locate(proj4str_str, "\\+init=")[[1]][1],
                           stop = str_locate(proj4str_str, " ")[[1]][1]-1)
    ifelse(test = is.na(poly_crs_str),
           yes = print("Strange! Polygons have still no CRS"),
           no = print(paste("Polygons CRS:", poly_crs_str)))
  } else {
    print(paste("New polygon CRS:", proj4str_str))
  }

  #transform df in a SpatialPointsDataFrame
  pts_df <- SpatialPointsDataFrame(coords = df %>% dplyr::select(lon_col, lat_col),
                                   data = df,
                                   proj4string = CRS(crs))

  # spatial JOIN: points over polygons
  pts_square <- over(polygons_df, pts_df, returnList = TRUE)

  # count how many points are in each polygon
  n_of_pts_square <- purrr:::map(pts_square, ~ nrow(.))
  n_of_pts_square <- data.frame(id = names(n_of_pts_square),
                                value = unlist(n_of_pts_square))

  # add counts on data attribute of SpatialPolygonDataFrame
  polygons_df@data <- bind_cols(polygons_df@data, n_of_pts_square)
  return(polygons_df)
}
