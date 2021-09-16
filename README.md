# Deploying a sample to-do app on AWS - ECS version

Hi guys! 
Recently I have been studying for the new AWS SysOps certification and as you may already know, this exam is more on the practical side of things. Since I am not currently employed as a Cloud Engineer/Cloud Administrator, I decided to build and deploy a container version of my  [sample serverless to-do app](https://blogs.houessou.com/sample-todo-app-aws) in other to prepare for most technical aspects of the exam. 
The application logic remains the same - *allow logged in visitors to manage their todo list*, but the underlining infrastructure will change a lot.
For the backend, we will use services like ECS and ECR, Elastic Load Balancers and Autoscaling Group, API Gateway and Cognito; and will make sure that our resources are securely deployed behind a VPC with the proper subnet configuration (NACLs, Route Tables and Security groups). We will deploy a highly available application across AZs, properly maintained and monitored with appropriate CloudWatch alarms and scaling policy.

## Overview & Basic Functionality

Refer to my previous  [blog post](https://blogs.houessou.com/sample-todo-app-aws) to get an overview of the application and learn more about it's functionalities.

## Application Components 

The biggest change with this version of the application is that we decided to deploy services backed by docker containers. And since we are deploying on AWS, *Elastic Container Service* is our choice to host the application backend.
Now along with ECS, we need to have a well defined VPC with networks spanning across multiple availability zones for maximum HA.
Below image should provide a good overview of each layer of the app and especially the technical components involved in the backend.

![app-components.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1631737544541/-loHqk0vX.png)

Let's go through our backend layer components:

**Services container**

The application services (Main and File services) have been written as Python functions served by a Flask App. 
The Flask server is responsible of routing the requests to the corresponding functions i.e.

```
# get todos for the provided path parameter userID
@app.route('/<userID>/todos', methods=['GET'])
def getTodos(userID):
    foo bar...
    ...
    return todolist     # as json
``` 
Even though both services use the same design, they are built in 2 separate images and stored on the AWS Elastic Container Registry. I am doing this to isolate the services so that an issue with one container does not affect the whole application.

> When building the container image, make sure to provide specific tag and version as it is going to be used for the deployment. 
You should also avoid using **latest** for your production environment; it refers to the latest image built without a version specified. Your deployment/update pipeline should add a version to modified images.

**ECS Task**

This is the task definition where we specify how the services containers should be built. It contains information such as container image, environment variables (i.e. the different DynamoDB tables name), container port and log configuration for each container.
I decided to define both services container in one task definition even-if they are not linked. This will help us make sure that we always have the same number of occurrences for all the services containers. 

*Now I didn't really experience the benefice of that configuration over having one task definition per container, if you have any ideas, please add them in the comment section.*

**ECS Service and Cluster**

The ECS service define the deployment configuration for your tasks. I like to compare it to the autoscaling group for tasks/containers. It specifies where our containers will run (instances that are part of the cluster) and how they register themselves to the load balancer to receive traffic.
For this application, we want to create one target group per service - so two target groups in total, since we already have distinct containers per service. By doing it, we make sure that the health of our services are evaluated individually and that some unhealthy containers for the main service do not affect the files service in our case.
Having two target groups will also help the load balancer identify what request goes to what target group based on the path.
The ECS cluster represents the cluster of EC2 instances (or Fargate "servers") that our service containers will be deployed to.

**Application Load Balancer**

With a task definition registered, we're ready to provision the infrastructure needed for our backend. Rather than directly expose our services to the Internet, we will provision an Application Load Balancer (ALB) to sit in front of our services tiers. This would enable our frontend website code to communicate with a single DNS name while our backend service would be free to elastically scale in-and-out based on demand or if failures occur and new containers need to be provisioned.
For our application, with need 2 target groups to allow each service containers register themselves as targets for requests that the load balancer receives to forward. We will create 2 load balancer listener rules as well for the ALB to forward the requests to specific target group based on the request path and parameters - *main service requests go to main service containers, files service request go to files service containers*.

