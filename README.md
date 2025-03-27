# Cloud-Based Messaging Application  

## 📌 Overview  
A cloud-hosted web application built with AWS services to facilitate secure messaging between users via email/SMS, with reply tracking and user management.  

## 🛠️ Architecture  
### Core AWS Services  
| Service       | Purpose                                                                 |
|--------------|-------------------------------------------------------------------------|
| **EC2**       | Hosted Flask web server (Ubuntu)                                        |
| **Cognito**   | User authentication & secure JWT token management                       |
| **DynamoDB**  | Stored user profiles, messages, and replies (NoSQL)                     |
| **Lambda**    | Serverless functions for DB operations & SNS messaging (Python/boto3)   |
| **SNS**       | Sent email/SMS notifications with tracking links                        |
| **API Gateway**| REST API endpoint for triggering Lambda functions                       |

### Key Design Decisions  
- **Storage:** Switched from Athena/S3 to DynamoDB for low-latency API performance  
- **Replies:** Implemented web-based reply collection (due to SNS reply limitations)  
- **Security:** TLS encryption + Cognito JWT validation for all routes  

## 🔧 Implementation  
### Tech Stack  
- **Backend:** Python (Flask), AWS Lambda (boto3)  
- **Frontend:** JavaScript, HTML/CSS  
- **Infrastructure:** AWS Public Cloud (Auto-scaling disabled for cost control)  

### Data Flow  
```mermaid
graph LR
  A[User] -->|Login| B(Cognito)
  B -->|JWT| C[EC2 Webserver]
  C -->|Invoke| D[Lambda]
  D -->|CRUD| E[DynamoDB]
  D -->|Send| F[SNS]
  F --> G[Customer Email/SMS]
  G -->|Link| H[Web Reply Form]
