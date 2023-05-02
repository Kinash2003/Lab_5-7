#######################################################################################
# This program:
# 1. Asks the user for their access token or to use the hard coded access token
# 2. Provides the information for a list of Webex Teams rooms using the JSON format
#
# The student will:
# 1. Provide the code to prompt the user for their access token else
#    use the hard coded access token
# 2. Enter the Webex Teams room API endpoint (URL)
#######################################################################################

# Libraries
# import requests library
import requests

#import json library
import json

#######################################################################################
#     Ask the user to use either the hard coded token (access token within the code)
#     or for the user to input their access token.
#     Assign the hard coded or user entered access token to the variable accessToken.
#######################################################################################

# Student Step #1
#    Following this comment and using the accessToken variable below, modify the code to
#    ask the user to use either hard-coded or user-entered access token.

choice = input("Do you want to use the hard-coded access token?(y/n)?")
if choice == "y" or choice == "Y":
    accessToken = "MWNlYjVkOTQtMTIzZC00YWFmLTg3YTEtZTJkNDVmYTkwN2FjNjA5YWQ0NjYtMDRh_PE93_f451a09f-5fe6-4b74-a13a-2fde64738081"
    accessToken = "Bearer " + accessToken
elif choice == "n" or choice == "N":
    accessToken = input("Please enter your access token: ")
    accessToken = "Bearer " + accessToken
else:
    print("Error")

#########################################################################################
#  Build request components, URI and header with bearer token 
#########################################################################################

#  Student Step #2
#     Following this comment, modify the code below to use the Webex Teams room API endpoint (URL)
apiUri = "https://api.ciscospark.com/v1/rooms"

##########################################################################################
# Make request and convert response JSON to Python object
##########################################################################################
#make request and store result
resp = requests.get( apiUri, 
                     headers = {"Authorization":accessToken}
                   ) 
# check if the API request executed correctly with the HTTP status code == 200
if not resp.status_code == 200:
    raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(resp.status_code, resp.text))

json_data = resp.json() # convert the JSON response to Python dictionary object

##########################################################################################
# Format and Output response data with string that identifies output
##########################################################################################

print("Webex Teams Response Data:") # Print identifying string
print( json.dumps(json_data, indent = 4) ) #format Python JSON data object and print

#######################################################################################
# End of program
#######################################################################################
