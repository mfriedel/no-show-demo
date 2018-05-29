# No-Show Predictor
A sample Skafos project that trains a classifier to predict the likelihood of patients showing up to scheduled appointments in the coming week. All data was acquired from this Kaggle competition.

## Project Contents
- `requirements.txt` contains basic python dependencies.
- `metis.config.yml` contains user-defined configurations for how the deployment should run.
- `helpers/*.` contains helper code and functions to better organize the codebase.
- `train.py` and `score.py` are the two jobs (scripts) that will run according to the details outlined in the config file.

## The ML Pipeline
Skafos allows the developer to build an end-to-end machine learning pipeline and deploy with a  `git push` to a production environment.

## Build Your Own No-Show Predictor 
You will need a few things first:
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Skafos Account + CLI Tool](https://docs.metismachine.io/docs/getting-started)

Feel free to fork this repository and start your own project using any or all code from this example. In order to make it your own:
- Init a new *blank* project with the CLI --> `$ skafos init no-show-predictor`
- Copy and/or replace files in your new project with files from this repository EXCEPT for the `metis.config.yml` file. That one is unique for each project!
- Generate and replace your project's job ID's from the CLI or on the dashboard.
- This example relies on [AWS s3](https://aws.amazon.com/s3/) for storage of the trained model. If you have AWS secret keys, set them as environment variables from the CLI: 
`$ skafos env AWS_ACCESS_KEY_ID --set <key>` and 
`$ skafos env AWS_SECRET_ACCESS_KEY --set <key>`
- Deployment options:

**Without GitHub**
```bash
$ git init
$ git add .
$ git commit -am "first commit"
$ skafos remote info
## Run the output of this command to add an origin
$ git push skafos master
```

**With GitHub**
```bash
$ git init
$ git add .
$ git commit -am "first commit"
$ git remote add origin https://github.com/<user or org name>/no-show-predictor.git
$ git push
```
From here on out, everytime you make some changes and want to redeploy, there is no need to do anything besides commit changes to your local repo (or on your branch) and then push/merge to master.
