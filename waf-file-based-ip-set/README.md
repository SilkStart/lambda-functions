# waf-file-based-ip-set

A Lambda function for updating a WAF [IP Set][1] based on changes to a text based
block file in S3.


## IPSet

This lambda function will create the IPSet if it does not already exist.


## Event Source

This lambda function is designed to be subscribed to an [S3 Event Source][2]. Ensure
that the **Event type** supports at least **PUT** events, so that it will be notified
on all updates.


## Policy

To be able to make sufficient use of this Lambda function, you will require a role 
with a number of permissions. An example policy is as follows:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::[S3 Bucket]/[S3 Object]"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "waf:UpdateIPSet",
                "waf:GetIPSet"
            ],
            "Resource": [
                "arn:aws:waf::[Account Number]:*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "waf:GetChangeToken",
                "waf:ListIPSets",
                "waf:CreateIPSet"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```

Be sure to replace `[S3 Bucket]` with the S3 bucket identifier, `[S3 Object]` is 
the S3 Object ID, and `[Account Number]` is the Account number for your S3 Account.


## Block List File

[sample-block-file.txt](sample-block-file.txt) is a sample block list file.


-----

Copyright 2015 SilkStart Technology Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

[1]: http://docs.aws.amazon.com/waf/latest/APIReference/API_IPSet.html
[2]: http://docs.aws.amazon.com/lambda/latest/dg/intro-core-components.html#intro-core-components-event-sources