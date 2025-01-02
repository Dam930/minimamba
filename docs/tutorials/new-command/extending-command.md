# Extend the command
In this section we will extend the `example-command` adding some functionalities to it through the use of components.

Concepts explained here present a recommended way of designing internal projects leveraging the interal config library. **It is not a set of rules that must be strictly followed.** Feel free to take them as advices and contribute to them: the discussion is always appreciated.

## What are components
Components are Python classes that follows the single-responsibility principle. Instead of implementing complex logic inside our commands, we should arrange our code into a set of components used by the commands. Each component has its own, well-defined functionalities and relies on other components for additional ones.

Similarly to commands, they are built starting from config objects. **Their constructor should accept a single, config objec**t: the constructor parameters are moved into the config object. This helps to keep the code clean and separate the code from its configuration, facilitating the configuration of multiple runs (instead of changing parameters in code, you only change or add JSON config files).

## Implementing a component
We want our command to perform the multiplication between two numbers. We implement the multiplication logic in a new component called `ExampleMulCalculator`.

As we saw in [Create a basic command](creating-command.md), we define a new config class for our component in `core/config_models.py` to store the two parameters we require, that is the two numbers we want to multiply together:

```python
from pydantic import StrictFloat


class ExampleMulCalcConfig(BaseObjectConfig):
    num_1: StrictFloat
    num_2: StrictFloat
```
This time the config object inherit from **BaseObjectConfig**. This tells the config library that the class instances will be used as constructor arguments to create Python objects.

Furthermore by defining the fields as StrictFloat the config library (based on pydantic) will perform a type checking on them, raising errors if in the JSON configuration we will try to insert other values than float in this attributes.

Now we can implement our `ExampleMulCalculator` class. Create a new module `example_calculator` and add `calculator.py` to it with the following code:
```python
import logging

from minimamba.core.config_models import ExampleMulCalcConfig
from minimamba.example_calculator.base import ExampleMulCalculator as BaseTool

logger = logging.getLogger(__name__)


class ExampleMulCalculator:
    def __init__(self, config: ExampleMulCalcConfig) -> None:
        self._config = config

    def calculate(self):
        logger.info("Calculating the multiplication")
        logger.info("num_1: %s", self._config.num_1)
        logger.info("num_2: %s", self._config.num_2)

        tot = self._config.num_1 * self._config.num_2
        logger.info("Result: %s", tot)
```

The class simply reads the two numbers from the config object and calculates their product.

## Connecting the component to the command (Configuration)
To use an `ExampleMulCalculator` object inside the `main` function of our command we could manually create an `ExampleMulCalcConfig` object, populate it with the two numbers we want to multiply together, and pass it to the constructor of `ExampleMulCalculator`.

Although this is allowed, it would violate the principle of keeping configurations and code separated. Instead, we should add an `ExampleMulCalculator` field to `ExampleCommandConfig` and arrange the JSON configuration files accordingly inside the `configs` folder.

We could see the config objects and the Python objects as two parallel trees that represents the entities used by our command from two different points of view: the configuration space and the actual execution space. There is a 1 to 1 mapping between config objects and Python objects. Config objects define the initial state and settings of the Python objects and they are defined inside the JSON files before the execution. Then, during the command execution, the config library allow us to create Python objects from their corresponding config objects.

Let us modify `ExampleCommandConfig` in `core/config_model.py`:
```python
class ExampleCommandConfig(BaseCommandConfig):
    calculator: ExampleMulCalcConfig
```
This will tell our application that the ExampleCommand needs an ExampleMulCalculator to work.

Then, we create a JSON config file for our ExampleMulCalcConfig in `configs/example-calculators/calculator.json`:
```json
{
    "$CONFIG_CLASS$": "ExampleMulCalcConfig",
    "$CONFIG_PARAMS$": {
        "$MODULE$": "minimamba.example_calculators.calculator",
        "$CLASS$": "ExampleMulCalculator",
        "num_1": 3.0,
        "num_2": 4.0
    }
}
```
As done for `example-command.json`, we specify in `$CONFIG_CLASS$` which config class we want to instantiate with this JSON file. This time, we also have to fill the `$CONFIG_PARAMS$` object:

- `$MODULE$`: special field that points to the module of the Python class to instantiate
- `$CLASS$`: special field that specify the Python class to instantiate inside the module
- `num_1, num_2`: fields defined in the config class

With the `$MODULE$` and `$CLASS$` we are explicitly declaring the mapping between config object and Python object. We are telling the config library which Python class can be instantiated with this config object.

Then, we have to modify also `example-command.json` by connecting the component:
```json
{
    "$CONFIG_CLASS$": "ExampleCommandConfig",
    "$CONFIG_PARAMS$": {
        "calculator": {
            "$CONFIG_LINK$": "example-calculators.calculator"
        }
    }
}
```
In the `ExampleCommandConfig` we defined `calculator` as a sub-config field (i.e. a field that is a config object in turn). In the JSON we have to populate this field by linking another JSON config, that will instantiate the desired config object for that field. `$CONFIG_LINK$` allows to do this. It uses the same notation as the Python modules, taking the `configs` folder as root.

In this case, we are telling to the config library to populate the `calculator` field with the object defined inside `example-calculators/calculator.json`.

As you might have seen, the structure of the config files in `configs` tries to replicate the one of the Python modules. Although this is not strictly required, it helps to visualize the parallelism between config and Python objects.

Now if you run
```shell
python -m <project_name> --config configs/example-command.json
```
in the `main` function the `config` variable, instance of `ExampleCommandConfig`, will contain the `calculator` field, instance of `ExampleMulCalcConfig`. The config library reads the config file specified in the CLI, resolves all the config links, creates the config objects tree and gives us its root, that is the config object of the command.

## Connecting the component to the command (Python)
