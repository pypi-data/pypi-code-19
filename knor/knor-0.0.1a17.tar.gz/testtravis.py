import yaml

f = open(".travis.yml", "rb")
x = yaml.load(f)
print x

f.close()
