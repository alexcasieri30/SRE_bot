class JsonDictionaryConfiguration(object):

    def __init__(self, json_dict):
        self.json_dict = json_dict

    def get_value(self, key_path_list):
        """ Returns the value described by the keys
        in key_path_list.  Returns None if key path
        is not valid.
        Args:
            key_path_list(list): The keys to get to target
            value.
        Returns:
            obj: The value can be any vaid JSON value.  None
            if the key path is invalid.
        """
        if(type(key_path_list) != list):
            raise ValueError("key_path_list must be a list")
        temp_value = self.json_dict
        for key in key_path_list:
            if(key in temp_value):
                temp_value = temp_value[key]
            else:
                return None
        return temp_value

    def get_json(self):
        return self.json_dict