from model_gen import Layer, ModelGen


layer_list = []
layer_list.append(Layer(name='Dense1', activation_function='relu', node_num=200, dropout=False))
layer_list.append(Layer(name='Dense2', activation_function='relu', node_num=100, dropout=False))
layer_list.append(Layer(name='Dense3', activation_function='relu', node_num=50, dropout=False))
layer_list.append(Layer(name='Dense4', activation_function='relu', node_num=50, dropout=False))


input_list = []
for i in range(63):
    input_list.append('X%d' % (i+1))
output_list = ['Y1']


model = ModelGen(batch_size=128,
                train_num=13000,
                val_num=1000,
                test_num=1000,
                input_list=input_list,
                output_list=output_list,
                data_filename='data/posco_init_data.csv',
                epoch=20,
                layer_list=layer_list,
                optimizer='adam',
                learning_rate=0.002,
                beta1=0.9,
                beta2=0.99)

model.run()

