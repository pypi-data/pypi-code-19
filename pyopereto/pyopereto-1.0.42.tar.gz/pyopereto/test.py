from client import OperetoClient
a = OperetoClient(opereto_host='https://54.235.124.172', opereto_user='admin', opereto_password='admin123')


print a.get_product('26ab6915a4a33a4e01275edfbc171b06')


#a.create_product('test', 'version', 123)


#a.delete_product('8e9e7dc9522176982ab41dd2ef591f91')



