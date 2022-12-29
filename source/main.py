import getopt
import sys

from modules.init import Sherlog

def print_banner():
	'''
    Print Sherlog banner
	'''
	# Banner by https://manytools.org/hacker-tools/ascii-banner/
	print("\n███████╗██╗  ██╗███████╗██████╗ ██╗      ██████╗  ██████╗ ")
	print("██╔════╝██║  ██║██╔════╝██╔══██╗██║     ██╔═══██╗██╔════╝ ")
	print("███████╗███████║█████╗  ██████╔╝██║     ██║   ██║██║  ███╗")
	print("╚════██║██╔══██║██╔══╝  ██╔══██╗██║     ██║   ██║██║   ██║")
	print("███████║██║  ██║███████╗██║  ██║███████╗╚██████╔╝╚██████╔╝")
	print("╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ")
	print("                                              by Octoguard")

def usage():
    '''
    Function to print usage in console
    '''
    print("usage:")
    print("\tsherlog main.py --profile <profile> [options]")

def print_help():
    '''
    Function to run when help argument is called
    '''
    usage()
    print("\n\t-p, --profile: If AWS profile is not given, default profile will be used ")
    print("\nOptions:")
    print("\t-j, --json: choose json output")
    print("\t-r, --region: AWS region (e.g. us-east-1), default will run for all available regions ")
    print("\t-d, --debug:	enable dubug mode")
    exit()

def main():
    '''
    Main function
    '''
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
    debug = False
    
    try:
        # Parsing argument
        arguments, values = getopt.getopt(arguments_list, options, long_options)
        # checking each argument
        if arguments:
            for current_argument, current_value in arguments:
                if current_argument in ("-h", "--help"):
                    print_help()
                elif current_argument in ("-p", "--profile"):
                    if current_value:
                        profile = current_value
                elif current_argument in ("-r", "--region"):
                    if current_value:
                        has_region=True
                        regions.append(current_value)
                elif current_argument in ("-j", "--json"):
                    output = "json"
                elif current_argument in ("-d","--debug"):
                    debug = True
                else:
                    sys.exit('Please provide an AWS profile')
        if not has_region:
            regions=str("all-regions")
        if not profile:
            profile = "default"
        if not output:
            print_banner()
        sherlog = Sherlog(debug=debug, profile=profile, output=output, regions=regions)
        sherlog.init()
    
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

if __name__ == "__main__":
    main()