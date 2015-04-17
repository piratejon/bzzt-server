library(signal)

normalize_accel_vector <- function(x, y, z) {
  sqrt((x*x)+(y*y)+(z*z))
}

highpass_filter <- function(d, freq) {
  bf <- butter(3, freq, "low")
  filter(bf, d)
}

setup_color <- function(x, yellow_limit, red_limit) {
  if (x > red_limit) 2
  else if (x > yellow_limit) 1
  else 0
}

setup_colors <- function(series) {
  mu <- mean(series)
  sigma <- sd(series)
#sapply(series, function(x) setup_color(abs(x-mu), sigma, 3*sigma))
  sapply(series, function(x) (x-mu)/sigma)
}

get_acc_colors <- function(acc) {
  norm_acc <- normalize_accel_vector(acc$x, acc$y, acc$z)
  hpf <- highpass_filter(norm_acc, 0.005)
  hpfc <- cbind(acc$ns, setup_colors(hpf))
}

bzzt_accel_filter <- function(acc_in, acc_out) {
  acc <- read.csv(gzfile(acc_in), skip=1, header=FALSE)
  colnames(acc) <- c('ns','x','y','z')
  colors <- get_acc_colors(acc)
  write.table(colors, file=acc_out,row.names=FALSE, col.names=FALSE, sep=',')
}

args <- commandArgs(trailingOnly = TRUE)
bzzt_accel_filter(args[1], args[2])

