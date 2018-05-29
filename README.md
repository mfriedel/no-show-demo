# No-Show Predictor
A sample Skafos project that trains a classifier to predict the likelihood of patients showing up to scheduled appointments in the coming week. All data was acquired from this Kaggle competition.

## Project Contents
- `requirements.txt` contains basic python dependencies.
- `metis.config.yml` contains user-defined configurations for how the deployment should run.
- `helpers/*.` contains helper code and functions to better organize the codebase.
- `train.py` and `score.py` are the two jobs (scripts) that will run according to the details outlined in the config file.

## The ML Pipeline
Skafos allows the developer to build an end-to-end machine learning pipeline and deploy with a  `git push` to a production environment.

## Build Your Own 
Interested in building a No-Show Predictor or something similar? Great - You will need a few things first:
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Skafos Account + CLI Tool](https://docs.metismachine.io/docs/getting-started)

Here are a few tips to get you started in no time:
- Init a new *blank* project with the CLI --> `$ skafos init no-show-predictor`
- Feel free to fork this repository and use any or all of the python code to assist your development.
- Details outlined in the `metis.config.yml` are unique to each developer/project. Copy and pasting the config file from this example to your new project will not work. You can use the outline, but build it based on the file generated in your new project. (The project token is unique for system authentication purposes).
Example project config:
```yml
project_token: <automatically-generated-by-CLI>
name: no-show-demo
jobs: 
  - job_id: <generate-a-new-one>
    language: python
    name: Train
    entrypoint: "train.py"
    schedule: "0 9 * * *"
    resources: 
      limits:
        cpu: 1
        memory: 1Gi
  - job_id: <generate-a-new-one>
    language: python
    name: Score
    entrypoint: "sleep 25 | score.py"
    resources: 
      limits:
        cpu: 1
        memory: 1Gi
    dependencies: [<first-job-id>]
```
- In the config file, generate and replace your project's job ID's from the CLI or on the [dashboard](https://dashboard.metismachine.io).
- This example relies on [AWS s3](https://aws.amazon.com/s3/) for storage of the trained model. If you have AWS secret keys, set them as environment variables from the CLI: 
`$ skafos env AWS_ACCESS_KEY_ID --set <key>` and 
`$ skafos env AWS_SECRET_ACCESS_KEY --set <key>`
- Incorporate your own models, business logic, or workflow as desired!
- Deployment options:

**Without GitHub**
This method doesn't require any github setup. Developers can deploy projects from any local branch (great for testing and development).
```bash
$ git init
$ git add .
$ git commit -am "first commit"
$ skafos remote info
## Run the output of this command to add an origin
$ git push skafos master
```

**With GitHub**
This method requires the developer to set up a github repository and attach the [Skafos App](https://github.com/apps/Skafos) to the project. Any changes made to the master branch will kick off a new deployment based on the config file (great for tested and trusted code that is "master-worthy").
```bash
$ git init
$ git add .
$ git commit -am "first commit"
$ git remote add origin https://github.com/<user or org name>/no-show-predictor.git
$ git push
```
From here on out, everytime you make some changes and want to redeploy, there is no need to do anything besides commit changes to your local repo (or on your branch) and then push/merge to master.

### What's So Special?
Behind the scenes, Skafos is organizing and provisioning cluster resources, managing dependencies, scheduling jobs, and managing data flow. All of the tech stack and spin-up time required to deploy a production scale algorithm is effectively wiped away with a `git push`.

### Need Help?
Check out the [Skafos Documentation](https://docs.metismachine.io).
