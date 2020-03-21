## the main test 
import sys
import platform

## In next line .. why 1? 
sys.path.insert(1, 'lib/' + platform.system())
## because 0 is the current directory

from imageModel import ImageModel
from modesEnum import Modes

from task3Test import Task3Test

# Assign vaild paths to the following 2 variables
image1Path : str = ""
image2Path : str = ""

# this format --> 'variable : variableType' is called annotation
# as you have noticed, python is not a static typed language, so many errors can happen by passing a different type than the expected one to a function
# type annotations can help you not to do this terrible mistake

test = Task3Test(image1Path, image2Path, ImageModel)
test.testMagAndPhaseMode(0.7, 0.3)
test.testRealAndImagMode(0.7, 0.3)