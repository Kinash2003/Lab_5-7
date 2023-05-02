###############################################################
# This program:
# 1. Asks the user to enter an access token or use the hard coded access token
# 2. Lists the users in Webex Teams rooms
# 3. Asks the user which Webex Teams room to monitor for "/location" requests (e.g. /San Jose)
# 4. Periodically monitors the selected Webex Team room for "/location" messages
# 5. Discovers GPS coordinates for the "location" using MapQuest API
# 6. Discovers the date and time of the next ISS flyover over the "location" using the ISS location API
# 7. Sends the results back to the Webex Team room
#
# The student will:
# 1. Enter the Webex Teams room API endpoint (URL)
# 2. Provide the code to prompt the user for their access token else
#    use the hard coded access token
# 3. Provide the MapQuest API Key
# 4. Extracts the longitude from the MapQuest API response using the specific key
# 5. Convers Unix Epoch timestamp to a human readable format
# 6. Enter the Webex Teams messages API endpoint (URL)
###############################################################

#Libraries

import requests
import json
import time

#######################################################################################
#     Ask the user to use either the hard-coded token (access token within the code)
#     or for the user to input their access token.
#     Assign the hard-coded or user-entered access token to the variable accessToken.
#######################################################################################

# Student Step #2
#    Following this comment and using the accessToken variable below, modify the code to
#    ask the user to use either hard-coded or user entered access token.

choice = input("Do you want to use the hard-coded access token?(y/n)?")
if choice == "y" or choice == "Y":
    accessToken = "OTY3ODk4ZmQtNzkzZC00ZGU2LTllMTAtOTYxYWM2OGEzOGIxMTZiMjk1ODItOTlh_PE93_f451a09f-5fe6-4b74-a13a-2fde64738081"
    accessToken = "Bearer " + accessToken
elif choice == "n" or choice == "N":
    accessToken = input("Please enter your access token: ")
    accessToken = "Bearer " + accessToken
else:
    print("Error")

#######################################################################################
#     Using the requests library, create a new HTTP GET Request against the Webex Teams API Endpoint for Webex Teams Rooms:
#     the local object "r" will hold the returned data.
#######################################################################################
#  Student Step #3
#     Modify the code below to use the Webex Teams room API endpoint (URL)

r = requests.get("https://api.ciscospark.com/v1/rooms",
                 headers={"Authorization": accessToken}
                 )
#######################################################################################
# Check if the response from the API call was OK (r. code 200)
#######################################################################################
if not r.status_code == 200:
    raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))

#######################################################################################
# Displays a list of rooms.
#
# If you want to see additional key/value pairs such as roomID:
#	print ("Room name: '" + room["title"] + "' room ID: " + room["id"])
#######################################################################################

print("List of rooms:")
rooms = r.json()["items"]
for room in rooms:
    print("Type: " + room["type"] + ", Name: " + room["title"])

#######################################################################################
# Searches for name of the room and displays the room
#######################################################################################

while True:
    # Input the name of the room to be searched
    roomNameToSearch = input("Which room should be monitored for /location messages? ")

    # Defines a variable that will hold the roomId
    roomIdToGetMessages = None

    for room in rooms:
        # Searches for the room "title" using the variable roomNameToSearch
        if (room["title"].find(roomNameToSearch) != -1):
            # Displays the rooms found using the variable roomNameToSearch (additional options included)
            print("Found rooms with the word " + roomNameToSearch)
            print(room["title"])

            # Stores room id and room title into variables
            roomIdToGetMessages = room["id"]
            roomTitleToGetMessages = room["title"]
            print("Found room : " + roomTitleToGetMessages)
            break

    if (roomIdToGetMessages == None):
        print("Sorry, I didn't find any room with " + roomNameToSearch + " in it.")
        print("Please try again...")
    else:
        break

