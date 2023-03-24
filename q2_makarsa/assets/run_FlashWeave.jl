#!/usr/bin/env julia

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
        "--heterogeneous"
            help = "enable heterogeneous mode for multi-habitat or -protocol data with at least thousands of samples                               (FlashWeaveHE), default = false"
            action = :store_true
        "--sensitive"
            help = "enable fine-grained associations (FlashWeave-S, FlashWeaveHE-S), sensitive=false results in the fast modes                     FlashWeave-F or FlashWeaveHE-F,default = false "
            action = :store_true
        "--max_k"
            help = "maximum size of conditioning sets, high values can strongly increase runtime. max_k=0 results in no                             conditioning (univariate mode)"
            arg_type = Int
            default = 2
        "--alpha"
            help = "threshold used to determine statistical significance"
            arg_type = Float64
            default =0.05
        "--conv"
            help = "convergence threshold, i.e. if conv=0.01 assume convergence if the number of edges increased by only 1%                         after 100% more runtime (checked in intervals)"
            arg_type = Float64
            default =0.01
        "--feed_forward"
            help = "enable feed-forward heuristic,default = true "
            action = :store_true
        "--max_tests"
            help = "maximum number of conditional tests that should be performed on a variable pair before association is                            assumed"
            arg_type = Int
            default = 20
        "--hps"
            help = "reliability criterion for statistical tests when sensitive=false"
            arg_type = Float64
            default =1.0
        "--FDR"
            help = "perform False Discovery Rate correction (Benjamini-Hochberg method) on pairwise associations,                                   default =    false "
            action = :store_true 
        "--n_obs_min"
            help = "don't compute associations between variables having less reliable samples (i.e. non-zero if                                      heterogeneous=true) than this number. -1: automatically choose a threshold"
            arg_type = Int
            default = -1
         "--time_limit"
            help = "if feed-forward heuristic is active, determines the interval (seconds) at which neighborhood information is                     updated"
            arg_type = Int
            default = 60
        "--normalize"
            help = "automatically choose and perform data normalization (based on sensitive and heterogeneous), default = true"
            action = :store_true
        "--track_rejections"
            help = "store for each discarded edge, which variable set lead to its exclusion (can be memory intense for large                       networks), default = false"
            action = :store_true
        "--verbose"
            help = "print progress information, default = true "
            action = :store_true
        "--transposed"
            help = "if true, rows of data are variables and columns are samples, default = false"
            action = :store_true
        "--prec"
            help = "precision in bits to use for calculations (16, 32, 64 or 128)"
            arg_type = Int
            default = 64
        "--make_sparse"
            help = "use a sparse data representation (should be left at true in almost all cases),default = true "
            action = :store_true 
        "--update_interval"
            help = "if verbose=true, determines the interval (seconds) at which network stat updates are printed"
            arg_type = Int
            default = 10
    end

    # Parse command line arguments
     args = parse_args(s)

     # Access the values of the arguments
     input_file = args["datapath"]
     input_meta = args["metadatapath"]
     output = args["output"]
     heterogeneous = args["heterogeneous"]
     sensitive = args["sensitive"]
     max_k = args["max_k"]
     alpha = args["alpha"]
     conv = args["conv"]
     feed_forward = args["feed_forward"]
     max_tests = args["max_tests"]
     hps = args["hps"]
     FDR= args["FDR"]
     n_obs_min= args["n_obs_min"]
     time_limit = args["time_limit"]
     normalize = args["normalize"]
     track_rejections = args["track_rejections"]
     verbose = args["verbose"]
     transposed = args["transposed"]
     prec = args["prec"]
     make_sparse = args["make_sparse"]
     update_interval = args["update_interval"]

     # Call FlashWeave with parsed arguments
     netw_results = learn_network(input_file, input_meta, sensitive=true, heterogeneous=false)
     save_network(output, netw_results)
end

main()
