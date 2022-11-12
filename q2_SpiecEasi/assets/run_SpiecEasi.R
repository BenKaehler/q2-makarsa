#!/usr/bin/env Rscript




library("optparse")
library('Matrix')

errQuit <- function(mesg, status=1) { message("Error: ", mesg); q(status=status) }

option_list = list(
 make_option(c("-i","--input_file"), action="store", default='NULL', type='character',
            help="File path to directory with the .tsv files to be processed"),
  
 make_option(c("-o","--output_file"), action="store", default='NULL', type='character',
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
inp.file <- opt$input_file
out.file <- opt$output_file

method<-opt$method

lambda.min.ratio <- if(opt$lambda.min.ratio=='NULL') NULL else as.numeric(opt$lambda.min.ratio)  
    
nlambda <- if(opt$nlambda=='NULL') NULL else as.integer(opt$nlambda)
    
rep.num <- if(opt$rep.num=='NULL') NULL else as.integer(opt$rep.num) 
    
ncores <- if(opt$ncores=='NULL') NULL else as.integer(opt$ncores)




### VALIDATE ARGUMENTS ###
# Input is expected a .tsv file

if(dir.exists(inp.file)) {
  errQuit("Input is a directory.")
} else {
  data = read.table(inp.file,sep = '\t', header=T, row.names=1)
  
}


# Output files are to be filenames (not directories) and are to be
# removed and replaced if already present.

 if(dir.exists(out.file)) {
   errQuit("Output filename ", out.file, " is a directory.")
  } else if(file.exists(out.file)) {
   invisible(file.remove(out.file))
  }




 ### LOAD LIBRARIES ###

suppressWarnings(library(SpiecEasi))
suppressWarnings(library(igraph))


data = t(data)
se.out = spiec.easi(data, method=method, lambda.min.ratio=lambda.min.ratio,
                    nlambda=nlambda, pulsar.params=list(rep.num=rep.num))

network = adj2igraph(getRefit(se.out))
V(network)$name = colnames(data)
write_graph(network, out.file, "graphml") 
