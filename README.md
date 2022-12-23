# LOG8415E - Individual Project

## Dependencies:

You need to have Python 3 and AWS CLI installed on your machine. Please refer to [this](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and [this](https://docs.python-guide.org/starting/install3/linux/) in order to install them.

## Launch

To run the main script, you first need to download the standalone script. This can be done using these commands on Ubuntu:

```bash
wget .....
sudo chmod +x script.sh
sudo ./script.sh
```

## Usage

The above script will clone this repository and run an interactive dialog.

```
==============================================
|                  LOG8415E                  |
|             Individual Project             |
|         2018968 - Antoine Lombardo         |
==============================================

Do you want to enter new AWS credentials? (y/n)
```

For the first run, you'll have to run this step. After that, it can be omitted.

```
Please enter your credentials.
You can find them by executing this command in the AWS CLI online:
cat ~/.aws/credentials

AWS Access Key ID: xxx
AWS Secret Access Key: xxx
AWS Session Token: xxx
AWS configured successfully!
```
This step is pretty straigth forward, just enter the AWS credentials that you can get from the AWS online shell.

```
Checking your AWS credentials...
AWS credentials validated.

Please choose one of the options below:
1. Deploy the system.

What do you want to do?
```

For this project, the deployment is automated, and the rest can be done through the REST API using Postman or other tools. The output of the deployment should look like this:

```
==============================================
|                DEPLOYMENT                  |
==============================================

Installing requirements...
Starting AWS setup...
INFO - Found credentials in shared credentials file: ~/.aws/credentials
INFO - Terminating old instances...
INFO -   i-06aa18cfa70c772b8: Terminated.
INFO -   i-0d4753816993af9b3: Terminated.
INFO -   i-0ef5bb1bb6606560d: Terminated.
INFO -   i-0aced8588e24857d6: Terminated.
INFO -   i-0c42c4475033a5621: Terminated.
INFO -   i-04d3c2717889a3dd5: Terminated.
INFO -   i-0cc7ad35e9231105b: Terminated.
INFO - Creating security group "sgo-master"...
INFO -   Already exist.
INFO - Creating security group "sgo-slaves"...
INFO -   Already exist.
INFO - Creating security group "sgo-proxy"...
INFO -   Already exist.
INFO - Creating security group "sgo-stdaln"...
INFO -   Already exist.
INFO - Creating security group "sgo-gtkpr"...
INFO -   Already exist.
INFO - sgo-master: Allowing SSH traffic...
INFO -   Rule already exist.
INFO - sgo-slaves: Allowing SSH traffic...
INFO -   Rule already exist.
INFO - sgo-proxy: Allowing SSH traffic...
INFO -   Rule already exist.
INFO - sgo-stdaln: Allowing SSH traffic...
INFO -   Rule already exist.
INFO - sgo-gtkpr: Allowing SSH traffic...
INFO -   Rule already exist.
INFO - sgo-gtkpr: Allowing HTTP traffic...
INFO -   Rule already exist.
INFO - sgo-slaves: Allowing all traffic from "sgo-slaves"...
INFO -   Rule already exist.
INFO - sgo-master: Allowing all traffic from "sgo-master"...
INFO -   Rule already exist.
INFO - sgo-proxy: Allowing all traffic from "sgo-proxy"...
INFO -   Rule already exist.
INFO - sgo-stdaln: Allowing all traffic from "sgo-stdaln"...
INFO -   Rule already exist.
INFO - sgo-gtkpr: Allowing all traffic from "sgo-gtkpr"...
INFO -   Rule already exist.
INFO - sgo-proxy: Allowing all traffic from "sgo-gtkpr"...
INFO -   Rule already exist.
INFO - sgo-master: Allowing all traffic from "sgo-proxy"...
INFO -   Rule already exist.
INFO - sgo-slaves: Allowing all traffic from "sgo-proxy"...
INFO -   Rule already exist.
INFO - sgo-stdaln: Allowing all traffic from "sgo-proxy"...
INFO -   Rule already exist.
INFO - sgo-slaves: Allowing all traffic from "sgo-master"...
INFO -   Rule already exist.
INFO - sgo-master: Allowing all traffic from "sgo-slaves"...
INFO -   Rule already exist.
INFO - Reading existing keypair...
INFO -   Keypair loaded.
INFO - Creating instance "io-stdaln" of type "t2.micro" instance in zone "us-east-1a"...
INFO -   io-stdaln: Created.
INFO -   io-stdaln: Naming...
INFO -   io-stdaln: Named.
INFO -   io-stdaln: Starting...
INFO -   io-stdaln: Started.
INFO -   io-stdaln: Public DNS.: ec2-54-161-75-43.compute-1.amazonaws.com
INFO -   io-stdaln: Private DNS: ip-172-31-44-103.ec2.internal
INFO - Creating 3 instances of type "t2.micro" instance in zone "us-east-1a"...
INFO -   io-slave1: Created.
INFO -   io-slave2: Created.
INFO -   io-slave3: Created.
INFO -   io-slave1: Naming...
INFO -   io-slave1: Named.
INFO -   io-slave2: Naming...
INFO -   io-slave2: Named.
INFO -   io-slave3: Naming...
INFO -   io-slave3: Named.
INFO -   io-slave1: Starting...
INFO -   io-slave1: Started.
INFO -   io-slave2: Starting...
INFO -   io-slave2: Started.
INFO -   io-slave3: Starting...
INFO -   io-slave3: Started.
INFO -   io-slave1: Public DNS.: ec2-54-198-73-252.compute-1.amazonaws.com
INFO -   io-slave1: Private DNS: ip-172-31-38-233.ec2.internal
INFO -   io-slave2: Public DNS.: ec2-107-20-55-176.compute-1.amazonaws.com
INFO -   io-slave2: Private DNS: ip-172-31-36-186.ec2.internal
INFO -   io-slave3: Public DNS.: ec2-54-152-150-159.compute-1.amazonaws.com
INFO -   io-slave3: Private DNS: ip-172-31-37-176.ec2.internal
INFO - Creating instance "io-master" of type "t2.micro" instance in zone "us-east-1a"...
INFO -   io-master: Created.
INFO -   io-master: Naming...
INFO -   io-master: Named.
INFO -   io-master: Starting...
INFO -   io-master: Started.
INFO -   io-master: Public DNS.: ec2-18-234-119-121.compute-1.amazonaws.com
INFO -   io-master: Private DNS: ip-172-31-34-177.ec2.internal
INFO - Creating instance "io-proxy" of type "t2.large" instance in zone "us-east-1a"...
INFO -   io-proxy: Created.
INFO -   io-proxy: Naming...
INFO -   io-proxy: Named.
INFO -   io-proxy: Starting...
INFO -   io-proxy: Started.
INFO -   io-proxy: Public DNS.: ec2-3-89-156-47.compute-1.amazonaws.com
INFO -   io-proxy: Private DNS: ip-172-31-40-1.ec2.internal
INFO - Creating instance "io-gtkpr" of type "t2.large" instance in zone "us-east-1a"...
INFO -   io-gtkpr: Created.
INFO -   io-gtkpr: Naming...
INFO -   io-gtkpr: Named.
INFO -   io-gtkpr: Starting...
INFO -   io-gtkpr: Started.
INFO -   io-gtkpr: Public DNS.: ec2-3-87-101-137.compute-1.amazonaws.com
INFO -   io-gtkpr: Private DNS: ip-172-31-46-97.ec2.internal
INFO -   io-master: Waiting for initialization...
INFO -   io-master: Initialized.
INFO -   io-slave1: Waiting for initialization...
INFO -   io-slave1: Initialized.
INFO -   io-slave2: Waiting for initialization...
INFO -   io-slave2: Initialized.
INFO -   io-slave3: Waiting for initialization...
INFO -   io-slave3: Initialized.
INFO -   io-stdaln: Waiting for initialization...
INFO -   io-stdaln: Initialized.
INFO -   io-proxy: Waiting for initialization...
INFO -   io-proxy: Initialized.
INFO -   io-gtkpr: Waiting for initialization...
INFO -   io-gtkpr: Initialized.
INFO - Deployment is done! Postman is the recommended tool to interact with the system.
INFO -
INFO - API usage:
INFO - + Start the cluster [GET]
INFO -   http://ec2-3-87-101-137.compute-1.amazonaws.com/start
INFO - + Run benchmark on the cluster [GET]
INFO -   http://ec2-3-87-101-137.compute-1.amazonaws.com/benchmark/cluster
INFO - + Run benchmark on the standalone [GET]
INFO -   http://ec2-3-87-101-137.compute-1.amazonaws.com/benchmark/standalone
INFO - + Make a query using the "Direct" mode [POST]
INFO -   http://ec2-3-87-101-137.compute-1.amazonaws.com/direct
INFO - + Make a query using the "Random" mode [POST]
INFO -   http://ec2-3-87-101-137.compute-1.amazonaws.com/random
INFO - + Make a query using the "Custom" mode [POST]
INFO -   http://ec2-3-87-101-137.compute-1.amazonaws.com/custom
```

## REST API

The Gatekeeper instance is the only one the and user can interact with, other instances security rules drop incoming request from outside.

The available routes are:

- GET - `http://{gatekeeper_dns}/start` - This will start the Cluster.
- GET - `http://{gatekeeper_dns}/benchmark/cluster` - This will run the benchmark on the Cluster.
- GET - `http://{gatekeeper_dns}/benchmark/standalone` - This will run the benchmark on the Standalone.
- POST - `http://{gatekeeper_dns}/direct` - This will execute a query using the 'Direct' mode
- POST - `http://{gatekeeper_dns}/random` - This will execute a query using the 'Random' mode
- POST - `http://{gatekeeper_dns}/custom` - This will execute a query using the 'Custom' mode

More infos are available in the report.
