import weka.core.jvm as jvm
from weka.classifiers import Classifier
import weka.core.classes

jvm.start(system_cp=True)

clsname = ".J48"
print(clsname)
cls = Classifier(classname=".J48")
print(cls.to_commandline())

weka.core.classes.complete_classname(".Discretize")

jvm.stop()
