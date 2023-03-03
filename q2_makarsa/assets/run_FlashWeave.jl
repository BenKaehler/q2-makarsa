
using FlashWeave
using ArgParse
using GraphIO


function main()
    # Create ArgParse settings object
    s = ArgParseSettings()

    # Add arguments to settings object
    @add_arg_table s begin
        "--datapath"
            help = "Data Path to input file"
            required = true
        "--metadatapath"
            help = "meta data Path to input file"
        "--output"
            help = "Path to output file"
            default = "output.gml"
        "--minclustersize"
            help = "minimum cluster size (default: 2)"
            arg_type = Int
            default = 2
        "--maxclustersize"
            help = "maximum cluster size (default: 50)"
            arg_type = Int
            default = 50
        "--pcadimension"
            help = "PCA dimension (default: 10)"
            arg_type = Int
            default = 10
        "--nthreads"
            help = "number of threads to use (default: 1)"
            arg_type = Int
            default = 1
            default = 10
        "--seed"
            help = "random seed (default: 1)"
            arg_type = Int
            default = 1
        "--alpha"
            help = "threshold used to determine statistical significance"
            arg_type = Float64
            default =0.05
        "--nruns"
            help = "flashweave parameter"
            arg_type = Int
            default = 10
        "--subsampleratio"
            help = "flashweave parameter"
            arg_type = Float64
            default = 0.8
        "--numclusters"
            help = "flashweave parameter"
            arg_type = Int
            default = 15
         "--maxoverlap"
            help = "flashweave parameter"
            arg_type = Float64
            default = 0.8
        "--verbose"
            help = "Enable verbose output"
            action = :store_true
        
    end

    # Parse command line arguments
     args = parse_args(s)

     # Access the values of the arguments
     input_file = args["datapath"]
     input_meta = args["metadatapath"]
     output = args["output"]
     minclustersize = args["minclustersize"]
     maxclustersize = args["maxclustersize"]
     pcadimension = args["pcadimension"]
     nthreads = args["nthreads"]
     seed = args["seed"]
     alpha = args["alpha"]
     nruns = args["nruns"]
     subsampleratio = args["subsampleratio"]
     numclusters= args["numclusters"]
     maxoverlap= args["maxoverlap"]
     verbose = args["verbose"]


     # Call FlashWeave with parsed arguments
     netw_results = learn_network(input_file, input_meta, sensitive=true, heterogeneous=false)
     save_network(output, netw_results)
end

main()








