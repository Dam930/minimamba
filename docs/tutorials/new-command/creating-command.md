# Create a basic command

In this first part, we will implement a new command `print-message` that simply print a string through the logger.

Table of contents:

- [Dive into the implementation](#dive-into-the-implementation)
- [Run the command](#run-the-command)
- [Code explanation](#code-explanation)
- [Docstring and help](#docstring-and-help)

## Dive into the implementation

To add a new command to our project we have to:

- Create `<project_name>/commands/print_message.py`, containing the command code
- Add `PrintMessageCommandConfig` to `<project_name>/commands/print_message.py`, that defines the configuration for the command (which input parameters can accept)
- Create `configs/print-message-command.json`, that contains the actual configuration for the command execution (the value to use as input parameters)

Below there is the complete code for all of them. An in-depth explanation it is given in the [Code explanation](#code-explanation) section.

`<project_name>/commands/print_message.py`

```python
import logging

logger = logging.getLogger(__name__)

def main(config: PrintMessageCommandConfig):
    logger.info("Running %s", __name__)
    logger.info(config.message)
    logger.info("Done")
```

---

`<project_name>/commands/print_message.py`

```python
from artificonfig.core.models import BaseCommandConfig
from pydantic import StrictStr

...

class PrintMessageConfig(BaseCommandConfig):
    message: StrictStr
```

---

`configs/print-message-command.json`

```json
{
    "@COMMAND_CONFIG": {
        "__config_class": "<project_name>.configs.models.PrintMessageCommandConfig",
        "__config_params": {
            "message": "Hello!"
        }
    }
}
```

## Run the command

The execute the new implemented command, open a terminal inside your project folder and run:

```shell
python -m <project_name> print-message --config configs/print-message-command.json
```

Since we installed our project in the conda environment during the setup phase, we can also use the shortcut:

```shell
<project-name> print-message --config configs/print-message-command.json
```

> **NOTE:** Here the underscores in the project name are replaced with hyphens (that is the name of our project installed in the virtual environment)

With both modalities, you should see as output:

```shell
INFO - minimamba.commands.print_message - Running <project_name>.commands.print_message
INFO - minimamba.commands.print_message - Hello!
INFO - minimamba.commands.print_message - Done
```

## Code explanation

To create a new command we have to add a Python file to the `commands` module. The project will automatically scan files in that module and register them as commands available through the CLI. The command name is inferred from the the file name, so we will call the new file `print_message.py` (underscores are replaced by hyphens).

Let us add the following code to `print_message.py`:

```python
import logging

logger = logging.getLogger(__name__)


def main():
    logger.info("Running %s", __name__)
    logger.info("Done")
```

Each command file requires the definition of a `main` function: it will contain the code that will be executed when the command is launched. In this case, we use the logger (already set up by the template framework) to log the command name and exit.

The command as it is cannot be executed yet. Indeed, we need a way to specify the message we want to print, and **every command requires a configuration object to be passed to its main function**.

Configuration objects for commands replace the command line arguments: the CLI is not customizable, and if we want to configure the command execution we have to create and modify a configuration object for it.

> **NOTE:** The only configuration library currently supported is the internal `artificonfig`.

`configs/models.py` is the default file where configuration classes are defined. Here we add the configuration class for our `print-message`:

```python
from artificonfig.core.models import BaseCommandConfig
from pydantic import StrictStr

class PrintMessageConfig(BaseCommandConfig):
    message: StrictStr
```

**Every command configuration class must inherit from BaseCommandConfig, provided by `artificonfig`**.  
Our config class contains the string to be printed by the command. By defining the config fields through Pydantic types we enable the type validation features.

Now we have to modify the `main` function in `commands/print_message.py` to accept and use the new config object:

```python
import logging

logger = logging.getLogger(__name__)

def main(config: PrintMessageCommandConfig):
    logger.info("Running %s", __name__)
    logger.info(config.message)
    logger.info("Done")
```

So far we have defined the config class for our command and connected it to our command code, but how we actually manage an instance of the command configuration? How can we specify the message to be printed?

The `configs` folder in the project root stores the configuration JSON files. Each file is an instance of a configuration class defined in `configs/models.py`.  
Inside this folder we create a new file `print-message-command.json`:

```json
{
    "@COMMAND_CONFIG": {
        "__config_class": "<project_name>.configs.models.PrintMessageCommandConfig",
        "__config_params": {
            "message": "Hello!"
        }
    }
}
```

The `@COMMAND_CONFIG` root field indicates which type of configuration we are creating (in this case, a configuration for a command).

> **NOTE:** Other possible values for the root field are `@SIMPLE_CONFIG` for simple configuration containers or `@OBJECT_CONFIG` for configurable Python objects. However, they are only required for more advanced configuration structures.

The `__config_class` field is a special field indicating to the config library which config class to instantiate (PrintMessageCommandConfig in our example).

Finally, `__config_params` is a JSON object specifying the attributes values for the config instance, i.e. the parameters passed to the constructor of the config class. In our case, we have to specify a value for the string field `message` of PrintMessageCommandConfig.

## Docstring and help

The template provide a default `help` command for the project. It provides the list of available commands in this project with a brief description for each of them. This description is taken from the docstring of the `main` function of that command.

Let us add a docstring to our command to enrich the `help` of our application:

```python
def main(config: PrintMessageCommandConfig):
    """Print a message on the console.

    It allows the user to specify a message that will be printed
    on the console.

    Args:
        config (PrintMessageCommandConfig): config object for the command
    """
    logger.info("Running %s", __name__)
    logger.info(config.message)
    logger.info("Done")
```

The docstring must follow the Google convention. The template will take the first row until the full stop as the command description.

Now by running the help command:

```shell
python -m <project_name> -h
```

You will get:

```shell
<project_name>
Artificialy SA - https://www.artificialy.ch/

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -g GLOBAL_CONFIG, --global-config GLOBAL_CONFIG
                        Path to global config file.

Commands:
  {print-message}
    print-message     Print a message on the console.
```
