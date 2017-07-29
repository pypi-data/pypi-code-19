"""
Cypress Cache module provides a common library for cache objects using Redis cache.
"""
import numpy
import random
import uuid
import redis
import time

from .common_helper import CypressCommonHelper
from .cypress_base import CypressBase

CATEGORY_PREFIX = 'profile:category:'
PROFILE_NP_PREFIX = 'profile:np:'
CATEGORY_HASH_NAME = 'profile:category'
VECTOR_HASH_NAME = 'profile:vector'
METADATA_PREFIX = 'profile:metadata:'

TARGET_NP_PREFIX = 'target:np:'
TARGET_VECTOR_HASH_NAME = 'target:vector'

DATA_IMPORT_HASH_NAME = 'data_import'
DATA_IMPORT_PREFIX = 'data_import:'
DATA_IMPORT_FAILED_SUFFIX = ':failed_images'
DB_IMPORT_ERROR = 'error'
DB_IMPORT_SUCCESS = 'success'
DB_IMPORT_TOTAL = 'total'
DB_IMPORT_TEMP_FAIL_PREFIX = 'temp_failed_import'

MIGRATION_PROFILE_HASH_NAME = 'migration:profile'
MIGRATION_TARGET_HASH_NAME = 'migration:target'


DATA_IMPORT_FAIL_TYPES = {
    0: "NO DETECTION",
    1: "LOW QUALITY",
    2: "INTERNAL SERVER ERROR",
    3: "CATEGORY DOES NOT EXIST",
    4: "IMAGE ID ALREADY EXISTS",
    5: "TOO MANY FACES",
    6: "INVALID IMAGE",
    7: "USER METADATA ERROR"
}

PROCESSOR_TASK_PREFIX = 'worker:'
VIDEO_TOTAL_FRAMES_PREFIX = 'video_frames:'


