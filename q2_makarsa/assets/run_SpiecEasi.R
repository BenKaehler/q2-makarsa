#!/usr/bin/env Rscript

library("optparse")
library("biomformat")

errQuit <- function(mesg, status = 1) {
  message("Error: ", mesg)
  q(status = status)
}

option_list <- list(
  make_option(c("-i", "--input-file"),
    action = "store", type = "character",
    help = "File path to biom file to be processed"
  ),
  make_option(c("-o", "--output-file"),
    action = "store", type = "character",
    help = "File path to output file. If already exists, will be overwritten"
  ),
  make_option(c("-m", "--method"),
    action = "store", default = NULL, type = "character",
    help = "method that will pass into spieceasi, available options mb, glasso"
  ),
  make_option(c("-l", "--lambda-min-ratio"),
    action = "store", default = NULL, type = "numeric",
    help = "the scaling factor that determines the minimum sparsity/lambda parameter"
  ),
  make_option(c("-d", "--nlambda"),
    action = "store", default = NULL, type = "numeric",
    help = "nlambda"
  ),
  make_option(c("-r", "--rep-num"),
    action = "store", default = NULL, type = "integer",
    help = "pulsar-params"
  ),
  make_option(c("-c", "--ncores"),
    action = "store", default = 1, type = "integer",
    help = "pulsar-params"
  ),
  make_option(c("-t", "--thresh"),
    action = "store", default = 0.05, type = "numeric",
    help = "Threshold for StARS criterion"
  ),
  make_option(c("-b", "--subsample-ratio"),
    action = "store", default = 0.8, type = "numeric",
    help = "Subsample size for StARS"
  ),
  make_option(c("-s", "--seed"),
    action = "store", default = NULL, type = "numeric",
    help = "Set the random seed for subsample set"
  ),
  make_option("--sel-criterion",
    action = "store", default = "stars", type = "character",
    help = " Specifying criterion/method for model selection, Accepts 'stars' [default], 'bstars' (Bounded StARS)"
  ),
  make_option(c("-v", "--verbose"),
    action = "store_true", default = FALSE,
    help = "Print extra output [default]"
  ),
  make_option("--not-lambda-log",
    action = "store_true", default = FALSE,
    help = "lambda-log should values of lambda be distributed logarithmically (TRUE) or linearly (FALSE) between lamba-min and lambda-max "
  ),
  make_option("--not-pulsar-select",
    action = "store_true", default = FALSE,
    help = "pulsar select flag to perform model selection"
  ),
  make_option("--lambda-min",
    action = "store", default = NULL, type = "numeric",
    help = "lower lambda limit if lambda-log is FALSE"
  ),
  make_option("--lambda-max",
    action = "store", default = NULL, type = "numeric",
    help = "upper lambda limit if lambda-log is FALSE"
  )
)

opt <- parse_args(OptionParser(option_list = option_list))


# assign each of the arguments to an appropriately named R variable
inp.file <- opt$`input-file`
out.file <- opt$`output-file`
method <- opt$method
lambda.min.ratio <- opt$`lambda-min-ratio`
nlambda <- opt$nlambda
rep.num <- opt$`rep-num`
ncores <- opt$ncores
thresh <- opt$thresh
subsample.ratio <- opt$`subsample-ratio`
seed <- opt$seed
sel.criterion <- opt$`sel-criterion`
verbose <- opt$verbose
lambda.log <- !(opt$`not-lambda-log`)
lambda.min <- opt$lambda_min
lambda.max <- opt$lambda_max
pulsar.select <- !(opt$`not-pulsar-select`)

### VALIDATE ARGUMENTS ###

data <- lapply(strsplit(inp.file, ", ")[[1]], function (x) {t(as.matrix(biom_data(read_biom(x))))})

# Output files are to be filenames (not directories) and are to be
# removed and replaced if already present.

if (dir.exists(out.file)) {
  errQuit("Output filename ", out.file, " is a directory.")
} else if (file.exists(out.file)) {
  invisible(file.remove(out.file))
}

### LOAD LIBRARIES ###

suppressWarnings(library(SpiecEasi))
suppressWarnings(library(igraph))
suppressWarnings(library(Matrix))

se.out <- spiec.easi(
  data,
  method = method,
  lambda.min.ratio = lambda.min.ratio,
  nlambda = nlambda,
  pulsar.select = pulsar.select,
  pulsar.params = list(
    thresh = thresh,
    subsample.ratio = subsample.ratio,
    rep.num = rep.num,
    seed = seed,
    ncores = ncores
  )
)

features <- list(Feature=unlist(lapply(data, colnames)))

if (method=='mb') {
bm <- symBeta(getOptBeta(se.out), mode="maxabs")
diag(bm) <- 0
weights <- Matrix::summary(t(bm))[,3]
network <- adj2igraph(Matrix::drop0(getRefit(se.out)),
                   edge.attr=list(weight=weights),
                  vertex.attr = features)
} else if (method=='glasso') {
secor  <- cov2cor(getOptCov(se.out))
bm     <- summary(triu(secor*getRefit(se.out), k=1)) 
network <- adj2igraph(getRefit(se.out),edge.attr=list(weight=bm[,3]),vertex.attr = features)
}else{
    print("Weighted graph only available for mb and glasso method")
    network <- adj2igraph(getRefit(se.out),vertex.attr = features)
}

write_graph(network, out.file, "graphml")
