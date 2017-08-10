import zomatopy

config = {
    "user_key" : "a9d25d472f80e72394ab4e6b8081455a"
}

zomato = zomatopy.initialize_app(config)
cityID = zomato.restaurant_search(query="french", cuisines="1, 2, 3")
print(cityID)
