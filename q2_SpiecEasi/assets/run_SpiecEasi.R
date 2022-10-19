#!/usr/bin/env Rscript

#install.packages("Matrix")
#install.packages("Rcpp")
#args <- commandArgs(trailingOnly = TRUE)


library("optparse")
library(dplyr)
library('Matrix')

#cat(R.version$version.string, "\n")
errQuit <- function(mesg, status=1) { message("Error: ", mesg); q(status=status) }

option_list = list(
 make_option(c("-i","--input_directory"), action="store", default='NULL', type='character',
            help="File path to directory with the .tsv files to be processed"),
  
 make_option(c("-o","--output_path"), action="store", default='NULL', type='character',
             help="File path to output file. If already exists, will be overwritten"),
 
 make_option(c("-m","--method"), action="store", default='NULL', type='character',
            help="method that will pass into spieceasi, available options mb, glasso"),
 
 make_option(c("-l","--lambda.min.ratio"), action="store", default='NULL', type='character',
            help="the scaling factor that determines the minimum sparsity/lambda parameter"),
 
 make_option(c("-d","--nlambda"), action="store", default='NULL', type='character',
            help="nlambda"),
 make_option(c("-r","--rep.num"), action="store", default='NULL', type='character',
            help="pulsar.params"), 
    
 make_option(c("-c","--ncores"), action="store", default='NULL', type='character',
            help="pulsar.params")  
    
   )
 
opt = parse_args(OptionParser(option_list=option_list))


# assign each of the arguments, in positional order, to an appropriately named R variable
inp.dir <- opt$input_directory
out.path <- opt$output_path

method<-opt$method

lambda.min.ratio <- if(opt$lambda.min.ratio=='NULL') NULL else as.numeric(opt$lambda.min.ratio)  
    
nlambda <- if(opt$nlambda=='NULL') NULL else as.integer(opt$nlambda)
    
rep.num <- if(opt$rep.num=='NULL') NULL else as.integer(opt$rep.num) 
    
ncores <- if(opt$ncores=='NULL') NULL else as.integer(opt$ncores)




### VALIDATE ARGUMENTS ###
# Input directory is expected to contain .tsv file(s)

if(!dir.exists(inp.dir)) {
  errQuit("Input directory does not exist....")
} else {
  unfilts <- list.files(inp.dir, pattern=".tsv", full.names=TRUE)
  if(length(unfilts) == 0) {
   errQuit("No input files with the expected filename format found.")
  }

}


# Output files are to be filenames (not directories) and are to be
# removed and replaced if already present.
for(fn in out.path) {
 if(dir.exists(fn)) {
   errQuit("Output filename ", fn, " is a directory.")
  } else if(file.exists(fn)) {
   invisible(file.remove(fn))
  }
}







 ### LOAD LIBRARIES ###
library(scales)
suppressWarnings(library(methods))
suppressWarnings(library(igraph))
suppressWarnings(library(SpiecEasi))
cat("SpiecEasi:", as.character(packageVersion("SpiecEasi")), "/",
    "Rcpp:", as.character(packageVersion("Rcpp")), "/",
    "RcppParallel:", as.character(packageVersion("RcppParallel")), "\n")  

#plant.surf.c = read.table('~/PhD/data/data-12-5-22/early-vaginal-and-cesarean-filtered/early-cesarean-filtered.tsv',
                      #  sep = '\t', header=T, row.names=1)

#plant.surf.c = read.table(args[1],sep = '\t', header=T, row.names=1)

plant.surf.c=list.files(inp.dir, pattern=".tsv", full.names=TRUE)
plant.surf.c = read.table(plant.surf.c,sep = '\t', header=T, row.names=1)

plant.surf.c = t(plant.surf.c)
se.mb.ps.c = spiec.easi(plant.surf.c, method=method, lambda.min.ratio=lambda.min.ratio,
                    nlambda=nlambda, pulsar.params=list(rep.num=rep.num))
#se.mb.ps.c=se.mb.ps.c

#ig.mb.c = adj2igraph(getRefit(se.mb.ps.c),vertex.attr=list(name=colnames(plant.surf.c)))
ig.mb.c = getRefit(se.mb.ps.c)
writeMM(ig.mb.c,file='test.mtx')