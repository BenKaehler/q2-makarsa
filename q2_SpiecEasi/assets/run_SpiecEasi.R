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
 make_option(c("-c","--ncores"), action="store", default=1, type='numeric',
            help="pulsar.params"),
 make_option(c("-t","--thresh"), action="store", default=0.05, type='numeric',
            help="Threshold for StARS criterion"),   
 make_option(c("-b","--subsample.ratio"), action="store", default=0.8, type='numeric',
            help="Subsample size for StARS"),  
 make_option(c("-s","--seed"), action="store", default='NULL', type='numeric',
            help="Set the random seed for subsample set"),  
 make_option("--wkdir", action="store_true", default='NULL', type='character',
            help=" Current working directory for process running jobs"),   
 make_option("--regdir", action="store", default='NULL', type='character',
            help=" Directory for storing the registry files"),   
 make_option("--init", action="store", default='init', type='character',
            help=" String for differentiating the init registry for batch mode pulsar"),
 make_option("--conffile", action="store", default='NULL', type='character',
            help="Path to config file or string that identifies a default config file"),   
    
 make_option("--job.res", action="store", default=list(), type='numeric',
            help=" Named list to specify job resources for an hpc"),   
 make_option("--cleanup", action="store", default=FALSE, 
            help=" Remove registry files, either TRUE or FALSE"),    
    
 make_option("--sel.criterion", action="store", default='stars', type='character', 
            help=" Specifying criterion/method for model selection, Accepts 'stars' [default], 'bstars' (Bounded StARS)"),     
 make_option(c("-v", "--verbose"), action="store_true", default=TRUE, 
        help="Print extra output [default]"),
 make_option("--pulsar.select", action="store", default=TRUE, type='character', 
            help="Perform model selection. Choices are TRUE/FALSE/'batch'  "),
 make_option("--lambda.log", action="store", default=TRUE, type='character', 
            help="lambda.log should values of lambda be distributed logarithmically (TRUE) or linearly (FALSE) between lamba.min and lambda.max ")
    
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
    
thresh<-opt$thresh
subsample.ratio<-opt$subsample.ratio
seed<-opt$seed
wkdir=opt$wkdir=getwd()
regdir<-opt$regdir
init<-opt$init
conffile<-opt$conffile
job.res<-opt$job.res
cleanup<-opt$cleanup
sel.criterion<-opt$sel.criterion
verbose<-opt$verbose
pulsar.select<-opt$pulsar.select
lambda.log<-opt$lambda.log



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

#Printing current working directory
cat("Current working directory:\n",wkdir,"\n")

data = t(data)
se.out = spiec.easi(data, method=method, lambda.min.ratio=lambda.min.ratio,
                    nlambda=nlambda, pulsar.params=list(rep.num=rep.num))

network = adj2igraph(getRefit(se.out))
V(network)$name = colnames(data)
write_graph(network, out.file, "graphml") 
