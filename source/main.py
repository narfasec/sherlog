import getopt, sys

from modules.sherlog_init import Sherlog

def print_banner():
	'''
	'''
	# Banner by https://manytools.org/hacker-tools/ascii-banner/
	print("\n███████╗██╗  ██╗███████╗██████╗ ██╗      ██████╗  ██████╗ ")
	print("██╔════╝██║  ██║██╔════╝██╔══██╗██║     ██╔═══██╗██╔════╝ ")
	print("███████╗███████║█████╗  ██████╔╝██║     ██║   ██║██║  ███╗")
	print("╚════██║██╔══██║██╔══╝  ██╔══██╗██║     ██║   ██║██║   ██║")
	print("███████║██║  ██║███████╗██║  ██║███████╗╚██████╔╝╚██████╔╝")
	print("╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ")
	print("                                              by Octoguard")

def create_output(output):
    '''
    Output function
    '''
def usage():
    print("usage:")
    print("\tpython3 main.py --profile <profile> [options]")

def help():
    print("usage:")
    print("\tpython3 init.py --profile <profile> [options]")
    print("\n\t-p, --profile:	AWS profile: ")
    print("\nOptions:")
    print("\t-j, --json: output has json file, provide filename")
    print("\t-r, --region:	AWS region")
    print("\t-d, --debug:	enable dubug mode")
    exit()

def main():
    # Remove 1st argument from the
    # # list of command line arguments
    arguments_list = sys.argv[1:]
    
    # Options
    options = "hp:r:j:d"
    
    # Long options
    long_options = ["help", "profile=","region=", "json=", "debug"]
    
    # Main arguments
    profile = None
    region = "all-regions"
    output = None
    fmt = ""
    debug = False
    
    try:
        # Parsing argument
        arguments, values = getopt.getopt(arguments_list, options, long_options)
        
        # checking each argument
        if arguments:
            for currentArgument, currentValue in arguments:
                if currentArgument in ("-h", "--help"):
                    help()
                elif currentArgument in ("-p", "--profile"):
                    if currentValue:
                        profile = currentValue
                    else:
                        print('Please provide an AWS profile')
                        exit()
                elif currentArgument in ("-r", "--region"):
                    if currentValue:
                        region = currentValue
                    else:
                        region = "all-regions"
                elif currentArgument in ("-j", "--json"):
                    if currentValue:
                        fmt = "JSON"
                elif currentArgument in ("-d","--debug"):
                    debug = True
                else:
                    sys.exit('Please provide an AWS profile and an output')
        else:
            usage()
            sys.exit('Please provide an AWS profile and an output')
        
        if profile:
            print_banner()
            # print(profile)
            # print(region)
            # print(output)
            # print(str(debug))
            sherlog = Sherlog(debug=debug, profile=profile, format=fmt, output=output)
            sherlog.init()
        else:
            usage()
            sys.exit('Please provide an AWS profile and an output')
    
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
    
    create_output(output)

if __name__ == "__main__":
    main()