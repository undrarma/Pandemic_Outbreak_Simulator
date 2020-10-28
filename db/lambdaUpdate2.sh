#!/bin/bash
zip -g lambdaFunc.zip createSimulation.py
aws s3 cp lambdaFunc.zip s3://ccbda-lambda-scripts
aws lambda update-function-code --function-name simulation-main --s3-bucket ccbda-lambda-scripts --s3-key lambdaFunc.zip
aws lambda update-function-code --function-name run-simulation --s3-bucket ccbda-lambda-scripts --s3-key lambdaFunc.zip
aws lambda update-function-code --function-name get-statistics --s3-bucket ccbda-lambda-scripts --s3-key lambdaFunc.zip
