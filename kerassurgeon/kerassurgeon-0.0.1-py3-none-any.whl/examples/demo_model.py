from keras.layers import Input, Dense, Concatenate
from keras.models import Model
from keras.utils.vis_utils import plot_model

input_1 = Input(shape=(10,))
input_2 = Input(shape=(10,))
input_3 = Input(shape=(10,))
input_4 = Input(shape=(10,))
dense_1 = Dense(3)
dense_2 = Dense(4)
dense_3 = Dense(5)
dense_4 = Dense(6)

cat_1 = Concatenate()
cat_2 = Concatenate()

a = dense_1(input_1)
b = dense_1(input_2)
c = dense_1(input_3)
d = dense_2(input_4)

# output_1 = dense_3(a)
# output_2 = dense_4(b)
# output_3 = dense_4(c)
# output_4 = cat_1([c, d])

e = dense_3(a)
f = dense_4(b)
g = dense_4(c)
h = cat_1([c, d])

output_1 = cat_2([e, f, g, h])

model = Model(inputs=[input_1, input_2, input_3, input_4],
              outputs=[output_1])

plot_model(model, 'demo_model.png')
