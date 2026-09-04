Create migration=[alembic revision --autogenerate -m "message"]
Apply migrations=[alembic upgrade head]

Roll back one migration=[alembic downgrade -1]
Current migration=[alembic current]
Migration history=[alembic history]



Weed run S3 cli

1. weed server -dir="D:\weed_data" -s3
2. Master UI / API: http://localhost:9333
3. Filer UI / API: http://localhost:8888
4. S3 Gateway: http://localhost:8333



1. Changing Default Port Numbers:
  [ weed server -dir="D:\weed_data" -s3 -master.port=9333 -filer.port=8888 -s3.port=8333]


-master.port: Controls the master management interface (Default: 9333)-
filer.port: Controls the local file system view interface (Default: 8888)-
s3.port: Controls the S3-compatible API endpoint (Default: 8333)

2. Configuring S3 Access Keys

SeaweedFS uses a configuration file named filer.toml to manage S3 buckets, access keys, and secret keys.

Step 1: Generate the configuration fileRun this command to create a default configuration file in your current folder:
[powershellweed scaffold -config=filer -output=.]

Step 2: Edit the Keys
1. Open the newly created filer.toml file in Notepad:--[powershellnotepad filer.toml]
2. Press Ctrl + F and search for [s3.config].
3. Look for the iam (Identity and Access Management) section. It will look like this:
   
   [s3.config]
# it is an array of users
[[s3.config.users]]
name = "test"
actions = ["Read", "Write", "Admin"]
[[s3.config.users.credentials]]
accessKey = "some_access_key"
secretKey = "some_secret_key"
4. Change some_access_key and some_secret_key to your preferred credentials and save the file.

Step 3: Run SeaweedFS with your configTo make SeaweedFS read your new keys and customized ports together, use this command:

[powershellweed server -dir="D:\weed_data" -s3 -s3.config=.\filer.toml]