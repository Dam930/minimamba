# Setup a new project

This tutorial assumes that you have Anaconda or Miniconda installed on your development system and a default Python interpreter available.

## Initialization

To create a new project starting from the Artificialy's Python Template you have two options:

- [Manual way](#manual-way)
- [Starting from the GitLab template](#from-the-gitlab-template) [**NOT RECOMMENDED**]

### Manual way

Create an empty GitLab repository for the new project. Make sure that the `Create a README file` option is deselected in the creation procedure: the repo must not contain any file.

On your development machine clone the template repo by running:

```bash
git clone git@gitlab.com:artificialy1/artificialy-internal-projects/artificialy-template/minimamba.git <new-project-name>
```

Inside the root folder of the cloned project run:

```bash
make init
```

The auto-setup procedure will start, asking some information about the project. Optional fields can be skipped by leaving them blank: in that case default values will be taken (the ones between square brackets).

The procedure will also create for you a conda environment, if requested. The template code currently support Python 3.9, 3.10 and 3.11.

Finally, the template will ask you to link the folder to a remote repository. Copy and paste the link to the empty GitLab repo you created before. The link procedure will delete the local git history to start from a clean git repository.  
If you skip this passage, you will have to manually manage the remote repo and the local history (that will contain commits and branches from the template project).

### From the GitLab template

**The initialization from the GitLab template is currenly not recommended**.

The GitLab template creates a fork of the Python template repo, cloning commits, branches and issues. For this reason, it does not fit with the initialization procedure and you will have to manually take care of all these problems.

This tutorial will be updated once this option will be contemplated by the initialization procedure.

The following steps will guide you through the creation of a new project repository from the GitLab template:

- When creating a new GitLab project select the option `Create from template`
- Navigate to the Group tab and choose `minimamba`
- Insert the requested project information and create the project

Once the GitLab project has been created, clone it on your development machine:

```bash
git clone <project-url>
```

Inside the root folder of the project run:

```bash
make init
```

Follow the auto-setup procedure as described in [Manual way](#manual-way) until you will be asked to setup a remote repository. Skip that part to preserve the git history and remote.

## Finalization

The project has been initialized, but our development environment needs some final configuration.

Activate the virtual environment that you created for the project:

```bash
conda activate <env-name>
```

And run:

```bash
make dev
```

This will install the base dependencies required for managing the project during the development. It will also configure pre-commit.
