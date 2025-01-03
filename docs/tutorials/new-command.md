# Implementing a new command

In this tutorial we will go through the steps to implement a new command and the related components.

The tutorial is composed of the following parts:

- [Create a basic command](new-command/creating-command.md)
- Extending the command (Coming soon)

The whole code is already included in the Python Template.

## Why do I need a command?

Commands define the functionalities of your application (e.g. training a model, making inference, running a REST API).

A common-yet-bad practice is defining a Python file for each functionality of the application, that will be used as the entry point of the execution. However, having multiple files, located in different parts of the project and with different startup operations leads to a messy project that is difficult to navigate and run for developers new to that project.

Instead, the command system standardizes the project structure and fosters the organization. It does this by forcing to have a single entry point for the application (the `__main__.py` file): specific functionalities have to be implemented in the command files located in the `commands` module. Each of those corresponds to a different command, and can be seen as virtual entry points for the application. Furthermore, the command system automatically takes care of and standardize common setup operations (e.g. setting up the logger, a serialization dir, handling the configurations, etc.).

## Note

The tutorial is a good chance to present a set of **guidelines and best practices** that should be followed during the project development. They do not pretend to be the best options, but they will help to keep projects as clean as possible and they will uniform the project here in Artificialy, helping the collaboration between different teams and people.

As we will see, implementing a command involves using configuration files and the internal `configmanager` configuration library.

If you have suggestions or improvements, please open an issue on GitLab.