# run the "bot" loop until manually stopped or an exception occurred
while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    GetParameters = {
        "roomId": roomIdToGetMessages,
        "max": 1
    }
    # run the call against the messages endpoint of the Webex Teams API using the HTTP GET method
    r = requests.get("https://api.ciscospark.com/v1/messages",
                     params=GetParameters,
                     headers={"Authorization": accessToken}
                     )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))

    # get the JSON formatted returned data
    json_data = r.json()
    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]
    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)

    # check if the text of the message starts with the magic character "/iss_now" followed by a location name
    if message.find("/iss_now") == 0:
        # name of a location (city) where we check for GPS coordinates using the MapQuest APIs
        #  message[1:]  returns all letters of the message variable except the first "/" character
        location = message[1:]

        #  Student Step #4
        #     Add the MapQuest API key (from Chapter 1)
        # the MapQuest API GET parameters
        #  "address" is the the location to lookup
        #  "key" is the secret API KEY you generated at https://developer.mapquest.com/user/me/apps
        mapsAPIGetParameters = {
            "location": location,
            "key": "JLYrqViOyPG3pmPeywQo5j5OXaFqMNPO"  # MapQuest API key here
        }

        # Get location information using the MapQuest API geocode service using the HTTP GET method
        r = requests.get("https://www.mapquestapi.com/geocoding/v1/address?",
                         params=mapsAPIGetParameters
                         )

        # Verify if the returned JSON data from the MapQuest API service are OK
        json_data = r.json()
        # check if the status key in the returned JSON data is "0"
        if not json_data["info"]["statuscode"] == 0:
            raise Exception("Incorrect reply from MapQuest API. Status code: {}".format(r.statuscode))

        # store the location received from the MapQuest API in a variable
        locationResults = json_data["results"][0]["providedLocation"]["location"]
        # print the location address
        print("Location: " + locationResults)

        #  Student Step #5
        #     Set the longitude key as retuned by the MapQuest API
        # store the GPS latitude and longitude of the location as received from the MapQuest API in variables
        locationLat = json_data["results"][0]["locations"][0]["displayLatLng"]["lat"]
        locationLng = json_data["results"][0]["locations"][0]["displayLatLng"]["lng"]
        # print the location address
        print("Location GPS coordinates: " + str(locationLat) + ", " + str(locationLng))

        # documentation of the ISS flyover API: http://open-notify-api.readthedocs.io/en/latest/iss_pass.html
        # the ISS flyover API GET parameters
        #  "lat" is the Latitude of the location
        #  "lon" is the longitude of the location
        issAPIGetParameters = {
            "lat": locationLat,
            "lon": locationLng
        }
        # Get IIS flyover information over the specified GPS coordinates using the HTTP GET method
        r = requests.get("http://api.open-notify.org/iss-now.json",
                         params=issAPIGetParameters
                         )
        # get the json formatted retuned data
        json_data = r.json()
        # Verify if the returned JSON data from the API service are OK and contains the "iss_position" key
        if not "iss_position" in json_data:
            raise Exception("Incorrect reply from open-notify.org API. Status code: {}. Text: {}".format(r.status_code, r.text))

        timestampInEpochSeconds = json_data["timestamp"]


        #  Student Step #6
        #     Use the time.????? function to convert the timestamp in Epoch timestamp to human readable time
        timestampInFormattedString = str((time.ctime(timestampInEpochSeconds)))

        forecastAPIGetParameters = {
            "lat": locationLat,
            "lon": locationLng,
            "units": "metric",
            "appid": "241c330117661206cb73d2041388145a"
        }
        r_forecast = requests.get("https://api.openweathermap.org/data/2.5/weather",
                                  params=forecastAPIGetParameters)
        json_data = r_forecast.json()
        if "weather" not in json_data:
            raise Exception("Incorrect reply from open-notify.org API. Status code: {}.""Text: {}".format(r_forecast.status_code, r_forecast.text))


        weather_description = json_data["weather"][0]["description"]
        if "main" not in json_data:
            raise Exception("Incorrect reply from open-notify.org API. Status code: {}.""Text: {}".format(r_forecast.status_code, r_forecast.text))

        temperature = json_data["main"]["temp"]

        mapsAPIGetParameters = {
            "lat": locationLat,
            "lng": locationLng,
            "key": "JLYrqViOyPG3pmPeywQo5j5OXaFqMNPO"
        }
        r_map = requests.get("https://www.mapquestapi.com/geocoding/v1/reverse",
                             params=mapsAPIGetParameters)
        json_data = r_map.json()
        if not json_data["info"]["statuscode"] == 0:
            raise Exception("Incorrect reply from MapQuest API. Status code:{}".format(r_map.status_code))


        locationResults_city = json_data["results"][0]["locations"][0]["adminArea5"]
        locationResults_county = json_data["results"][0]["locations"][0]["adminArea4"]
        locationResults_country = json_data["results"][0]["locations"][0]["adminArea1"]

        # assemble the response message
        responseMessage = ""
        if locationResults_country == "":
            responseMessage = "Now ISS fly over the ocean"
        else:
            responseMessage = "The ISS now: {}, {}, {}, {}.\n" \
                              "Forecast: {}, {} Celsius".format(locationResults_city,
                                                                locationResults_county,
                                                                locationResults_country,
                                                                timestampInFormattedString,
                                                                weather_description,
                                                              temperature)
        # print the response message
        print("Sending to Webex Teams: " + responseMessage)

        # the Webex Teams HTTP headers, including the Content-Type header for the POST JSON data
        HTTPHeaders = {
            "Authorization": accessToken,
            "Content-Type": "application/json"
        }

        # the Webex Teams POST JSON data
        #  "roomId" is is ID of the selected room
        #  "text": is the responseMessage assembled above
        PostData = {
            "roomId": roomIdToGetMessages,
            "text": responseMessage
        }
        # run the call against the messages endpoint of the Webex Teams API using the HTTP POST method
        #  Student Step #7
        #     Modify the code below to use the Webex Teams messages API endpoint (URL)
        r = requests.post("https://api.ciscospark.com/v1/messages",
                          data=json.dumps(PostData),
                          headers=HTTPHeaders
                          )
        if not r.status_code == 200:
            raise Exception(
                "Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))

















