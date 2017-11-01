from flask_testing import TestCase
from Tests.test_setup import BaseTestClass
from app.models import User, Bucketlist, Item

import json

class list_Item_test(BaseTestClass):
    """ Testing operations on bucket_list entries """

    def test_add_Item(self):
        "Test for adding an Item successfully"

        # Querying the initial and final counts of the entries
        initial_count = Item.query.count()
        Item_name = json.dumps({"name":"Rock Climbing"})
        response = self.app.post("/api/v1/bucketlists/23/items",
                        data= Item_name, headers=self.header,
                        content_type=self.mime_type)

        response_data =json.loads(response.data)

        response_control = self.app.post("/api/v1/bucketlists/23/items",\
                                         data= Item_name, headers=self.header,
                                         content_type=self.mime_type)
        response_control_data = json.loads(response_control.data)

        second_count = Item.query.count()
        # Running asserts

        self.assertEqual(1,second_count-initial_count)
        self.assertListEqual([201,404], [response.status_code,
                                         response_control.status_code])
        self.assertIn("The Bucketlist cannot be found",
                        response_control_data["message"])
        self.assertEqual("Item successfully added to the list",
                         response_data["message"])

    def tests_add_item_wrong_inputs(self):
        """Testing that blank spaces and null arguements are not accepted"""

        blank = json.dumps({})
        empty = json.dumps({"name":""})
        space = json.dumps({"name":" "})

        blank_response = self.app.post("/api/v1/bucketlists/1/items",
                                        data=blank, headers=self.header,
                                        content_type=self.mime_type)
        empty_response = self.app.post("/api/v1/bucketlists/1/items",
                                        data=empty, headers=self.header,
                                        content_type = self.mime_type)
        space_response = self.app.post("/api/v1/bucketlists/1/items",
                                        data= space, headers= self.header,
                                        content_type=self.mime_type)

        blank_response_data = json.loads(blank_response.data)
        empty_response_data = json.loads(empty_response.data)
        space_response_data = json.loads(space_response.data)

        # assertions on the returned data
        self.assertEqual(1,Item.query.count())
        self.assertListEqual([400,400,400],[blank_response.status_code,
                                            empty_response.status_code,
                                            space_response.status_code])
        self.assertIn("Item name required",blank_response_data["message"],["name"])
        self.assertEqual("No blank items allowed",
                        empty_response_data["message"])
        self.assertEqual("You have entered an invalid name",
                        space_response_data["message"])

    def test_delete_item(self):
        "Test that an item is deleted successfully"

        initial = Item.query.count()
        response = self.app.delete("/api/v1/bucketlists/1/items/1",
                                    headers=self.header)
        response_data = json.loads(response.data)

        final_value = Item.query.count()

        self.assertEqual(1, initial - final_value)
        self.assertEqual(200,response.status_code)
        self.assertIn("item has been deleted successfully",
                        response_data["message"])

        Item_unavailable  = self.app.delete("/api/v1/bucketlists/1/items/1",
                                                headers=self.header)
        Item_unavailable_data = json.loads(Item_unavailable.data)
        self.assertEqual(404,Item_unavailable.status_code)
        self.assertIn("item not found", Item_unavailable_data["message"])

    def test_update_item(self):
        "Test that an item can be updated with at least one arguement"
        # defining the validity types

        valid_data = json.dumps({"name": "update_list", "status": "true"})
        invalid_status = json.dumps({"status": "unable"})
        empty_name = json.dumps({"name":"", "status":"true"})
        space_name = json.dumps({"name":" ","status":"true"})
        blank_data = json.dumps({})

        valid_response= self.app.put("/api/v1/bucketlists/1/items/2",
                                        data= valid_data,
                                        headers=self.header,
                                        content_type=self.mime_type)
        blank_response = self.app.put("/api/v1/bucketlists/1/items/2",
                                        data= blank_data,
                                        headers= self.header,
                                        content_type=self.mime_type)
        invalid_response= self.app.put("/api/v1/bucketlists/1/items/2",
                                        data= invalid_status,
                                        headers=self.header,
                                        content_type=self.mime_type)
        invalid_url_response= self.app.put("/api/v1/bucketlists/1/items/2",
                                        data = valid_data,
                                        headers =self.header,
                                        content_type=self.mime_type)
        empty_name_response= self.app.put("/api/v1/bucketlists/1/items/2",
                                        data= empty_name,
                                        headers=self.header,
                                        content_type=self.mime_type)
        space_name_response= self.app.put("/api/v1/bucketlists/1/items/2",
                                        data= space_name,
                                        headers=self.header,
                                        content_type=self.mime_type)

        valid_response_data = json.loads(valid_response.data)
        blank_response_data = json.loads(blank_response.data)
        invalid_response_data = json.loads(invalid_response.data)
        invalid_url_response_data = json.loads(invalid_url_response.data)
        empty_name_response_data = json.loads(empty_name_response.data)
        space_name_response_data = json.loads(space_name_response.data)

        Item_check = Item.query.filter_by(id=1).first()

        self.assertEqual("testlist", Item_check.name)
        self.assertTrue(Item_check.status)
        self.assertTrue(Item_check.date_modified > Item_check.date_created)
        self.assertListEqual([200,400,400,400,400,400],
                            [valid_response.status_code,
                            blank_response.status_code,
                            invalid_url_response.status_code,
                            empty_name_response.status_code,
                            space_name_response.status_code,
                            ])

        self.assertEqual("Item has been updated",valid_response_data["message"])
        self.assertEqual("status required as true or false ",
                        invalid_response_data["message"]["status"])
        self.assertEqual("provide at least one parameter to change",
                        invalid_url_response_data["message"])
        self.assertEqual("name is invalid",
                        space_name_response_data["message"])
        self.assertEqual("name cannot be blank",
                        empty_name_response_data["message"])
        no_bucket_response = self.app.put("/api/v1/bucketlists/34/items/1",
                                            data=valid_data, headers=self.header,
                                            content_type=self.mime_type)

        self.assertEqual(404, no_bucket_response.status_code)
    def test_bad_request(self):
        "Testing put command exception handling"
        valid_data = json.dumps({"name":"Updated list","status":"true"})
        invalid_response = self.app.put("/api/v1/bucketlists/1/items/",
                                            data= valid_data, headers=self.header,
                                            content_type=self.mime_type)
        invalid_response_data = json.loads(invalid_response.data)
        self.assertEqual(invalid_response.status_code, 400)

        self.assertEqual("Bad request",invalid_response_data["message"])
