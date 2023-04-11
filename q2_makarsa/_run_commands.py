import subprocess


def run_commands(cmds, verbose=True):  # EEE need to credit the authors of this
    if verbose:
        print(
            "Running external command line application(s). This may print "
            "messages to stdout and/or stderr."
        )
        print(
            "The command(s) being run are below. These commands cannot "
            "be manually re-run as they will depend on temporary files that "
            "no longer exist."
        )
    for cmd in cmds:
        if verbose:
            print("\nCommand:", end=" ")
            print(" ".join(cmd), end="\n\n")
        subprocess.run(cmd, check=True)
