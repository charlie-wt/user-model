# description of the machine learning models
### Input data
Per page in each reading of each story, an input datum is a vector (tuple) containing heuristic values for walk distance, number of previous visits, altitude, number of points of interest within 100m and how much the page's title is mentioned by the previous page's title & text, as well as the ranking of the page along each of these heuristics relative to the other pages visible at that point. The target value is either 1 (page was chosen) or 0 (not chosen).

There were 1126 total input vectors taken from 55 total readings accross all stories.

### linreg
Linear regression using L2 regularisation, a gradient descent optimiser and 10-fold cross-validation.

Parameter values:

* Learning rate: 0.01
* Epochs: 100
* Batch size: 1
* Convergence threshold: 0.0001

### logreg
Logistic regression using L2 regularisation, a gradient descent optimiser and 10-fold cross-validation.

There are two output classes, representing

a) the confidence the page should be chosen.
a) the confidence the page should not be chosen.

Parameter values:

* Learning rate: 0.01
* Epochs: 100
* Batch size: 1
* Convergence threshold: 0.0001

### nn
Feedforward neural network using ReLU activation and the Adam optimiser.

Parameter values:

* Learning rate: 0.01
* Epochs: 100
* Batch size: 1
* Convergence threshold: 0.0001
* Number of hidden layers: 1
* Hidden layer size: 5