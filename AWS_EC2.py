__author__ = 'zhaopeix'

import os
import time
import boto.ec2
from crawler import crawler
KEY_PAIR_NAME = 'TheKeyPair'
SECURITY_GROUP_NAME = 'csc326-group4'
SECURITY_GROUP_DESC = 'security group for CSC326 project'



class AWS_EC2(object):

    def __init__(self):
        """
        This function will initialize the AWS EC2 instance object
        :return:
        """
        self.address = None
        self.AWS_Access_Key_Id = 0
        self.AWS_Secret_Key = 0
        # read access key id and key from a csv file
        with open('rootkey.csv', 'r') as f:
            for line in f:
                if line.strip().split("=")[0] == 'AWSAccessKeyId':
                    self.AWS_Access_Key_Id = line.strip().split("=")[1]
                elif line.strip().split("=")[0] == 'AWSSecretKey':

                    self.AWS_Secret_Key = line.strip().split("=")[1]

        # setup connection
        self.conn = boto.ec2.connect_to_region("us-east-1", aws_access_key_id = self.AWS_Access_Key_Id,
                                               aws_secret_access_key = self.AWS_Secret_Key)


        #clear up
        self.clean_up()

        # create our new key pair
        self.conn.create_key_pair(KEY_PAIR_NAME).save('')

        # create security group
        self.Security_Group = self.conn.create_security_group(SECURITY_GROUP_NAME, SECURITY_GROUP_DESC)

        # Authorize the protocols
        self.Security_Group.authorize(ip_protocol='icmp', from_port=-1, to_port=-1, cidr_ip='0.0.0.0/0')
        self.Security_Group.authorize(ip_protocol='tcp', from_port=22, to_port=22, cidr_ip='0.0.0.0/0')
        self.Security_Group.authorize(ip_protocol='tcp', from_port=80, to_port=80, cidr_ip='0.0.0.0/0')

        # start the instance
        # Note: run_instances will return a reservation object which may contain more than one instances
        self.instance = self.conn.run_instances('ami-98aa1cf0', key_name=KEY_PAIR_NAME,
                                                security_groups=[self.Security_Group.name],
                                                instance_type='t1.micro').instances[0]



    def instance_state_pull_loop(self, state):
        """
        This function will pull the state of the instance until it equals the state in parameter
        :param state:
        :return:
        """
        while self.instance.state != state:
            time.sleep(5)
            self.instance.update()


    def set_static_ip(self):
        """
        the function will assign a static ip address to the running instance
        :return:
        """
        self.address = self.conn.allocate_address()
        self.address.associate(instance_id = self.instance.id)


    def clean_up(self):
        """
        this function will clean up all the resources use by the previous instance
        :return:
        """

        # remove previous instances
        reservationList = self.conn.get_all_instances()
        for r in reservationList:
            for i in r.instances:
                #pprint (i.__dict__)
                for g in i.groups:
                    if g.name == SECURITY_GROUP_NAME:
                        # this is the public ip used by the instance, we will release it later
                        ip_to_be_release = i.ip_address
                        self.conn.terminate_instances(i.id)
                        # if the state is not terminated yet, wait till it is
                        while i.state != 'terminated':
                            time.sleep(5)
                            i.update()
        # wait till the instance is terminated to remove the security group
        groupList = self.conn.get_all_security_groups()
        for g in groupList:
            if g.name == SECURITY_GROUP_NAME:
                self.conn.delete_security_group(g.name,g.id)

        # release the ip used by the previous instance
        addressList = self.conn.get_all_addresses()
        for a in addressList:
            if a.public_ip == ip_to_be_release:
                self.conn.release_address(public_ip=i.ip_address, allocation_id=a.allocation_id)

        # remove the previous key pair
        self.conn.delete_key_pair(KEY_PAIR_NAME)
        # remove all local key pair files
        os.system("rm -f ./%s" % KEY_PAIR_NAME + '.pem')

if __name__ == "__main__":
    # create the crawler
    print "Crawler Running..."
    bot = crawler(None, "urls.txt")
    bot.crawl(depth=2)
    print "Crawling done"

    print "Preparing to create AWS EC2 instance..."
    # create the instance
    ec2Instance = AWS_EC2()
    # assign the elastic ip address
    print "EC2 Instance Created, Connecting:..."

    ec2Instance.instance_state_pull_loop('running')
    # now running, can assign the static ip
    ec2Instance.set_static_ip()
    print "EC2 Instance Running, Instance ID:" + ec2Instance.instance.id

    #print "Next step: scp -i %s ../CSC326_Lab_2/ ubuntu@%s:~/"  % (KEY_PAIR_NAME+'.pem', ec2Instance.instance.public_dns_name)

    #
    #
    #
    # print "Deploying search engine..."
    # os.system("scp -r -v -o StrictHostKeyChecking=no -i %s ../CSC326_Lab_2/ ubuntu@%s:~/"
    #           % (KEY_PAIR_NAME+'.pem', ec2Instance.instance.public_dns_name))
    #
    #
    # os.system("ssh -v -o StrictHostKeyChecking=no -i %s ubuntu@%s nohup python CSC326_Lab_2/Google_Auth_Test.py"
    #           % (KEY_PAIR_NAME+'.pem', ec2Instance.instance.public_dns_name))
    #
    # print "Search Engine Launched, now you may access it from the following address:"
    # print " http://" + ec2Instance.instance.public_dns_name





