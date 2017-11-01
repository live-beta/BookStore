from Tests.test_setup import BaseTestClass
from app.models import User, Bucketlist, Item

import json


class BucketlistsTest(BaseTestClass):
    "Tests for bucketlist endpoints"

    def test_authorisation_required(self):
        "Test for no access if token not given"
        get_bucket = self.app.get("/api/v1/bucketlists")
        get_bucket_data = json.loads(get_bucket.data)
        post_item = self.app.post("/api/v1/bucketlists/1/items")
        post_item_data = json.loads(post_item.data)
        self.assertListEqual([401, 401], [get_bucket.status_code,
                                          post_item.status_code])
        self.assertListEqual([Bucketlist.query.count(),
                              Item.query.count()], [1, 1])
        self.assertEqual("Access denied", get_bucket_data["message"])
        self.assertEqual("Access denied", post_item_data["message"])

    def test_token_gives_access(self):
        "Testing that the authentication token gains access"
        response = self.app.get("/api/v1/bucketlists", headers=self.header)
        self.assertEqual(200, response.status_code)

    def test_bad_token(self):
        "Test that access is denied if tocken is incorrect"
        test_token = self.token + "33"
        bad_header = {"Authorization": test_token}
        response = self.app.get("/api/v1/bucketlists", headers=bad_header)
        self.assertEqual(401, response.status_code)

    def test_successfully_add_view_bucketlist(self):
        "Testint that the bucketlist can be added and viewed"
        initial = Bucketlist.query.count()
        data = json.dumps({"name": "test_bucket"})
        response = self.app.post(
            "/api/v1/bucketlists", data=data, headers=self.header, content_type=self.mime_type)
        response_data = json.loads(response.data)
        final_data = Bucketlist.query.count()
        self.assertEqual(1, final_data - initial)
        self.assertEqual(201, response.status_code)
        self.assertIn("test_bucket", response_data["message"])

        response_final = self.app.get(
            "api/v1/bucketlists", headers=self.header)
        response_final_data = json.loads(response_final.data)
        self.assertEqual(200, response_final.status_code)
        self.assertListEqual(["bucket_test_list", "test_bucket"], [
                             response_final_data[0]["name"], response_final_data[1]["name"]])

        bucket_absent = self.app.get(
            "api/v1/bucketlists/12", headers=self.header)
        bucket_absent_data = json.loads(bucket_absent.data)
        self.assertEqual(404, bucket_absent.status_code)
        self.assertIn("not fount", bucket_absent_data["message"])

    def test_inputs_required_to_post(self):
        "Testing that the user inputs are validated"
        initial = Bucketlist.query.count()
        no_det = json.dumps({})

        response = self.app.post(
            "api/v1/bucketlists", data=no_det, headers=self.header, content_type=self.mime_type)
        response_data = json.loads(response.data)
        final_data = Bucketlist.query.count()

        self.assertEqual("Bucketlist name is required",
                         response_data["message"]["name"])
        bl_name = json.dumps({"name": ""})

        bl_name_response = self.app.post(
            "api/v1/bucketlists", data=bl_name, headers=self.header, content_type=self.mime_type)
        new_bl = Bucketlist.query.count()
        resp_bl_name_data = json.loads(bl_name_response.data)
        self.assertEqual("no blank fields allowed",
                         resp_bl_name_data["message"])

        sp_name = json.dumps({"name": " "})
        sp_name_response = self.app.post(
            "api/v1/bucketlists", data=sp_name, headers=self.header, content_type=self.mime_type)

        sp_name_data = json.loads(sp_name_response.data)
        new_sp = Bucketlist.query.count()
        self.assertListEqual("Name is valid", sp_name_data["message"])
        self.assertListEqual([400, 400, 400], [
                             response.status_code, bl_name_response.status_code, sp_name_response.status_code])
        self.assertListEqual(
            [0, 0, 0], [final_data - initial, new_bl - initial, new_sp - initial])

    def test_deleting_bucketlist(self):
        "Test that bucketlist can be viewed and deletes"
        initial_bc_count = Bucketlist.query.count()

        initial_Item_count = Item.query.count()

        deleted_bucket = self.app.delete(
            "/api/v1/bucketlists/1", headers=self.header)
        deleted_bucket_data = json.loads(deleted_bucket.data)

        new_bc_count = Bucketlist.query.count()
        new_Item_count = Item.query.count()

        self.assertEqual(deleted_bucket.status_code, 200)
        self.assertListEqual(
            [1, 1], [initial_bc_count - new_bc_count, initial_Item_count - new_Item_count])
        self.assertIn("testlist has been deleted", deleted_bucket["message"])

        # When one attempts to delete a non existent bucketlist
        no_bucket_list_delete = self.app.delete(
            "/api/v1/bucketlists/1", headers=self.header)
        no_bucket_list_delete_data = json.loads(no_bucket_list_delete.data)
        self.assertEqual(404, no_bucket_list_delete.status_code)
        self.assertIn("bucjetlist not found",
                      no_bucket_list_delete_data["message"])

        bad_del = self.app.delete("/api/v1/bucketlists", headers=self.header)
        bad_del_data = json.loads(bad_del.data)
        self.assertEqual(404, bad_del.status_code)
        self.assertEqual("bad request", bad_del_data["message"])

    def test_update_bucketlist(self):
        "Check that bucket list can update"

        bl_data = json.dumps({"name": "updated testlist"})
        data_empty = json.dumps({})
        data_noname = json.dumps({"name": ""})
        data_space = json.dumps({"name": " "})

        valid = self.app.put("/api/v1/bucketlists/1", data=bl_data,
                             headers=self.header, content_type=self.mime_type)

        valid_data = json.loads(valid.data)

        no_bucket = self.app.put("/api/v1/bucketlists/1", data=bl_data,
                                 headers=self.header, content_type=self.mime_type)
        no_bucket_data = json.loads(no_bucket.data)

        blank = self.app.put("/api/v1/bucketlists/1", data=data_empty,
                             headers=self.header, content_type=self.mime_type)
        blank_data = json.loads(blank.data)

        noname = self.app.put("/api/v1/bucketlists/1", data=data_noname,
                              headers=self.header, content_type=self.mime_type)
        noname_data = json.loads(noname.data)
        name_space = self.app.put("/api/v1/bucketlists/1", data=data_space,
                                  headers=self.header, content_type=self.mime_type)
        name_space_data = json.loads(name_space.data)

        self.assertListEqual([200, 400, 400, 400, 404], [valid.status_code, blank.status_code,
                                                         noname.status_code, name_space.status_code, no_bucket.status_code])
        self.assertIn("bucketlist not found", no_bucket_data["message"])
        self.assertIn("has been updated", valid_data["message"])
        self.assertIn("name_required", blank_data["message"]["name"])
        self.assertIn("no blank fields", noname_data["message"])
        self.assertIn("name is invalid", name_space_data["message"])

        bucket = Bucketlist.query.filter_by(id=1).first()
        self.assertTrue(bucket.date_modified > bucket.date_created)

    def test_user_can_not_access_other_users_buckets(self):
        "Test the logged in user cannot access otheres bucketlists"

        # login by token
        data = json.dumps({"username": "bob", "password": "bobpass"})
        response = self.app.post("/api/v1/auth/login",
                                 data=data, content_type=self.mime_type)

        response_data = json.loads(response.data)
        token = "Bearer " + response_data["token"]
        headerbob = {"Authorization": token}

        # Creating bobs bucketlist
        new_bucket = json.dumps({"name": "Bob's list"})
        bucket = self.app.post("api/v1/bucketlists", data=new_bucket,
                               headers=headerbob, content_type=self.mime_type)

        self.assertEqual(201, bucket.status_code)
        self.assertEqual(2, Bucketlist.query.count())

        # Alice's attempt to access
        alice_bucket = self.app.get(
            "api/v1/bucketlists/2", headers=self.header)
        alice_bucket_data = json.loads(alice_bucket.data)
        self.assertEqual(404, alice_bucket.status_code)
        self.assertIn("bucketlist not found", alice_bucket_data["message"])

    def test_bad_route(self):
        "Test for bad post"
        name = json.dumps({"name": "Does things"})
        bad_post_response = self.app.post(
            "/api/v1/bucketlists/1", data=name, headers=self.header, content_type=self.mime_type)
        bad_put_response = self.app.put(
            "/api/v1/bucketlists", data=name, headers=self.header, content_type=self.mime_type)
        bad_post_response_data = json.loads(bad_post_response.data)
        put_response_data = json.loads(bad_put_response.data)
        self.assertEqual(400, bad_put_response.status_code)
        self.assertEqual(400, bad_post_response.status_code)
        self.assertEqual("This is a bad request, try again",
                         bad_post_response_data["message"])
        self.assertEqual("Bad request", put_response_data["message"])

    def test_search_bucketlist(self):
        "Testing that search functionlity works "

        search = self.app.get(
            "/api/v1/bucketlists?q=list", headers=self.header)
        search_data = json.loads(search.data)
        self.assertEqual(200, search.status_code)
        self.assertEqual("bucket_test_list", search_data[0]["name"])
        #self.assertEqual("alice", search_data[0]["created_by"])

        missing = self.app.get(
            "/api/v1/bucketlists?q=missing", headers=self.header)
        missing_data = json.loads(missing.data)

        self.assertEqual(404, missing.status_code)
        self.assertIn("that name is not found", missing_data["message"])

    def test_pagination_limit_for_bucketlist(self):
        "Testing for pagination and limit arguements"

        name_1 = json.dumps({"name": "lister"})
        self.app.post("/api/v1/bucketlists", data=name_1,
                      headers=self.header, content_type=self.mime_type)

        name_2 = json.dumps({"name": "bloom"})
        self.app.post("/api/v1/bucketlists", data=name_2,
                      headers=self.header, content_type=self.mime_type)

        page_1 = self.app.get(
            "/api/v1/bucketlists?page=1&limit=1", headers=self.header)

        page_1_data = json.loads(page_1.data)

        page_2 = self.app.get("/api/v1/bucketlists?page=2&limit=1",
                              headers=self.header)
        page_2_data = json.loads(page_2.data)

        page_3 = self.app.get("/api/v1/bucketlists?page=3&limit=1",
                              headers=self.header)
        page_3_data = json.loads(page_3.data)

        page_all = self.app.get(
            "/api/v1/bucketlists?page=1&limit=3", headers=self
            .header)
        page_all_data = json.loads(page_all.data)

        self.assertListEqual(
            [200, 200, 200], [page_1.status_code, page_2.status_code, page_3.status_code])
        self.assertListEqual(["bucket_test_list", "lister", "bloom"],
                             [page_1_data[0]["name"], page_2_data[0]["name"], page_3_data[0]["name"]])
        self.assertListEqual(3, len(page_all_data))