class CypressCache(CypressBase):
    """
    CypressCache class for using Redis as cache server
    """
    def __init__(self, host='localhost', port=6379, encoding='utf-8', unittest=False):
        """
        Connect to the Redis server.
        :param host: Redis server host name or IP.
        :type host: basestring
        :param port: Redis server port number.
        :type port: int
        :param encoding: Redis encoding.
        :type encoding: basestring
        """
        CypressBase.__init__(self)
        self.unittest = unittest
        self.host = host
        self.port = port
        self.encoding = encoding
        self.redis = None
        self.connect_to_redis()

    ##############################################################
    ###### General Functions ######
    ##############################################################

    def connect_to_redis(self):
        redis_retry_counter = 0
        while True:
            try:
                self.redis = redis.Redis(host=self.host, port=self.port, encoding=self.encoding)
                ret = self.redis.ping()
                if ret:
                    break
            except redis.RedisError and redis.ConnectionError:
                time.sleep(1.0)
                redis_retry_counter += 1
                self.logger.info("Retry connect to Redis host [{0}:{1}]. Retry [{2}]"
                                 .format(self.host, self.port, str(redis_retry_counter)))
                continue

    def is_key_exists(self, name):
        """
        Returns a boolean indicating whether a key "name" exists.
        :param name: the name of the key
        :return: True if the key exists; False if the key doesn't exists.
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.exists(name)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def is_key_exists_in_hash(self, name, key):
        """
        Returns a boolean indicating if "key" exists within hash "name".
        :param name: the hash name
        :param key: the key within the hash name
        :return: True if the key exists within hash "name"; False if the key doesn't exists within hash "name".
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.hexists(name, key)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def get_keys_by_hash_name(self, name):
        """
        Return the list of keys within hash ``name``
        :param name: hash name
        :return: the list of keys within hash ``name``
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.hkeys(name)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def get_all_by_hash_name(self, name):
        """
        Return a Python dict of the hash's name/value pairs
        :param name: The hash name to query
        :return: The object mapped to the hash name as a python dictionary
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.hgetall(name)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def get_kv_by_hash_name(self, name, key):
        """
        Return the value of ``key`` within the hash ``name``
        :param name: hash name to query
        :param key: key within the hash name to get the value for
        :return: the value of ``key`` within the hash ``name``
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.hget(name, key)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def set_kv_to_hash(self, name, key, value):
        """
        Set a key value pair to a hash name.
        :param name: hash name to be set
        :param key: the key within the hash name to add/update
        :param value: the value of the key to be set
        :return:
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.hset(name, key, value)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def increment_hash_kv(self, name, key, amount):
        """
        "Increment the value of ``key`` in hash ``name`` by ``amount``"
        :param name: hash name to be updated
        :param key: the key within the hash name to increment
        :param amount: the number to increment for the value of the key
        :type amount: int
        :return: The new value of the key
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.hincrby(name, key, amount)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def add_to_sorted_set(self, name, *args, **kwargs):
        """
        Set any number of score, element-name pairs to the key ``name``. Pairs
        can be specified in two ways:

        As *args, in the form of: score1, name1, score2, name2, ...
        or as **kwargs, in the form of: name1=score1, name2=score2, ...

        The following example would add four values to the 'my-key' key:
        redis.zadd('my-key', 1.1, 'name1', 2.2, 'name2', name3=3.3, name4=4.4)
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.zadd(name, *args, **kwargs)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def get_sorted_set_rank(self, name, value):
        """
        Returns a 0-based value indicating the rank of ``value`` in sorted set ``name``
        :param name: sorted set name
        :param value: the values to get rank
        :return: If member exists in the sorted set, return the rank of member (integer).
                If member does not exist in the sorted set or key does not exist, return None
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.zrank(name, value)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def remove_from_sorted_set(self, name, *values):
        """
        "Remove member ``values`` from sorted set ``name``"
        :param name: sorted set name
        :param values: the values to be removed
        :return: The number of members removed from the sorted set, not including non existing members.
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.zrem(name, *values)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def set_mkv_to_hash(self, name, mapping):
        """
        Set key to value within hash ``name`` for each corresponding key and value from the ``mapping`` dict.
        :param name: hash name to be set
        :param mapping: a dictionary object contains one ore more key value pairs
        :return:
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.hmset(name, mapping)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def get_value_by_key(self, key):
        """
        Return the value at key ``key``, or None if the key doesn't exist
        :param key: key to query
        :return: the value at key ``key``, or None if the key doesn't exist
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.get(key)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def set_value_to_key(self, key, value):
        """
        Set the value at key ``key`` to ``value``
        :param key: the key to set
        :param value: the value of the key to set
        :return:
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.set(key, value)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def delete_from_sorted_set(self, name,  *values):
        """
        Remove member ``values`` from sorted set ``name``
        :param name: the sorted set name
        :type name: basestring
        :param values: the values to delete
        :type values: string separated by comma. i.e. r.zrem('test_set', 'b:1', 'b:4')
        :return: The number of members removed from the sorted set, not including non existing members.
        :rtype: int
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.zrem(name, *values)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def delete_keys(self, *key):
        """
        Delete one or more keys specified by ``names``
        :param key: the key to delete
        :type key: string or tuple or list
        :return: The number of keys that were removed.
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.delete(*key)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    def delete_keys_from_hash(self, name, *key):
        """
        Delete one or more ``keys`` from hash ``name``
        :param name: the hash name
        :param key: the key within the hash name to delete
        :type key: string or tuple or list
        :return: the number of fields that were removed from the hash, not including specified but non existing fields.
        :rtype: int
        """
        redis_retry_counter = 0
        while True:
            try:
                return self.redis.hdel(name, *key)
            except redis.ConnectionError:
                redis_retry_counter += 1
                self.connect_to_redis()

    ##############################################################
    ###### Video Processor Functions ######
    ##############################################################

    def get_task_id_by_worker_id(self, worker_id):
        """
        Get the task by worker id
        :param worker_id: the id of the offline processor worker
        :type worker_id: basestring or uuid
        :return:
        """
        key = PROCESSOR_TASK_PREFIX + str(worker_id)
        return self.get_kv_by_hash_name(key, "task_id")

    # The below methods are for VA-3147
    def add_task_to_worker(self, worker_id, task_id, task, video_id=None, category_ids=None):
        """
        Add an offline processor task
        :param worker_id: the id of the offline processor worker
        :type worker_id: basestring or uuid
        :param task: video file name with extension
        :type task: basestring
        :return:
        """
        key = PROCESSOR_TASK_PREFIX + str(worker_id)
        self.set_kv_to_hash(key, "task_id", task_id)
        self.set_kv_to_hash(key, "task", task)
        self.set_kv_to_hash(key, "video_id", video_id)
        self.set_kv_to_hash(key, "category_ids", category_ids)

    def get_task_by_worker_id(self, worker_id):
        """
        Get the task by worker id
        :param worker_id: the id of the offline processor worker
        :type worker_id: basestring or uuid
        :return:
        """
        key = PROCESSOR_TASK_PREFIX + str(worker_id)
        task = None
        task_id = None
        video_id = None
        category_ids = None

        if self.is_key_exists(key):
            task_hash_map = self.get_all_by_hash_name(key)
            task = task_hash_map.get("task")
            task_id = task_hash_map.get("task_id")
            video_id = task_hash_map.get("video_id")
            category_ids = task_hash_map.get("category_ids")

        return task, task_id, video_id, category_ids

    def remove_worker_task(self, worker_id):
        """
        Delete the worker task
        :param worker_id: the id of the offline processor worker
        :type worker_id: basestring or uuid
        :return:
        """
        key = PROCESSOR_TASK_PREFIX + str(worker_id)
        self.delete_keys(key)

    def get_all_worker_ids(self):
        """
        Get worker id for all video processing task.
        :return: A list of worker id for video processing tasks.
        """
        worker_ids = []
        for keys in self.redis.scan_iter(match=PROCESSOR_TASK_PREFIX + '*'):
            worker_id = keys.split(":")
            if len(worker_id) == 2:
                worker_ids.append(worker_id[-1])
        return worker_ids

    def set_task_total_frames(self, task_id, total):
        key = VIDEO_TOTAL_FRAMES_PREFIX+str(task_id)
        self.set_value_to_key(key, total)

    def get_task_total_frames(self, task_id):
        key = VIDEO_TOTAL_FRAMES_PREFIX + str(task_id)
        return self.get_value_by_key(key)

    def delete_task_total_frames_key(self, task_id):
        key = VIDEO_TOTAL_FRAMES_PREFIX + str(task_id)
        self.delete_keys(key)

    ##############################################################
    ###### AC Utility Functions ######
    ##############################################################

    def get_category_id(self, image_id):
        """
        Get category id by image id.
        :param image_id: the id of the image to check
        :type image_id: basestring or UUID
        :return: category id if image exists; None if image does not exist
        """
        image_id = str(image_id)
        category_id = self.get_kv_by_hash_name(CATEGORY_HASH_NAME, image_id)
        return category_id

    def is_category_exists(self, category_id):
        """
        Check if category exists in database
        :param category_id: the id the category
        :type category_id: basestring or UUID
        :return: True if exists; False if not exist
        """
        key = CATEGORY_PREFIX + str(category_id)
        return self.is_key_exists(key)

    def add_category(self, category_name, category_description=None):
        """
        Create a new category to the database.
        i.e.
        { "profile:category:<category_id1>":
            {"name": "xinjiang", "description": "this categorys long description or notes",
            "created_time": "1478323698000", "updated_time": "1478323698000"}
        }
        :param category_name: the name of the category. Category name needs to be unique!
        :type category_name: basestring
        :param category_description: the long description of the category
        :type category_description: basestring
        :return: False with a http code (as a tuple) if failed to add a category;
        True with the category id if added successfully.
        :rtype: tuple
        """
        category_id = str(uuid.uuid4())
        category_key = CATEGORY_PREFIX + category_id
        if self.is_key_exists(category_key):
            self.logger.error('Newly generated category id already exists: ' + category_id)
            return False, 500
        if self.is_category_name_exists(category_name):
            # encode category name because it may includes Chinese character
            self.logger.warning('Category name already exists: ' + category_name)
            return False, 409

        ts = CypressCommonHelper.get_current_time_ms()
        # Redis will auto encode the Chinese character here, so no need to encode
        category_info = {
            'name': category_name,
            'description': category_description if category_description else '',
            'created_time': ts,
            'updated_time': ts
        }
        self.set_mkv_to_hash(category_key, category_info)
        return True, category_id

    def edit_category(self, category_id, category_name, category_description=None):
        """
        Update the category name or description.
        :param category_id: the id of the category to edit.
        :type category_id: basestring or UUID
        :param category_name: the new name of the category, required
        :type category_name: basestring
        :param category_description: the new description of the category, optional
        :type category_description: basestring
        :return: True with http code if updated; False with http error code if failed to edit.
        :rtype: tuple
        """
        category_id = str(category_id)
        if not self.is_category_exists(category_id):
            self.logger.warning('category_id does not exist: ' + category_id)
            return False, 404

        if isinstance(category_name, unicode):
            category_name = category_name.encode('utf-8')

        key = CATEGORY_PREFIX + category_id
        if self.get_kv_by_hash_name(key, 'name') != category_name and self.is_category_name_exists(category_name):
            # it's ok to have the input name equal to itself's name
            self.logger.warning('Category name already exists: ' + category_name)
            return False, 409

        if category_description:
            self.set_kv_to_hash(key, 'description', category_description)

        self.set_kv_to_hash(key, 'name', category_name)
        self.set_kv_to_hash(key, 'updated_time', CypressCommonHelper.get_current_time_ms())
        return True, 200

    def get_category_info(self, category_id):
        """
        Get the details of a category.
        :param category_id: id of the category
        :type category_id: basestring or UUID
        :return: None if category does not exist; Otherwise, return the object mapped to the category. i.e.
         {"name": "xinjiang", "description": "this categorys long description or notes",
         "created_time": "1478323698000", "updated_time": "1478323698000"}
        :rtype: python dictionary
        """
        category_id = str(category_id)
        cat_key = CATEGORY_PREFIX + category_id
        result = self.get_all_by_hash_name(cat_key)
        if not result:
            return None
        return result

    def get_all_categories(self):
        """
        Get a list of category ids in the database.
        i.e. ['<cat id 1>','<cat id 2>','<cat id 3>']
        :return: a list of category ids from the database. Empty list if there's no category found.
        """
        match = CATEGORY_PREFIX+'*'
        results = [k.split(':')[-1] for k in self.redis.keys(pattern=match)]
        return results

    def is_category_name_exists(self, category_name):
        """
        Check if the category name already exists.
        :param category_name: the name of the category
        :type category_name: basestring
        :return: True if category name exists; False if category does not exist.
        """
        if isinstance(category_name, unicode):
            category_name = category_name.encode('utf-8')
        match = CATEGORY_PREFIX + '*'
        for cat_key in self.redis.keys(pattern=match):
            for k, v in self.redis.hscan_iter(cat_key, match='name'):
                if v == category_name:
                    return True
        return False

    def get_category_id_by_name(self, category_name):
        """
        Get a category id by category name, as category name is unique.
        :param category_name: The unique name of the category
        :type category_name: basestring
        :return: The id of the category that has the input category name. None if category name does not exist.
        """
        if isinstance(category_name, unicode):
            category_name = category_name.encode('utf-8')
        match = CATEGORY_PREFIX + '*'
        for cat_key in self.redis.keys(pattern=match):
            for k, v in self.redis.hscan_iter(cat_key, match='name'):
                if v == category_name:
                    return cat_key.split(':')[-1]
        return None

    def clear_category(self, category_id):
        """
        Delete all category associated image information from database, without deleting the category information.
        -1. delete from profile vector hash table
        -2. delete from profile category hash table
        -3. delete profile np hash table
        -4. delete profile metadata from profile metadata key value pair
        -5. delete profile metadata from profile metadata set
        :param category_id: The id of the category to delete
        :type category_id: basestring
        :return: True if cleared successfully (no matter it exist or not)
        """
        category_id = str(category_id)
        if not self.is_category_exists(category_id):
            self.logger.warning('Category does not exist in category table: {0}'.format(category_id))

        profile_ids = self.get_profile_ids_by_category(category_id)
        if profile_ids:
            cat_profile_ids = []
            np_profile_hashes = []
            meta_keys = []
            for image_id in profile_ids:
                cat_profile_ids.append(category_id + ':' + image_id)
                np_profile_hashes.append(PROFILE_NP_PREFIX + image_id)
                meta_keys.append(METADATA_PREFIX + image_id)

            # 1. delete from profile vector hash table
            self.delete_keys_from_hash(VECTOR_HASH_NAME, *cat_profile_ids)
            # 2. delete from profile category hash table
            self.delete_keys_from_hash(CATEGORY_HASH_NAME, *profile_ids)
            # 3. delete from profile np hash table
            self.delete_keys(*np_profile_hashes)
            # 4. delete profile metadata from profile metadata key value pair
            self.delete_keys(*meta_keys)
            # 5. delete profile metadata from profile metadata set
            set_name = METADATA_PREFIX + category_id
            self.delete_keys(set_name)
        else:
            self.logger.info('No profile is found for category: {0}'.format(category_id))

        return True

    def delete_category(self, category_id):
        """
        Delete a category with all associated image information from database by category id.
        -1. delete from profile vector hash table
        -2. delete from profile category hash table
        -3. delete profile np hash table
        -4. delete profile metadata from profile metadata key value pair
        -5. delete profile metadata from profile metadata set
        -6. delete profile category table
        :param category_id: The id of the category to delete
        :type category_id: basestring
        :return: True if deleted successfully (no matter it exist or not), False if delete failed
        """
        category_id = str(category_id)
        if not self.is_category_exists(category_id):
            self.logger.warning('Category does not exist in category table: {0}'.format(category_id))

        profile_ids = self.get_profile_ids_by_category(category_id)
        if profile_ids:
            cat_profile_ids = []
            np_profile_hashes = []
            meta_keys = []
            for image_id in profile_ids:
                cat_profile_ids.append(category_id + ':' + image_id)
                np_profile_hashes.append(PROFILE_NP_PREFIX + image_id)
                meta_keys.append(METADATA_PREFIX + image_id)

            # 1. delete from profile vector hash table
            self.delete_keys_from_hash(VECTOR_HASH_NAME, *cat_profile_ids)
            # 2. delete from profile category hash table
            self.delete_keys_from_hash(CATEGORY_HASH_NAME, *profile_ids)
            # 3. delete from profile np hash table
            self.delete_keys(*np_profile_hashes)
            # 4. delete profile metadata from profile metadata key value pair
            self.delete_keys(*meta_keys)
            # 5. delete profile metadata from profile metadata set
            set_name = METADATA_PREFIX + category_id
            self.delete_keys(set_name)
        else:
            self.logger.info('No profile is found for category: {0}'.format(category_id))

        # 6. delete from profile category table
        cat_key = CATEGORY_PREFIX + category_id
        delete_task = self.delete_keys(cat_key)
        return delete_task == 1 or delete_task == 0

    def get_profiles_count(self, category_id=None):
        """
        Get the number of profiles within a category.
        If category id is not provided, then return the total number of profiles in the whole database.
        :param category_id: The category id to query the number of profiles that is within this category
        :type category_id: basestring or UUID
        :return: the number of profiles within the category
        """
        if category_id is None:
            return self.redis.hlen(VECTOR_HASH_NAME)

        category_id = str(category_id)
        set_name = METADATA_PREFIX + category_id
        count = self.redis.zcard(set_name)

        return count

    def add_image_to_profiles(self, image_id, category_id, np_bytes, axis0, axis1, expire=600):
        """
        Add a new image with numpy array bytes, dimension information to the database, associate with a category.
        Return False if the input category doesn't exist.
        The image will be one of the profiles, a search will be against these profiles.
        i.e. {"profile:np:<image_id1>": {"matrix":"<numpy array bytes>", "axis0": "2", "axis1": "5"}}
        { "profile:category": {"id1": "00", "id3": "01", ......} }
        :param image_id: The id of the image to create
        :type image_id: basestring or UUID
        :param category_id: the id of the category that is associated with the image
        :type category_id: basestring or UUID
        :param np_bytes: the numpy array of the image in bytes. The image must be in mode 'BGR'!
        :type np_bytes: bytes
        :param axis0: numpy array dimension, the first element in the tuple
        :type axis0: int
        :param axis1: numpy array dimension, the second element in the tuple
        :type axis1: int
        :param expire: Set an expire flag on key name(profile:np:<image_id1>) for xx seconds. Default to 600s.
        :type expire: can be represented by an integer or a Python timedelta object. If it's None, then no expire.
        :return: False with http error code if failed to add a new image; True with http code if added successfully.
        :rtype: tuple
        """
        category_id = str(category_id)
        image_id = str(image_id)

        if not self.is_category_exists(category_id):
            return False, 404

        np_hash_name = PROFILE_NP_PREFIX + image_id

        if self.is_key_exists(np_hash_name):
            self.logger.warning('Image already exists: ' + np_hash_name)
            return False, 409
        if self.is_key_exists_in_hash(CATEGORY_HASH_NAME, image_id):
            self.logger.warning('Image already exists in category hash table: ' + image_id)
            return False, 409

        hash_mapping = {'matrix': np_bytes, 'axis0': axis0, 'axis1': axis1}
        set_np = self.set_mkv_to_hash(np_hash_name, hash_mapping)
        if expire:
            # set expire to np_hash_name
            self.redis.expire(np_hash_name, expire)

        set_category = self.set_kv_to_hash(CATEGORY_HASH_NAME, image_id, category_id)
        return set_np == 1 and set_category == 1, 201

    def delete_image_from_profiles(self, image_id):
        """
        Delete the numpy array information of a profile by removing key "profile:np:<image_id1>"
        i.e. {"profile:np:<image_id1>": {"matrix":"<numpy array bytes>", "axis0": "2", "axis1": "5"}}
        :param image_id: The id of the image to delete numpy array information
        :type image_id: basestring or UUID
        :return: (True, 204) if deleted; (False, 404) if image np info does not exist in profiles database
        :rtype: tuple
        """
        image_id = str(image_id)
        category_id = self.get_category_id(image_id)
        if not category_id:
            self.logger.error('There is no category found for profile: {}'.format(image_id))
            return False, 404

        del_np = self.delete_keys(PROFILE_NP_PREFIX + image_id)
        if del_np == 0:
            self.logger.warning('There is no numpy array information to be deleted for profile: {}'.format(image_id))
            return False, 404
        return True, 204

    def add_image_to_targets(self, image_id, np_bytes, axis0, axis1, expire=600):
        """
        Add a new image with numpy array bytes, dimension information to the database, without category information.
        The image will be the target image to search against the profile database.
        i.e. { "target:np:id1": {"matrix":"<matrix bytes>", "axis0": "34", "axis1": "54"} }
        :param image_id: the id of the image to create
        :type image_id: basestring or UUID
        :param np_bytes: the numpy array of the image in bytes. The image must be in mode 'BGR'!
        :type np_bytes: bytes
        :param axis0: numpy array dimension, the first element in the tuple
        :type axis0: int
        :param axis1: numpy array dimension, the second element in the tuple
        :type axis1: int
        :param expire: Set an expire flag on key name(target:np:<image_id1>) for xx seconds. Default to 600s.
        :type expire: can be represented by an integer or a Python timedelta object. If it's None, then no expire.
        :return: False if image already exists; True if add image succeed.
        """
        image_id = str(image_id)
        hash_name = TARGET_NP_PREFIX + image_id

        if self.is_key_exists(hash_name):
            self.logger.warning('Image already exists in target image hash table: ' + hash_name)
            return False

        hash_mapping = {'matrix': np_bytes, 'axis0': axis0, 'axis1': axis1}
        set_target_zp = self.set_mkv_to_hash(hash_name, hash_mapping)
        if expire:
            # set expire to hash_name
            self.redis.expire(hash_name, expire)

        return set_target_zp == 1

    def add_metadata_to_profile(self, profile_id, category_id, metadata, max_size=128):
        """
        Add user metadata to a profile, as sorted set for pagination purpose.
        If the profile with same metadata already exists, the new request will overwrite the old data.
        Only call this method after add_image_to_profiles(profile_id, ...) was called, make sure the profile id exists in:
        { "profile:category": {"<profile_id3>": "<category_id2>", ......} }

        i.e. metadata structure
        { "profile:metadata:<category_id1>": ["<image_id1>"(score1), "<image_id3>"(score2), ......] }
        For each profile that has metadata:
        { "profile:metadata:<image_id1>": "user_metadata_1"}
        :param profile_id: the id of the profile/image to add user metadata to.
        :type profile_id: basestring or UUID
        :param category_id: the id of the category the profile belongs to.
        :type category_id: basestring or UUID
        :param metadata: stringified user meatadata
        :type metadata: basestring
        :param max_size: maximum size of input metadata, default to 128
        :type max_size: int
        :return: True if add/update metadata to profile succeed; False otherwise.
        """
        if isinstance(metadata, unicode):
            metadata = metadata.encode('utf-8')
        if len(metadata) > max_size:
            self.logger.error('Input metadata is too big, max size: {}'.format(max_size))
            raise IOError('Input metadata is too big, max size: {}'.format(max_size))
        profile_id = str(profile_id)
        category_id = str(category_id)
        if self.get_kv_by_hash_name(CATEGORY_HASH_NAME, profile_id) != category_id:
            self.logger.error('The profile: {} does not belong to category: {}.'.format(profile_id, category_id))
            raise IOError('The profile: {} does not belong to category: {}.'.format(profile_id, category_id))

        set_name = METADATA_PREFIX + category_id
        # generate a random float number between 0 and 1000. If it's updating, the score/rank of the value will change
        random_score = random.uniform(0, 1000)
        self.add_to_sorted_set(set_name, profile_id, random_score)

        metadata_key = METADATA_PREFIX + profile_id
        result = self.set_value_to_key(metadata_key, str(metadata))

        return result == 1 or result == 0

    def get_profiles_by_category(self, category_id, start, end, desc=False, withscores=False, score_cast_func=float):
        """
        Return a range of values from sorted set between ``start`` and ``end`` sorted in ascending order (default).
        :param category_id: the id of the category to get profiles from.
        :param start: index, can be negative, indicating the start of the range.
        :param end: index, can be negative, indicating the end of the range.
        :param desc: a boolean indicating whether to sort the results descendingly
        :param withscores: indicates to return the scores along with the values. The return type is a list of (value, score) pairs
        :param score_cast_func: a callable used to cast the score return value
        :return: Empty list if there's no profiles within the category; Otherwise, a list of metadata with image id:
        i.e. ["<image_id1>", "<image_id3>", ......]
        """
        category_id = str(category_id)
        set_name = METADATA_PREFIX + category_id
        results = self.redis.zrange(set_name, start, end, desc, withscores, score_cast_func)
        return results

    def get_profile_metadata(self, profile_id):
        """
        Get user metadata of a profile. i.e.
        { "profile:metadata:<image_id1>": "user_metadata_1"}
        :param profile_id: the id of the profile to get metadata from
        :type profile_id: basestring or uuid
        :return: profile user metadata as a string; None if no metadata is found.
        :rtype: basestring
        """
        return self.get_value_by_key(METADATA_PREFIX + str(profile_id))

    def add_vector_to_profile(self, image_id, vector):
        """
        Add image vector information to an image in profiles database.
        i.e. { "profile:vector": {"00:id1": "vector2", "01:id3": "vector3", ......} }
        :param image_id: the id of the image to add vector information
        :type image_id: basestring or UUID
        :param vector: the vector information of the face image
        :type vector: bytes
        :return: False if failed to add vector to profile; True if succeed.
        """
        image_id = str(image_id)
        category_id = self.get_category_id(image_id)
        if not category_id:
            self.logger.warning('Image does not exist: ' + image_id)
            return False

        vector_key = str(category_id) + ':' + image_id
        if self.is_key_exists_in_hash(VECTOR_HASH_NAME, vector_key):
            self.logger.warning('Vector already exists: ' + vector_key)
            return False
        set_vector = self.set_kv_to_hash(VECTOR_HASH_NAME, vector_key, vector)
        return set_vector == 1

    def add_vector_to_target(self, image_id, vector):
        """
        Add image vector information to an image in targets database.
        i.e. { "target:vector": {"id1": "vector2", "id3": "vector3", ......} }
        :param image_id: the id of the image to add vector information
        :type image_id: basestring or UUID
        :param vector: the vector information of the face image
        :type vector: bytes
        :return: False if failed to add vector to target; True if succeed.
        """
        image_id = str(image_id)

        if self.is_key_exists_in_hash(TARGET_VECTOR_HASH_NAME, image_id):
            self.logger.warning('Vector already exists: ' + image_id)
            return False
        set_vector = self.set_kv_to_hash(TARGET_VECTOR_HASH_NAME, image_id, vector)
        return set_vector == 1

    def get_vector_from_profiles(self, image_id):
        """
        Get vector information of an image from the profile database.
        :param image_id: the id of the image used to get the vector information
        :type image_id: basestring or UUID
        :return: vector information if there's one
        """
        image_id = str(image_id)
        category_id = self.get_category_id(image_id)
        if not category_id:
            self.logger.warning('Image does not exist: ' + image_id)
            return None

        vector_key = category_id + ':' + image_id
        value = self.get_kv_by_hash_name(VECTOR_HASH_NAME, vector_key)
        if not value:
            self.logger.warning('Vector information does not exist.')
            return None
        return value

    def get_vector_from_targets(self, image_id):
        """
        Get vector information of an image from the targets database.
        :param image_id: the id of the image used to get the vector information
        :type image_id: basestring or UUID
        :return: vector information if there's one
        """
        image_id = str(image_id)
        value = self.get_kv_by_hash_name(TARGET_VECTOR_HASH_NAME, image_id)
        if not value:
            self.logger.warning('Vector information does not exist.')
            return None
        return value

    def get_np_image_by_id(self, image_id, usage='profile'):
        """
        Read the image object from targets database by image_id, reshape the one dimensional array to
         mutli-dimension array using the `axis0` and `axis1`. Return the image in np.ndarray format.
        :param image_id: image id
        :type image_id: basestring or uuid
        :param usage: The usage passed in from engine. Default to 'profile', anything else goes to targets db
        :type usage: basestring
        :return: on success - reshaped image in ndarray (The image is in mode 'BGR'!); on failure - None
        """
        try:
            if usage == 'profile':
                img_obj = self.get_np_from_profiles(image_id)
            else:
                img_obj = self.get_np_from_targets(image_id)
            image = numpy.frombuffer(img_obj.get('matrix'), dtype=numpy.uint8)\
                .reshape(int(img_obj.get('axis0')), int(img_obj.get('axis1')), 3)
            return numpy.copy(image)
        except AttributeError as e:
            self.logger.error("Failed to reshape image. msg={0}".format(str(e)))
            return None

    def get_np_from_profiles(self, image_id):
        """
        Get image numpy array in bytes information of an image from the profiles database.
        :param image_id: the id of the image used to get the numpy array bytes information
        :type image_id: basestring or UUID
        :return: dictionary object, image numpy array bytes with dimension information if there's one.
        Note: The image is in mode 'BGR'!
        i.e.  {'matrix': 'np bytes', 'axis0': '23', 'axis1': '32'}
        Return None if not found.
        """
        image_id = str(image_id)
        hash_name = PROFILE_NP_PREFIX + image_id
        obj = self.get_all_by_hash_name(hash_name)
        if not obj:
            self.logger.warning('Image numpy array information does not exist.')
            return None
        return obj

    def delete_profile(self, image_id):
        """
        Remove an image (np data, vector data, categroy data) in profiles database.
        The five data structures to operate on:
        { "profile:vector": {"<category_id1>:<image_id1>": "vector2", "<category_id2>:<image_id3>": "vector3", ......} }
        { "profile:np:<image_id1>": {"matrix":"<numpy array bytes>", "axis0": "2", "axis1": "5"} }
        { "profile:category": {"<image_id1>": "<category id>", "<image_id3>": "<category id>", ......} }
        { "profile:metadata:<image_id1>": "user_metadata_1" }
        { "profile:metadata:<category_id1>": ["<image_id1>"(score1), "<image_id3>"(score2), ......] }
        :param image_id: the id of the image to delete
        :type image_id: basestring or uuid
        :return: (True, 204) if deleted; (False, 404) if image does not exist in profiles database
        :rtype: tuple
        """
        image_id = str(image_id)
        category_id = self.get_category_id(image_id)
        if not category_id:
            self.logger.warning('Category does not exist.')
            return False, 404
        vector_key = str(category_id) + ':' + image_id
        np_hash_name = PROFILE_NP_PREFIX + image_id

        del_vector = self.delete_keys_from_hash(VECTOR_HASH_NAME, vector_key)
        del_cat = self.delete_keys_from_hash(CATEGORY_HASH_NAME, image_id)

        metadata_key = METADATA_PREFIX + image_id
        self.delete_keys(metadata_key)
        set_name = METADATA_PREFIX + category_id
        self.delete_from_sorted_set(set_name, image_id)

        # note: this returns either 0 or 1 because np_hash_name could be expired
        del_np = self.delete_keys(np_hash_name)

        if not del_vector and not del_cat:
            self.logger.warning('Image does not exist in profiles database.')
            return False, 404
        return True, 204

    def get_np_from_targets(self, image_id):
        """
        Get image numpy array in bytes information of an image from the targets database.
        :param image_id: the id of the image used to get the numpy array bytes information
        :type image_id: basestring or UUID
        :return: dictionary object, image numpy array bytes with dimension information if there's one.
        Note: The image is in mode 'BGR'!
        i.e.  {'matrix': 'np bytes', 'axis0': '23', 'axis1': '32'}
        Return None if not found.
        """
        image_id = str(image_id)
        hash_name = TARGET_NP_PREFIX + image_id
        obj = self.get_all_by_hash_name(hash_name)
        if not obj:
            self.logger.warning('Image numpy array information does not exist.')
            return None
        return obj

    def delete_target(self, image_id):
        """
        Remove an image (np data and vector data) in targets database.
        The two data structures to operate on:
        { "target:vector": {"<image_id1>": "vector2", "<image_id3>": "vector3", ......} }
        { "target:np:<image_id1>":  {"matrix":"<numpy array bytes>", "axis0": "34", "axis1": "54"} }
        :param image_id: the id of the image to delete
        :type image_id: basestring or uuid
        :return: True if deleted; False if image does not exist in targets database.
        """
        image_id = str(image_id)
        del_vector = None
        del_np = None

        if not self.is_key_exists_in_hash(TARGET_VECTOR_HASH_NAME, image_id):
            self.logger.warning('Image does not exist in target vector hash table: {0}'.format(image_id))
        else:
            del_vector = self.delete_keys_from_hash(TARGET_VECTOR_HASH_NAME, image_id)

        np_hash_name = TARGET_NP_PREFIX + image_id
        if not self.is_key_exists(np_hash_name):
            self.logger.warning('Image does not exist in target np hash table: {0}'.format(image_id))
        else:
            del_np = self.delete_keys(np_hash_name)

        if not del_np and not del_vector:
            self.logger.warning('Image does not exist in targets database.')
            return False
        return True

    def get_all_profile_vectors(self, use_float16=False):
        """
        Return a tuple with two elements: array of profile ids, array of profile vectors.
        :return: a tuple with two elements: array of profile ids with category data (python array), array of profile vectors (numpy array).
        ['01:image_id_1', '04:image_id_2'], ['vector1', 'vector2']
        Return empty arrays if no result is found.
        """
        profile_ids = []
        profile_vectors = []
        for k, v in self.redis.hscan_iter(VECTOR_HASH_NAME):
            try:
                # get the second part of the key (image id)
                profile_ids.append(k)
                vec_32 = numpy.frombuffer(v, dtype=numpy.float32)

                if use_float16 is True:
                    vec_16 = numpy.array(vec_32, dtype=numpy.float16)
                    profile_vectors.append(vec_16)
                else:
                    profile_vectors.append(vec_32)
            except Exception as e:
                try:
                    profile_ids.remove(k)
                except:
                    pass
                self.logger.error("failed to get vector for profile {0}, exception {1}".format(k, e))

        if use_float16 is True:
            np_profile_vectors = numpy.asarray(profile_vectors, dtype=numpy.float16)
        else:
            np_profile_vectors = numpy.asarray(profile_vectors, dtype=numpy.float32)

        # return empty python list, not np list if np list is empty
        if np_profile_vectors.size == 0:
            if use_float16 is True:
                return profile_ids, numpy.array([], dtype=numpy.float16)
            else:
                return profile_ids, numpy.array([], dtype=numpy.float32)
        else:
            return profile_ids, np_profile_vectors

    def get_profile_vectors_by_categories(self, categories):
        """
        Return a tuple with two elements: array of profile ids, array of profile vectors.
        :return: a tuple with two elements: array of profile ids with category data (python array), array of profile vectors (numpy array).
        ['01:image_id_1', '04:image_id_2'], ['vector1', 'vector2']
        Return empty arrays if no result is found.
        """
        profile_ids = []
        profile_vectors = []
        for k, v in self.redis.hscan_iter(VECTOR_HASH_NAME):
            try:
                # get the second part of the key (image id)
                vector = numpy.frombuffer(v, dtype=numpy.float32)
                cat_id, image_id = k.split(":")
                if cat_id in categories:
                    profile_ids.append(k)
                    profile_vectors.append(vector)
            except Exception as e:
                self.logger.error("failed to get vector for profile {0}, exception {1}".format(k, e))

        np_profile_vectors = numpy.asarray(profile_vectors, dtype=numpy.float32)
        # return empty python list, not np list if np list is empty
        if np_profile_vectors.size == 0:
            return profile_ids, numpy.array([], dtype=numpy.float32)
        else:
            return profile_ids, np_profile_vectors

    def get_all_profile_ids(self):
        """
        Return a full list of image ids from the profiles database.
        :return: a full list of image ids in the profiles database; empty array if there's none
        """
        return self.get_keys_by_hash_name(CATEGORY_HASH_NAME)

    def get_profile_ids_by_category(self, category_id):
        """
        Return a list of image ids that are associated with input category from the profile database
        :param category_id: the id of the category as a filter to query the image ids
        :type category_id: basestring
        :return: a list of image ids that are associated with input category from the profile database; empty array if there's none
        """
        results = []
        category_id = str(category_id)
        if not self.is_category_exists(category_id):
            self.logger.warning('Category does not exist: ' + category_id)
            return None

        # assume "profile:vector" hash table consists all images with vector info
        full_ids = self.redis.hkeys(VECTOR_HASH_NAME)
        for c_p in full_ids:
            if c_p.split(':')[0] == category_id:
                results.append(c_p.split(':')[1])
        return results

    ##############################################################
    ###### Data import functions ######
    ##############################################################

    def set_data_import_stats(self, status, count):
        """
        Update the processed stats for data import service, including the counts for success, fail, and total number of records.
        :param status: the key in the hash mapping: 'success', 'error', 'total'
        :type status: basestring
        :param count: the number of records being processed for the specified status
        :type count: int
        :return: True if set successfully, False if set failed.
        """
        status_list = [DB_IMPORT_ERROR, DB_IMPORT_SUCCESS, DB_IMPORT_TOTAL]
        if status not in status_list:
            self.logger.error('Failed to set data import stats, the input status does not exist: {0}'.format(status))
            raise IOError('Unrecognized input status value.')
        count = int(count)
        # create or update the count for status
        set_count = self.set_kv_to_hash(DATA_IMPORT_HASH_NAME, status, count)
        return set_count == 1 or set_count == 0

    def increment_data_import_stats(self, status, amount):
        """
        Increment the processed stats for data import service, including the counts for success and fail number of records.
        If key(status) does not exist the value is set to 0 before the operation is performed.
        :param status: the key in the hash mapping: 'success', 'error'
        :type status: basestring
        :param amount: the number to increment for the value of the key
        :type amount: int
        :return: The new value of the key
        """
        status_list = [DB_IMPORT_ERROR, DB_IMPORT_SUCCESS]
        if status not in status_list:
            self.logger.error('Failed to set data import stats, the input status does not exist: {0}'.format(status))
            raise IOError('Unrecognized input status value.')
        amount = int(amount)
        return self.increment_hash_kv(DATA_IMPORT_HASH_NAME, status, amount)

    def get_data_import_stats(self, status=None):
        """
        Get the stats for data import service.
        :param status Default to None.
        :type status basestring
        :return:
        - If input status is None: return a dictionary contains all status.
        i.e.  {"success": "0", "error": "0", "total": "0"}
        - If input status is in status list: return an integer represent the count of the input status.
        i.e. 3
        - If no result found for status that is in status_list, return 0.
        - If input status is not in status_list,
        """
        status_list = [DB_IMPORT_ERROR, DB_IMPORT_SUCCESS, DB_IMPORT_TOTAL]
        if not status:
            obj = self.get_all_by_hash_name(DATA_IMPORT_HASH_NAME)
            if not obj:
                self.logger.warning('Data import stats does not exist.')
                return None
            return obj
        if status and status in status_list:
            count = self.get_kv_by_hash_name(DATA_IMPORT_HASH_NAME, status)
            if not count:
                return 0
            return int(count)
        if status and status not in status_list:
            self.logger.error('Input status is not a part of the data import stats status: {0}'.format(status))
            raise IOError('Unrecognized input status value.')

    def set_db_import_status(self, task_id, hash_mapping):
        """
        Set db import service status.
        :param task_id: the id of the task to add to
        :type task_id: basestring or uuid
        :param hash_mapping: the status of db import service
        :type hash_mapping: dictionary
        :return: True if set successfully, False if set failed
        """
        status = self.set_mkv_to_hash(DATA_IMPORT_PREFIX + str(task_id), hash_mapping)
        return status == 1 or status == 0

    def get_all_db_import_task_id(self):
        """
        Get task id for all data import services.
        :return: A list of task id for data import services.
        """
        task_ids = []
        for keys in self.redis.scan_iter(match=DATA_IMPORT_PREFIX + '*'):
            import_key = keys.split(":")
            if len(import_key) == 2:
                task_ids.append(import_key[-1])
        return task_ids

    def get_import_tasks_by_category(self, category_id):
        """
        Get task id for all data import services for input category id.
        :param category_id: the id of the category to get import tasks.
        :return: A list of task id for data import services for input category id.
        """
        category_id = str(category_id)
        task_ids = []
        for keys in self.redis.scan_iter(match=DATA_IMPORT_PREFIX + '*'):
            import_key = keys.split(":")
            task_id = import_key[-1]
            if len(import_key) == 2 and self.get_kv_by_hash_name(DATA_IMPORT_PREFIX+task_id, 'category_id') == category_id:
                task_ids.append(task_id)
        return task_ids

    def add_import_failed_image(self, task_id, image_id, err_code):
        """
        add failed image id to the data import failed image list for a specific import task.
        i.e.  sorted set for pagination purpose
        {"data_import:<task_id_1>:failed_images": ["<fail_code>:<image_id_1>"(score), "<fail_code>:<image_id_3>"(score), "<fail_code>:<image_id_4>"(score)]}
        :param task_id: the id of the task to add failed image to
        :type task_id: basestring or uuid
        :param err_code: the error code of the failed image
        :type err_code: int, see :ERR_CODE
        :param score: the score for the set element
        :type score: float
        :return:
        """
        # generate a random float number between 0 and 1000
        random_score = random.uniform(0, 1000)
        task_id = str(task_id)
        image_id = str(image_id)
        err_code = str(err_code)
        failed_img_name = DATA_IMPORT_PREFIX + task_id + DATA_IMPORT_FAILED_SUFFIX
        self.add_to_sorted_set(failed_img_name, err_code + ':' + image_id, random_score)

    def get_import_failed_images(self, task_id, start, end, desc=False, withscores=False, score_cast_func=float):
        """
        Return a range of values from sorted set between ``start`` and ``end`` sorted in ascending order (default).
        :param task_id: the id of the task to get failed image from
        :param start: index, can be negative, indicating the start of the range.
        :param end: index, can be negative, indicating the end of the range.
        :param desc: a boolean indicating whether to sort the results descendingly
        :param withscores: indicates to return the scores along with the values. The return type is a list of (value, score) pairs
        :param score_cast_func: a callable used to cast the score return value
        :return: Empty list if there's no failed images; Otherwise, return a list of image ids with error code as prefix
        i.e.
        ['1:<image_id1>', '3:<image_id2>']
        """
        task_id = str(task_id)
        failed_img_name = DATA_IMPORT_PREFIX + task_id + DATA_IMPORT_FAILED_SUFFIX
        results = self.redis.zrange(failed_img_name, start, end, desc, withscores, score_cast_func)
        return results

    def get_redis_memory_usage(self):
        """
        :return: current memory usage in float, from 0 to 1.
        """
        info = self.redis.info()
        max_memory = info["maxmemory"]
        if max_memory == 0:
            raise Exception("maxmemory is zero!")
        used = info["used_memory"]
        return float(used)/max_memory

    def set_import_temp_fail(self, count):
        """
        set DB_IMPORT_TEMP_FAIL_PREFIX for unstructured import
        :param count: count to set to DB_IMPORT_TEMP_FAIL_PREFIX
        :return: True on success False on failure
        """
        return self.set_value_to_key(DB_IMPORT_TEMP_FAIL_PREFIX, count)

    def get_import_temp_fail(self):
        """
        get DB_IMPORT_TEMP_FAIL_PREFIX count for unstructured import
        :return: count
        """
        return self.get_value_by_key(DB_IMPORT_TEMP_FAIL_PREFIX)

    def set_migration_stats(self, status, count, usage='profile'):
        """
        Update the processed stats for data migration service, including the counts for success, fail, and total number of records.
        :param status: the key in the hash mapping: 'success', 'error', 'total'
        :type status: basestring
        :param count: the number of records being processed for the specified status
        :type count: int
        :param usage: either profile or target
        :type usage: basestring
        :return: True if set successfully, False if set failed.
        """
        status_list = [DB_IMPORT_ERROR, DB_IMPORT_SUCCESS, DB_IMPORT_TOTAL]
        if status not in status_list:
            self.logger.error('Failed to set data migration stats, the input status does not exist: {0}'.format(status))
            raise IOError('Unrecognized input status value.')
        count = int(count)
        # create or update the count for status
        if usage == 'profile':
            set_count = self.set_kv_to_hash(MIGRATION_PROFILE_HASH_NAME, status, count)
        else:
            set_count = self.set_kv_to_hash(MIGRATION_TARGET_HASH_NAME, status, count)
        return set_count == 1 or set_count == 0

    def increment_migration_stats(self, status, amount, usage='profile'):
        """
        Increment the processed stats for data migration service, including the counts for success and fail number of records.
        If key(status) does not exist the value is set to 0 before the operation is performed.
        :param status: the key in the hash mapping: 'success', 'error'
        :type status: basestring
        :param amount: the number to increment for the value of the key
        :type amount: int
        :param usage: either profile or target
        :type usage: basestring
        :return: The new value of the key
        """
        status_list = [DB_IMPORT_ERROR, DB_IMPORT_SUCCESS]
        if status not in status_list:
            self.logger.error('Failed to set data migration stats, the input status does not exist: {0}'.format(status))
            raise IOError('Unrecognized input status value.')
        amount = int(amount)
        if usage == 'profile':
            return self.increment_hash_kv(MIGRATION_PROFILE_HASH_NAME, status, amount)
        else:
            return self.increment_hash_kv(MIGRATION_TARGET_HASH_NAME, status, amount)

    def get_migration_stats(self, usage='profile'):
        """
        Get the stats for data migration service.
        :param status Default to None.
        :type status basestring
        :param usage: either profile or target
        :type usage: basestring
        :return: a dictionary contains all status.
        i.e.  {"success": "0", "error": "0", "total": "0"}
        None if no data.
        """
        if usage == 'profile':
            obj = self.get_all_by_hash_name(MIGRATION_PROFILE_HASH_NAME)
        else:
            obj = self.get_all_by_hash_name(MIGRATION_TARGET_HASH_NAME)

        if not obj:
            self.logger.warning('Data import stats does not exist.')
            return None
        return obj
