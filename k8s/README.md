# AWS EKS Deployment Guide

This guide explains how to deploy the Asset Management System on AWS Elastic Kubernetes Service (EKS).

## Prerequisites

1. AWS CLI installed and configured
2. eksctl installed
3. kubectl installed
4. Docker installed
5. AWS ECR repository created

## Setup Steps

### 1. Create EKS Cluster

```bash
eksctl create cluster \
  --name asset-management \
  --region us-west-2 \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 5 \
  --managed
```

### 2. Configure kubectl

```bash
aws eks update-kubeconfig --name asset-management --region us-west-2
```

### 3. Create ECR Repository

```bash
aws ecr create-repository --repository-name asset-management
```

### 4. Build and Push Docker Image

```bash
# Build the image
docker build -t asset-management .

# Tag the image
docker tag asset-management:latest \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-west-2.amazonaws.com/asset-management:latest

# Login to ECR
aws ecr get-login-password --region us-west-2 | \
  docker login --username AWS --password-stdin \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-west-2.amazonaws.com

# Push the image
docker push \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-west-2.amazonaws.com/asset-management:latest
```

### 5. Deploy Kubernetes Resources

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Create ConfigMap
kubectl apply -f configmap.yaml

# Create Secret (update with your values)
kubectl apply -f secret.yaml

# Deploy PostgreSQL
kubectl apply -f postgres.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n asset-management

# Deploy Django application
kubectl apply -f django.yaml

# Deploy Ingress
kubectl apply -f ingress.yaml
```

### 6. Run Database Migrations

```bash
# Get a pod name
POD_NAME=$(kubectl get pods -n asset-management -l app=django -o jsonpath="{.items[0].metadata.name}")

# Run migrations
kubectl exec -n asset-management $POD_NAME -- python manage.py migrate

# Create superuser
kubectl exec -n asset-management $POD_NAME -- python manage.py createsuperuser
```

## Monitoring and Maintenance

### View Logs

```bash
kubectl logs -n asset-management -l app=django
```

### Scale Application

```bash
kubectl scale deployment django -n asset-management --replicas=5
```

### Update Application

1. Build and push new Docker image
2. Update deployment:
```bash
kubectl set image deployment/django django=your-ecr-repository/asset-management:new-version -n asset-management
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
kubectl exec -n asset-management $(kubectl get pods -n asset-management -l app=postgres -o jsonpath="{.items[0].metadata.name}") \
  -- pg_dump -U postgres asset_management > backup.sql

# Restore from backup
kubectl exec -i -n asset-management $(kubectl get pods -n asset-management -l app=postgres -o jsonpath="{.items[0].metadata.name}") \
  -- psql -U postgres asset_management < backup.sql
```

## Troubleshooting

### Common Issues

1. **Pod Not Starting**
   - Check logs: `kubectl logs -n asset-management <pod-name>`
   - Check events: `kubectl describe pod -n asset-management <pod-name>`

2. **Database Connection Issues**
   - Verify PostgreSQL is running: `kubectl get pods -n asset-management -l app=postgres`
   - Check PostgreSQL logs: `kubectl logs -n asset-management -l app=postgres`

3. **Ingress Issues**
   - Check ALB status: `kubectl describe ingress -n asset-management`
   - Verify DNS records are pointing to ALB

### Monitoring

1. **Enable CloudWatch Container Insights**
```bash
kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/quickstart/cwagent-fluentd-quickstart.yaml
```

2. **View Metrics in CloudWatch**
   - CPU and Memory usage
   - Network traffic
   - Error rates
   - Latency

## Security Considerations

1. **Network Security**
   - Use VPC security groups
   - Enable VPC flow logs
   - Use private subnets for worker nodes

2. **Access Control**
   - Use IAM roles for service accounts
   - Implement pod security policies
   - Enable encryption at rest

3. **Monitoring**
   - Enable CloudTrail
   - Set up GuardDuty
   - Configure Security Hub

## Cost Optimization

1. **Resource Management**
   - Use spot instances for non-critical workloads
   - Implement auto-scaling
   - Right-size resource requests and limits

2. **Storage**
   - Use EBS gp3 volumes
   - Implement lifecycle policies
   - Regular cleanup of old backups

3. **Networking**
   - Use VPC endpoints
   - Optimize ALB configuration
   - Implement caching where appropriate 