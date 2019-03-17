# Steps to set up AWS/CW access keyhole

In your AWS account, navigate to IAM/Users.
![Alt text](CloudWatch_Keyhole_User_a.jpg?raw=true "Create keyhole step 1")

Then to add user, this will be your keyhole access "user".
![Alt text](CloudWatch_Keyhole_User_b.jpg?raw=true "Create keyhole step 2")

Give this "user" <b>only Read, GetMetricWidgetImage</b> permission
![Alt text](CloudWatch_Keyhole_User_c.jpg?raw=true "Create keyhole step 3")

By creating an access keyhole policy 
![Alt text](CloudWatch_Keyhole_User_d.jpg?raw=true "Create keyhole step 4")

Then select this new access keyhole policy for your new "user"
![Alt text](CloudWatch_Keyhole_User_e.jpg?raw=true "Create keyhole step 5")

Create this new "user"
![Alt text](CloudWatch_Keyhole_User_f.jpg?raw=true "Create keyhole step 6")

You will need these parameters "Access key ID" and "Secret access key"
![Alt text](CloudWatch_Keyhole_User_g.jpg?raw=true "Create keyhole step 7")

Now create an initialization file for CW_Remote.py, CW_Remote_Ini_Create.py will help.
![Alt text](CloudWatch_Keyhole_User_h1.jpg?raw=true "Create keyhole step 8")
