# Project: Implementation of NetDevOps to a Cloud Environment

## Overview
The project presents an implementation/proof of concept of applying a CI/CD pipeline, taken from the aspects and principles of DevOps, and applying it to a Cloudformation template which contains network-centric infrastrucutre under test: VPC, CIDR blocks, a Site-to-Site VPN through Transit Gateway etc. Although this could be modified and/or extended to also include security aspects such as IAM roles/permission or anything else which is able to be placed into a Cloudformation template. 

The diagram shows the flow of the current implementation.
![Project Diagram](https://github.com/jdockerty/UniProject/blob/master/Images/NetDevOps%20Pipeline%20Diagram.png)

This is achieved through a culmination of various technologies and services, they are as follows:
* CodePipeline (CI/CD service)
* S3 (Source repository/artifact store)
* Cloudformation (Deployment of templates)
* Lambda (Static code analysis on the templates)
* Python (Runtime chosen for Lambda)
* Ansible (On-premise configuration)
* GNS3 (On-premise network emulation)

### On-premise

An interesting aspect of the project came from emulating some sort of on-premise network which could be configured for use with the VPN connection and receive the BGP route advertisement for the cloud provisioned CIDR blocks. To achieve this, GNS3 was chosen with a Cisco router image, this router would be acting as the edge device for a business, connecting them to the outside world. For this project, it was used to peer with AWS using BGP over an IPsec tunnel and advertise the on-premise network block over to our AWS resources and vice versa. As this wasn't the main focus of the project, I kept the configuration simple for the on-premise and aimed to ensure connectivity was possible. 

The diagram below demonstrates the emulated on-premise network design. A CentOS machine, configured with Ansible, is connected to the router for ease of configuration when the AWS network resources are deployed. The CIDR range of `172.31.0.0/30` is used on a virtual loopback interface on the router for testing purposes, this is sent out as a prefix advertisement by BGP. Whilst a larger prefix would be used in an enterprise environment, the main concern was ensuring that the router was a BGP speaker and would peer with its AWS counterpart, forming a neighbourship, and advertising the prefix.

![GNS3 Simple network](https://github.com/jdockerty/UniProject/blob/master/Images/Emulated%20network%20GNS3.png)

At the manual approval stage, this is where the Ansible script was run to configure the router after the appropriate tunnel information and peer addresses were entered. Once this was done, the EC2 instance within the `10.1.0.0/16` CIDR was tested to ping on-premise, this demonstrates reachability to on-premise, thanks to the BGP peering, and back again.

![Successful ping from AWS](https://github.com/jdockerty/UniProject/blob/master/Images/Ping%20from%20cloud%20to%20onpremise%20loopback%20address.png)
