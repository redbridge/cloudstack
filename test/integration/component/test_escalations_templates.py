# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# Import Local Modules
from marvin.cloudstackTestCase import *
from marvin.cloudstackException import *
from marvin.cloudstackAPI import *
from marvin.sshClient import SshClient
from marvin.lib.utils import *
from marvin.lib.base import *
from marvin.lib.common import *
from marvin.lib.utils import checkVolumeSize
from marvin.codes import SUCCESS
from nose.plugins.attrib import attr
from time import sleep
from ctypes.wintypes import BOOLEAN

class TestTemplates(cloudstackTestCase):

    @classmethod
    def setUpClass(cls):
        try:
            cls._cleanup = []
            cls.testClient = super(TestTemplates, cls).getClsTestClient()
            cls.api_client = cls.testClient.getApiClient()
            cls.services = cls.testClient.getParsedTestDataConfig()
            # Get Domain, Zone, Template
            cls.domain = get_domain(cls.api_client)
            cls.zone = get_zone(cls.api_client, cls.testClient.getZoneForTests())
            cls.template = get_template(
                                cls.api_client,
                                cls.zone.id,
                                cls.services["ostype"]
                                )
            cls.hypervisor = cls.testClient.getHypervisorInfo()
            cls.services['mode'] = cls.zone.networktype
            cls.account = Account.create(
                                cls.api_client,
                                cls.services["account"],
                                domainid=cls.domain.id
                                )
            # Getting authentication for user in newly created Account
            cls.user = cls.account.user[0]
            cls.userapiclient = cls.testClient.getUserApiClient(cls.user.username, cls.domain.name)
            cls._cleanup.append(cls.account)
        except Exception as e:
            cls.tearDownClass()
            raise Exception("Warning: Exception in setup : %s" % e)
        return

    def setUp(self):

        self.apiClient = self.testClient.getApiClient()
        self.cleanup = []

    def tearDown(self):
        # Clean up, terminate the created resources
        cleanup_resources(self.apiClient, self.cleanup)
        return

    @classmethod
    def tearDownClass(cls):
        try:
            cleanup_resources(cls.api_client, cls._cleanup)
        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)

        return

    def __verify_values(self, expected_vals, actual_vals):
        """
        @Desc: Function to verify expected and actual values
        @Steps:
        Step1: Initializing return flag to True
        Step1: Verifying length of expected and actual dictionaries is matching.
               If not matching returning false
        Step2: Listing all the keys from expected dictionary
        Step3: Looping through each key from step2 and verifying expected and actual dictionaries have same value
               If not making return flag to False
        Step4: returning the return flag after all the values are verified
        """
        return_flag = True

        if len(expected_vals) != len(actual_vals):
            return False

        keys = expected_vals.keys()
        for i in range(0, len(expected_vals)):
            exp_val = expected_vals[keys[i]]
            act_val = actual_vals[keys[i]]
            if exp_val == act_val:
                return_flag = return_flag and True
            else:
                return_flag = return_flag and False
                self.debug("expected Value: %s, is not matching with actual value: %s" % (
                                                                                          exp_val,
                                                                                          act_val
                                                                                          ))
        return return_flag

    @attr(tags=["advanced", "basic", "provisioning"])
    def test_01_list_templates_pagination(self):
        """
        @Desc: Test to List Templates pagination
        @steps:
        Step1: Listing all the Templates for a user
        Step2: Verifying that no Templates are listed
        Step3: Creating (page size + 1) number of Templates
        Step4: Listing all the Templates again for a user
        Step5: Verifying that list size is (page size + 1)
        Step6: Listing all the Templates in page1
        Step7: Verifying that list size is (page size)
        Step8: Listing all the Templates in page2
        Step9: Verifying that list size is 1
        Step10: Listing the template by Id
        Step11: Verifying if the template is downloaded and ready.
                If yes the continuing
                If not waiting and checking for template to be ready till timeout
        Step12: Deleting the Template present in page 2
        Step13: Listing all the Templates in page2
        Step14: Verifying that no Templates are listed
        """
        # Listing all the Templates for a User
        list_templates_before = Template.list(
                                              self.userapiclient,
                                              listall=self.services["listall"],
                                              templatefilter=self.services["templatefilter"]
                                              )
        # Verifying that no Templates are listed
        self.assertIsNone(
                          list_templates_before,
                          "Templates listed for newly created User"
                          )
        self.services["templateregister"]["ostype"] = self.services["ostype"]
        # Creating pagesize + 1 number of Templates
        for i in range(0, (self.services["pagesize"] + 1)):
            template_created = Template.register(
                                                 self.userapiclient,
                                                 self.services["templateregister"],
                                                 self.zone.id,
                                                 hypervisor=self.hypervisor
                                                 )
            self.assertIsNotNone(
                                 template_created,
                                 "Template creation failed"
                                 )
            if(i < self.services["pagesize"]):
                self.cleanup.append(template_created)

        # Listing all the Templates for a User
        list_templates_after = Template.list(
                                             self.userapiclient,
                                             listall=self.services["listall"],
                                             templatefilter=self.services["templatefilter"]
                                             )
        status = validateList(list_templates_after)
        self.assertEquals(
                          PASS,
                          status[0],
                          "Templates creation failed"
                          )
        # Verifying that list size is pagesize + 1
        self.assertEquals(
                          self.services["pagesize"] + 1,
                          len(list_templates_after),
                          "Failed to create pagesize + 1 number of Templates"
                          )
        # Listing all the Templates in page 1
        list_templates_page1 = Template.list(
                                             self.userapiclient,
                                             listall=self.services["listall"],
                                             templatefilter=self.services["templatefilter"],
                                             page=1,
                                             pagesize=self.services["pagesize"]
                                             )
        status = validateList(list_templates_page1)
        self.assertEquals(
                          PASS,
                          status[0],
                          "Failed to list Templates in page 1"
                          )
        # Verifying the list size to be equal to pagesize
        self.assertEquals(
                          self.services["pagesize"],
                          len(list_templates_page1),
                          "Size of Templates in page 1 is not matching"
                          )
        # Listing all the Templates in page 2
        list_templates_page2 = Template.list(
                                             self.userapiclient,
                                             listall=self.services["listall"],
                                             templatefilter=self.services["templatefilter"],
                                             page=2,
                                             pagesize=self.services["pagesize"]
                                             )
        status = validateList(list_templates_page2)
        self.assertEquals(
                          PASS,
                          status[0],
                          "Failed to list Templates in page 2"
                          )
        # Verifying the list size to be equal to 1
        self.assertEquals(
                          1,
                          len(list_templates_page2),
                          "Size of Templates in page 2 is not matching"
                          )
        # Verifying the state of the template to be ready. If not waiting for state to become ready
        template_ready = False
        count = 0
        while template_ready is False:
            list_template = Template.list(
                                          self.userapiclient,
                                          id=template_created.id,
                                          listall=self.services["listall"],
                                          templatefilter=self.services["templatefilter"],
                                          )
            status = validateList(list_template)
            self.assertEquals(
                              PASS,
                              status[0],
                              "Failed to list Templates by Id"
                              )
            if list_template[0].isready is True:
                template_ready = True
            elif (str(list_template[0].status) == "Error"):
                self.fail("Created Template is in Errored state")
                break
            elif count > 10:
                self.fail("Timed out before Template came into ready state")
                break
            else:
                time.sleep(self.services["sleep"])
                count = count + 1

        # Deleting the Template present in page 2
        Template.delete(
                        template_created,
                        self.userapiclient
                        )
        # Listing all the Templates in page 2 again
        list_templates_page2 = Template.list(
                                             self.userapiclient,
                                             listall=self.services["listall"],
                                             templatefilter=self.services["templatefilter"],
                                             page=2,
                                             pagesize=self.services["pagesize"]
                                             )
        # Verifying that there are no Templates listed
        self.assertIsNone(
                          list_templates_page2,
                          "Templates not deleted from page 2"
                          )
        del self.services["templateregister"]["ostype"]
        return

    @attr(tags=["advanced", "basic", "provisioning"])
    def test_02_download_template(self):
        """
        @Desc: Test to Download Template
        @steps:
        Step1: Listing all the Templates for a user
        Step2: Verifying that no Templates are listed
        Step3: Creating a Templates
        Step4: Listing all the Templates again for a user
        Step5: Verifying that list size is 1
        Step6: Verifying if the template is in ready state.
                If yes the continuing
                If not waiting and checking for template to be ready till timeout
        Step7: Downloading the template (Extract)
        Step8: Verifying that Template is downloaded
        """
        # Listing all the Templates for a User
        list_templates_before = Template.list(
                                              self.userapiclient,
                                              listall=self.services["listall"],
                                              templatefilter=self.services["templatefilter"]
                                              )
        # Verifying that no Templates are listed
        self.assertIsNone(
                          list_templates_before,
                          "Templates listed for newly created User"
                          )
        self.services["templateregister"]["ostype"] = self.services["ostype"]
        self.services["templateregister"]["isextractable"] = True
        # Creating aTemplate
        template_created = Template.register(
                                             self.userapiclient,
                                             self.services["templateregister"],
                                             self.zone.id,
                                             hypervisor=self.hypervisor
                                             )
        self.assertIsNotNone(
                             template_created,
                             "Template creation failed"
                             )
        self.cleanup.append(template_created)
        # Listing all the Templates for a User
        list_templates_after = Template.list(
                                             self.userapiclient,
                                             listall=self.services["listall"],
                                             templatefilter=self.services["templatefilter"]
                                             )
        status = validateList(list_templates_after)
        self.assertEquals(
                          PASS,
                          status[0],
                          "Templates creation failed"
                          )
        # Verifying that list size is 1
        self.assertEquals(
                          1,
                          len(list_templates_after),
                          "Failed to create a Template"
                          )
        # Verifying the state of the template to be ready. If not waiting for state to become ready till time out
        template_ready = False
        count = 0
        while template_ready is False:
            list_template = Template.list(
                                          self.userapiclient,
                                          id=template_created.id,
                                          listall=self.services["listall"],
                                          templatefilter=self.services["templatefilter"],
                                          )
            status = validateList(list_template)
            self.assertEquals(
                              PASS,
                              status[0],
                              "Failed to list Templates by Id"
                              )
            if list_template[0].isready is True:
                template_ready = True
            elif (str(list_template[0].status) == "Error"):
                self.fail("Created Template is in Errored state")
                break
            elif count > 10:
                self.fail("Timed out before Template came into ready state")
                break
            else:
                time.sleep(self.services["sleep"])
                count = count + 1

        # Downloading the Template name
        download_template = Template.extract(
                                             self.userapiclient,
                                             template_created.id,
                                             mode="HTTP_DOWNLOAD",
                                             zoneid=self.zone.id
                                             )
        self.assertIsNotNone(
                             download_template,
                             "Download Template failed"
                             )
         # Verifying the details of downloaded template
        self.assertEquals(
                          "DOWNLOAD_URL_CREATED",
                          download_template.state,
                          "Download URL not created for Template"
                          )
        self.assertIsNotNone(
                             download_template.url,
                             "Download URL not created for Template"
                             )
        self.assertEquals(
                          template_created.id,
                          download_template.id,
                          "Download Template details are not same as Template created"
                          )
        del self.services["templateregister"]["ostype"]
        del self.services["templateregister"]["isextractable"]
        return

    @attr(tags=["advanced", "basic", "provisioning"])
    def test_03_edit_template_details(self):
        """
        @Desc: Test to Edit Template name, displaytext, OSType
        @steps:
        Step1: Listing all the Templates for a user
        Step2: Verifying that no Templates are listed
        Step3: Creating a Templates
        Step4: Listing all the Templates again for a user
        Step5: Verifying that list size is 1
        Step6: Verifying if the template is in ready state.
                If yes the continuing
                If not waiting and checking for template to be ready till timeout
        Step7: Editing the template name
        Step8: Verifying that Template name is edited
        Step9: Editing the template displaytext
        Step10: Verifying that Template displaytext is edited
        Step11: Editing the template ostypeid
        Step12: Verifying that Template ostypeid is edited
        Step13: Editing the template name, displaytext
        Step14: Verifying that Template name, displaytext are edited
        Step15: Editing the template name, displaytext, ostypeid
        Step16: Verifying that Template name, displaytext and ostypeid are edited
        """
        # Listing all the Templates for a User
        list_templates_before = Template.list(
                                              self.userapiclient,
                                              listall=self.services["listall"],
                                              templatefilter=self.services["templatefilter"]
                                              )
        # Verifying that no Templates are listed
        self.assertIsNone(
                          list_templates_before,
                          "Templates listed for newly created User"
                          )
        self.services["templateregister"]["ostype"] = self.services["ostype"]
        # Creating aTemplate
        template_created = Template.register(
                                             self.userapiclient,
                                             self.services["templateregister"],
                                             self.zone.id,
                                             hypervisor=self.hypervisor
                                             )
        self.assertIsNotNone(
                             template_created,
                             "Template creation failed"
                             )
        self.cleanup.append(template_created)
        # Listing all the Templates for a User
        list_templates_after = Template.list(
                                             self.userapiclient,
                                             listall=self.services["listall"],
                                             templatefilter=self.services["templatefilter"]
                                             )
        status = validateList(list_templates_after)
        self.assertEquals(
                          PASS,
                          status[0],
                          "Templates creation failed"
                          )
        # Verifying that list size is 1
        self.assertEquals(
                          1,
                          len(list_templates_after),
                          "Failed to create a Template"
                          )
        # Verifying the state of the template to be ready. If not waiting for state to become ready till time out
        template_ready = False
        count = 0
        while template_ready is False:
            list_template = Template.list(
                                          self.userapiclient,
                                          id=template_created.id,
                                          listall=self.services["listall"],
                                          templatefilter=self.services["templatefilter"],
                                          )
            status = validateList(list_template)
            self.assertEquals(
                              PASS,
                              status[0],
                              "Failed to list Templates by Id"
                              )
            if list_template[0].isready is True:
                template_ready = True
            elif (str(list_template[0].status) == "Error"):
                self.fail("Created Template is in Errored state")
                break
            elif count > 10:
                self.fail("Timed out before Template came into ready state")
                break
            else:
                time.sleep(self.services["sleep"])
                count = count + 1

        # Editing the Template name
        edited_template = Template.update(
                                          template_created,
                                          self.userapiclient,
                                          name="NewTemplateName"
                                          )
        self.assertIsNotNone(
                             edited_template,
                             "Editing Template failed"
                             )
         # Verifying the details of edited template
        expected_dict = {
                         "id":template_created.id,
                         "name":"NewTemplateName",
                         "displaytest":template_created.displaytext,
                         "account":template_created.account,
                         "domainid":template_created.domainid,
                         "format":template_created.format,
                         "ostypeid":template_created.ostypeid,
                         "templatetype":template_created.templatetype,
                         }
        actual_dict = {
                       "id":edited_template.id,
                       "name":edited_template.name,
                       "displaytest":edited_template.displaytext,
                       "account":edited_template.account,
                       "domainid":edited_template.domainid,
                       "format":edited_template.format,
                       "ostypeid":edited_template.ostypeid,
                       "templatetype":edited_template.templatetype,
                       }
        edit_template_status = self.__verify_values(
                                                    expected_dict,
                                                    actual_dict
                                                    )
        self.assertEqual(
                         True,
                         edit_template_status,
                         "Edited Template details are not as expected"
                         )
        # Editing the Template displaytext
        edited_template = Template.update(
                                          template_created,
                                          self.userapiclient,
                                          displaytext="TemplateDisplaytext"
                                          )
        self.assertIsNotNone(
                             edited_template,
                             "Editing Template failed"
                             )
         # Verifying the details of edited template
        expected_dict = {
                         "id":template_created.id,
                         "name":"NewTemplateName",
                         "displaytest":"TemplateDisplaytext",
                         "account":template_created.account,
                         "domainid":template_created.domainid,
                         "format":template_created.format,
                         "ostypeid":template_created.ostypeid,
                         "templatetype":template_created.templatetype,
                         }
        actual_dict = {
                       "id":edited_template.id,
                       "name":edited_template.name,
                       "displaytest":edited_template.displaytext,
                       "account":edited_template.account,
                       "domainid":edited_template.domainid,
                       "format":edited_template.format,
                       "ostypeid":edited_template.ostypeid,
                       "templatetype":edited_template.templatetype,
                       }
        edit_template_status = self.__verify_values(
                                                    expected_dict,
                                                    actual_dict
                                                    )
        self.assertEqual(
                         True,
                         edit_template_status,
                         "Edited Template details are not as expected"
                         )
        # Editing the Template ostypeid
        ostype_list = list_os_types(self.userapiclient)
        status = validateList(ostype_list)
        self.assertEquals(
                          PASS,
                          status[0],
                          "Failed to list OS Types"
                          )
        for i in range(0, len(ostype_list)):
            if ostype_list[i].id != template_created.ostypeid:
                newostypeid = ostype_list[i].id
                break

        edited_template = Template.update(
                                          template_created,
                                          self.userapiclient,
                                          ostypeid=newostypeid
                                          )
        self.assertIsNotNone(
                             edited_template,
                             "Editing Template failed"
                             )
         # Verifying the details of edited template
        expected_dict = {
                         "id":template_created.id,
                         "name":"NewTemplateName",
                         "displaytest":"TemplateDisplaytext",
                         "account":template_created.account,
                         "domainid":template_created.domainid,
                         "format":template_created.format,
                         "ostypeid":newostypeid,
                         "templatetype":template_created.templatetype,
                         }
        actual_dict = {
                       "id":edited_template.id,
                       "name":edited_template.name,
                       "displaytest":edited_template.displaytext,
                       "account":edited_template.account,
                       "domainid":edited_template.domainid,
                       "format":edited_template.format,
                       "ostypeid":edited_template.ostypeid,
                       "templatetype":edited_template.templatetype,
                       }
        edit_template_status = self.__verify_values(
                                                    expected_dict,
                                                    actual_dict
                                                    )
        self.assertEqual(
                         True,
                         edit_template_status,
                         "Edited Template details are not as expected"
                         )
        # Editing the Template name, displaytext
        edited_template = Template.update(
                                          template_created,
                                          self.userapiclient,
                                          name=template_created.name,
                                          displaytext=template_created.displaytext
                                          )
        self.assertIsNotNone(
                             edited_template,
                             "Editing Template failed"
                             )
         # Verifying the details of edited template
        expected_dict = {
                         "id":template_created.id,
                         "name":template_created.name,
                         "displaytest":template_created.displaytext,
                         "account":template_created.account,
                         "domainid":template_created.domainid,
                         "format":template_created.format,
                         "ostypeid":newostypeid,
                         "templatetype":template_created.templatetype,
                         }
        actual_dict = {
                       "id":edited_template.id,
                       "name":edited_template.name,
                       "displaytest":edited_template.displaytext,
                       "account":edited_template.account,
                       "domainid":edited_template.domainid,
                       "format":edited_template.format,
                       "ostypeid":edited_template.ostypeid,
                       "templatetype":edited_template.templatetype,
                       }
        edit_template_status = self.__verify_values(
                                                    expected_dict,
                                                    actual_dict
                                                    )
        self.assertEqual(
                         True,
                         edit_template_status,
                         "Edited Template details are not as expected"
                         )
        # Editing the Template name, displaytext, ostypeid
        edited_template = Template.update(
                                          template_created,
                                          self.userapiclient,
                                          name="NewTemplateName",
                                          displaytext="TemplateDisplaytext",
                                          ostypeid=template_created.ostypeid
                                          )
        self.assertIsNotNone(
                             edited_template,
                             "Editing Template failed"
                             )
         # Verifying the details of edited template
        expected_dict = {
                         "id":template_created.id,
                         "name":"NewTemplateName",
                         "displaytest":"TemplateDisplaytext",
                         "account":template_created.account,
                         "domainid":template_created.domainid,
                         "format":template_created.format,
                         "ostypeid":template_created.ostypeid,
                         "templatetype":template_created.templatetype,
                         }
        actual_dict = {
                       "id":edited_template.id,
                       "name":edited_template.name,
                       "displaytest":edited_template.displaytext,
                       "account":edited_template.account,
                       "domainid":edited_template.domainid,
                       "format":edited_template.format,
                       "ostypeid":edited_template.ostypeid,
                       "templatetype":edited_template.templatetype,
                       }
        edit_template_status = self.__verify_values(
                                                    expected_dict,
                                                    actual_dict
                                                    )
        self.assertEqual(
                         True,
                         edit_template_status,
                         "Edited Template details are not as expected"
                         )
        del self.services["templateregister"]["ostype"]
        return

    @attr(tags=["advanced", "basic", "provisioning"])
    def test_04_copy_template(self):
        """
        @Desc: Test to copy Template from one zone to another
        @steps:
        Step1: Listing Zones available for a user
        Step2: Verifying if the zones listed are greater than 1.
               If Yes continuing.
               If not halting the test.
        Step3: Listing all the templates for a user in zone1
        Step4: Verifying that no templates are listed
        Step5: Listing all the templates for a user in zone2
        Step6: Verifying that no templates are listed
        Step7: Creating a Template in zone 1
        Step8: Listing all the Templates again for a user in zone1
        Step9: Verifying that list size is 1
        Step10: Listing all the templates for a user in zone2
        Step11: Verifying that no templates are listed
        Step12: Copying the template created in step7 from zone1 to zone2
        Step13: Listing all the templates for a user in zone2
        Step14: Verifying that list size is 1
        Step15: Listing all the Templates for a user in zone1
        Step16: Verifying that list size is 1
        """
        # Listing Zones available for a user
        zones_list = Zone.list(
                               self.userapiclient,
                               available=True
                               )
        status = validateList(zones_list)
        self.assertEquals(
                          PASS,
                          status[0],
                          "Failed to list Zones"
                          )
        if not len(zones_list) > 1:
            raise unittest.SkipTest("Enough zones doesnot exists to copy template")
        else:
            # Listing all the Templates for a User in Zone 1
            list_templates_zone1 = Template.list(
                                                 self.userapiclient,
                                                 listall=self.services["listall"],
                                                 templatefilter=self.services["templatefilter"],
                                                 zoneid=zones_list[0].id
                                                 )
            # Verifying that no Templates are listed
            self.assertIsNone(
                              list_templates_zone1,
                              "Templates listed for newly created User in Zone1"
                              )
            # Listing all the Templates for a User in Zone 2
            list_templates_zone2 = Template.list(
                                                 self.userapiclient,
                                                 listall=self.services["listall"],
                                                 templatefilter=self.services["templatefilter"],
                                                 zoneid=zones_list[1].id
                                                 )
            # Verifying that no Templates are listed
            self.assertIsNone(
                              list_templates_zone2,
                              "Templates listed for newly created User in Zone2"
                              )
            self.services["templateregister"]["ostype"] = self.services["ostype"]
            # Listing Hypervisors in Zone 1
            hypervisor_list = Hypervisor.list(
                                              self.apiClient,
                                              zoneid=zones_list[0].id
                                              )
            status = validateList(zones_list)
            self.assertEquals(
                              PASS,
                              status[0],
                              "Failed to list Hypervisors in Zone 1"
                              )
            # Creating aTemplate in Zone 1
            template_created = Template.register(
                                                 self.userapiclient,
                                                 self.services["templateregister"],
                                                 zones_list[0].id,
                                                 hypervisor=hypervisor_list[0].name
                                                 )
            self.assertIsNotNone(
                                 template_created,
                                 "Template creation failed"
                                 )
            self.cleanup.append(template_created)
            # Listing all the Templates for a User in Zone 1
            list_templates_zone1 = Template.list(
                                                 self.userapiclient,
                                                 listall=self.services["listall"],
                                                 templatefilter=self.services["templatefilter"],
                                                 zoneid=zones_list[0].id
                                                 )
            status = validateList(list_templates_zone1)
            self.assertEquals(
                              PASS,
                              status[0],
                              "Templates creation failed in Zone1"
                              )
            # Verifying that list size is 1
            self.assertEquals(
                              1,
                              len(list_templates_zone1),
                              "Failed to create a Template"
                              )
            # Listing all the Templates for a User in Zone 2
            list_templates_zone2 = Template.list(
                                                 self.userapiclient,
                                                 listall=self.services["listall"],
                                                 templatefilter=self.services["templatefilter"],
                                                 zoneid=zones_list[1].id
                                                 )
            # Verifying that no Templates are listed
            self.assertIsNone(
                              list_templates_zone2,
                              "Templates listed for newly created User in Zone2"
                              )
            # Verifying the state of the template to be ready. If not waiting for state to become ready till time out
            template_ready = False
            count = 0
            while template_ready is False:
                list_template = Template.list(
                                              self.userapiclient,
                                              id=template_created.id,
                                              listall=self.services["listall"],
                                              templatefilter=self.services["templatefilter"],
                                              )
                status = validateList(list_template)
                self.assertEquals(
                                  PASS,
                                  status[0],
                                  "Failed to list Templates by Id"
                                  )
                if list_template[0].isready is True:
                    template_ready = True
                elif (str(list_template[0].status) == "Error"):
                    self.fail("Created Template is in Errored state")
                    break
                elif count > 10:
                    self.fail("Timed out before Template came into ready state")
                    break
                else:
                    time.sleep(self.services["sleep"])
                    count = count + 1

            # Copying the Template from Zone1 to Zone2
            copied_template = Template.copy(
                                            self.userapiclient,
                                            template_created.id,
                                            sourcezoneid=template_created.zoneid,
                                            destzoneid=zones_list[1].id
                                            )
            self.assertIsNotNone(
                                 copied_template,
                                 "Copying Template from Zone1 to Zone2 failed"
                                 )
            # Listing all the Templates for a User in Zone 1
            list_templates_zone1 = Template.list(
                                                 self.userapiclient,
                                                 listall=self.services["listall"],
                                                 templatefilter=self.services["templatefilter"],
                                                 zoneid=zones_list[0].id
                                                 )
            status = validateList(list_templates_zone1)
            self.assertEquals(
                              PASS,
                              status[0],
                              "Templates creation failed in Zone1"
                              )
            # Verifying that list size is 1
            self.assertEquals(
                              1,
                              len(list_templates_zone1),
                              "Failed to create a Template"
                              )
            # Listing all the Templates for a User in Zone 2
            list_templates_zone2 = Template.list(
                                                 self.userapiclient,
                                                 listall=self.services["listall"],
                                                 templatefilter=self.services["templatefilter"],
                                                 zoneid=zones_list[1].id
                                                 )
            status = validateList(list_templates_zone2)
            self.assertEquals(
                              PASS,
                              status[0],
                              "Template failed to copy into Zone2"
                              )
            # Verifying that list size is 1
            self.assertEquals(
                              1,
                              len(list_templates_zone2),
                              "Template failed to copy into Zone2"
                              )
            self.assertNotEquals(
                                 "Connection refused",
                                 list_templates_zone2[0].status,
                                 "Failed to copy Template"
                                 )
            self.assertEquals(
                              True,
                              list_templates_zone2[0].isready,
                              "Failed to copy Template"
                              )
        del self.services["templateregister"]["ostype"]
        return