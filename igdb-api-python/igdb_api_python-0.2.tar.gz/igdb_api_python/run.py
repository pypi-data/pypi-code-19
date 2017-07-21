from igdb import igdb

# ENTER YOUR API KEY HERE
igdb = igdb("YOUR_API_KEY")

#RESULT OF 1 GAME
result = igdb.games(1942,fields="name")
for game in result:
    print("Retrieved: " + game["name"])

#RESULT OF LATEST  NEWS ARTICLES WITH SOME ORDERING
result = igdb.pulses(params="&limit=5&order=created_at:desc&offset=")
#print(result)
for game in result:
    print("Retrieved: " + game["title"])

#ALL PULSE ARTICLES
result = igdb.pulses()
for game in result:
    print("Retrieved: " + game["title"])

#GET A SPECIFIC ARTICLE
result = igdb.pulses(78992)
for game in result:
    print("Retrieved: " + game["title"])
