#!/bin/bash

#Create AIM role for executing Lambdas
aws iam create-role --role-name lambdaRole

#Create s3 bucket
aws s3api create-bucket --bucket ccbda-lambda-scripts --region eu-west-1

#Create Lambdas
aws lambda create-function --function-name createSimulation --zip-file fileb://createSimulationPackages.zip --handler createSimulation.lambda_handler --runtime python3.7 --role arn:aws:iam::236327592378:role/service-role/lambdaRole
aws lambda create-function --function-name getStatistics --zip-file fileb://getStatisticsPackages.zip --handler getStatistics.lambda_handler --runtime python3.7 --role arn:aws:iam::236327592378:role/service-role/lambdaRole
aws lambda create-function --function-name refreshSimList --zip-file fileb://refreshSimListPackages.zip --handler refreshSimList.lambda_handler --runtime python3.7 --role arn:aws:iam::236327592378:role/service-role/lambdaRole

# zip -g lambdaFunc.zip createSimulation.py

#Update Zips in S3
aws s3 cp createSimulationPackages.zip s3://ccbda-lambda-scripts
aws s3 cp getStatisticsPackages.zip s3://ccbda-lambda-scripts
aws s3 cp refreshSimListPackages.zip s3://ccbda-lambda-scripts

#Update Lambdas
aws lambda update-function-code --function-name createSimulation-main --s3-bucket ccbda-lambda-scripts --s3-key createSimulationPackages.zip
aws lambda update-function-code --function-name getStatistics --s3-bucket ccbda-lambda-scripts --s3-key getStatisticsPackages.zip
aws lambda update-function-code --function-name refreshSimList --s3-bucket ccbda-lambda-scripts --s3-key refreshSimListPackages.zip
