'''
Pretty Output
'''

class PrettyOutput:
    '''
    Class to allow other modules print colorful messages
    '''
    def __init__(self):
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKCYAN = '\033[96m'
        self.OKGREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'
 
    def success(self, text='Sherlog has found AWS resources that are not logging according to security best practices.'):
        '''
        Print success message
        '''
        print("\n"+self.OKGREEN+text+self.ENDC+"\n")
    
    def print_color(self, text, color=None, header=None):
        '''
        Print desired text with prefered color
        
        Args:
            text   (str): Text to be printed
            colors (str): Color for the printed text (Default is None)
                Colors available:
                    - 'green'
                    - 'blue'
                    - 'yellow'
                    - 'red'
        '''
        if header:
            print('\n'+self.HEADER+self.UNDERLINE+header+self.ENDC)
        if color == 'green':
            print(self.OKGREEN+text+self.ENDC)
        elif color == 'blue':
            print(self.OKBLUE+text+self.ENDC)
        elif color == 'yellow':
            print(self.WARNING+text+self.ENDC)
        elif color == 'red':
            print(self.FAIL+text+self.ENDC)
        else:
            print(text)