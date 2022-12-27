import getopt
import sys

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
    print("\sherlog main.py --profile <profile> [options]")

def help():
    usage()
    print("\n\t-p, --profile:	AWS profile: ")
    print("\nOptions:")
    print("\t-j, --json: choose json output")
    print("\t-r, --region:	AWS region")
    print("\t-d, --debug:	enable dubug mode")
    exit()

def main():
    # Remove 1st argument from the
    # # list of command line arguments
    arguments_list = sys.argv[1:]
    
    # Options
    options = "hp:r:jd"
    
    # Long options
    long_options = ["help", "profile=","region=", "json", "debug"]
    
    # Main arguments
    profile = None
    has_region = False
    regions = []
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
                        has_region=True
                        regions.append(currentValue)
                elif currentArgument in ("-j", "--json"):
                    output = "json"
                elif currentArgument in ("-d","--debug"):
                    debug = True
                else:
                    sys.exit('Please provide an AWS profile')
        else:
            usage()
            sys.exit('Please provide an AWS profile and an output')
        
        if not has_region:
            regions=str("all-regions")

        if profile:
            if not output:
                print_banner()
            # print(profile)
            # print(regions)
            # print(output)
            # print(str(debug))
            sherlog = Sherlog(debug=debug, profile=profile, format=fmt, output=output, regions=regions)
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