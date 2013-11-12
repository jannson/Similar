import os
from pybrain.datasets import ClassificationDataSet
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised import BackpropTrainer
from pybrain.structure.modules import SoftmaxLayer

classes = ['apple', 'orange', 'peach', 'banana']*10
input = ['ap','or','pea','bana']

data = ClassificationDataSet(len(input), 1, nb_classes=len(classes), class_labels=classes)

data._convertToOneOfMany( )                 # recommended by PyBrain

fnn = buildNetwork( data.indim, 5, data.outdim, outclass=SoftmaxLayer ) 

trainer = BackpropTrainer( fnn, dataset=data, momentum=0.99, verbose=True, weightdecay=0.01)

trainer.trainUntilConvergence(maxEpochs=80)

# stop training and start using my trained network here

output = fnn.activate(input)

class_index = max(xrange(len(output)), key=output.__getitem__)
class_name = classes[class_index]
print class_name
