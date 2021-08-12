from datetime import datetime
from srelib.tsdb.client import QueryRateOptions

class TSDBGraph(object):
    """ Used to create TSDB URLs for a TSDBRequest or TSDBQuery.
    One can also just use metric and tag-values in order to create
    a URL.
    """
    def __init__(self, start_time=None, end_time=None):
        """
        Args:
            start_time(String): %Y/%m/%d-%H:%M:%S format
            end_time(String): %Y/%m/%d-%H:%M:%S format
        """
        #TODO:Retrieve via settings module.
        self.endpoint = "tsdb2.dc.dotomi.net"
        self.endpoint_path = "/api/query?"
        self.start_time = start_time
        self.end_time = end_time
        self.query_list = []
        self.is_one_graph = False
        self.one_graph_tag_list = []
        
    def set_one_graph(self, is_one_graph, one_graph_tag_list):
        """ Sets if the graph url created will be on multiple tabs.
        
        Args:
            is_one_graph (bool): True if the graph should be created with one tab.
            one_graph_tag_list (List(String)):  The tag names for the value that should be concatenated in
            the one graph.
        Returns:
            None
        """
        self.is_one_graph = is_one_graph
        self.one_graph_tag_list = one_graph_tag_list
        
    def add_query(self, metric, tag_dictionary, is_rate, drop_resets):
        """ Adds a query to the graph using the provided parameters.
        
        Call get_url() in order to obtain the url associated with 
        queries added by this method.
        
        Please note that currently this is only supporting the "sum" aggregation.
        
        Args:
            metric (String): The metric that should be graphed.
            tag_dictionary (Dictionary): The tag-values that should be graphed with
            the given metric.
            is_rate(Boolean): True if the graph is a rate graph. False if the graph is
            a count graph.
        Returns:
            None
        """
        self.query_list.append(GraphQuery(metric, tag_dictionary, "sum", is_rate, drop_resets))
    
    @staticmethod
    def get_url_for_tsdb_request(tsdb_request_obj, one_graph_tag_list=None):
        """ Returns a url that includes all quries in the TSDBRequest object.
        Args:
            tsdb_request_obj (TSDBRequest):  The request object that contains the 
            queries.
            one_graph_tag_list (List(String)):  The tag names for the value that should be concatenated in
            the one graph.
        Returns:
            A URL that contains all the queries configured in the request.
        """
        return TSDBGraph.get_url_for_tsdb_queries(tsdb_request_obj, tsdb_request_obj.get_queries(), one_graph_tag_list)
        
    @staticmethod
    def get_url_for_tsdb_queries(tsdb_request_obj, tsdb_query_obj_list, one_graph_tag_list):
        """ Returns a url that uses the TSDBQuery objects in tsdb_query_obj_list.
            The tsdb_request_obj is required in order to obtain rate, aggregation, etc
            information.
            
        Args:
            tsdb_request_obj (TSDBRequest): The request object.
            tsdb_query_obj_list (list): The list of TSDBQuery objects.
            one_graph_tag_list (List(String)):  The tag names for the value that should be concatenated in
            the one graph.
            
        Returns:
            A URL that contains all the queries in tsdb_query_obj_list.
        """
        start_time = datetime.utcfromtimestamp(tsdb_request_obj.get_start_time())
        end_time = datetime.utcfromtimestamp(tsdb_request_obj.get_end_time())
        
        request_url_list =[]
        request_url_list.append("http://")
        #todo: obtain these values from settings 
        request_url_list.append("tsdb2.dc.dotomi.net")
        request_url_list.append("/#")
        
        request_url_list.append(
            TSDBGraph._create_start_date_string(None, start_time.strftime("%Y/%m/%d-%H:%M:%S"))
        )
        request_url_list.append(
            TSDBGraph._create_end_date_string(None, end_time.strftime("%Y/%m/%d-%H:%M:%S"))
        )
        
        query_str_list = []
        has_all_rate = True
        if((one_graph_tag_list is not None) and (len(one_graph_tag_list) > 0)):
            metric = None
            agg_type = None
            is_rate = None
            agg_tags = {}
            last_tag_list = []
            last_dict = {}
            #will not support not grouped for now.
            for query in tsdb_query_obj_list:
                grouped_tags_list = query.get_grouped_by_tag_names()
                last_tag_list = grouped_tags_list
                total_grouped = len(grouped_tags_list)
                
                
                metric = query.get_metric()
                agg_type = query.get_aggregation().get_aggregation_value()
                is_rate = query.get_is_rate()
                
                for tag in grouped_tags_list:
                    last_dict[tag] = query.get_tag_value(tag)
                    if(tag in one_graph_tag_list):
                        if(tag not in agg_tags):
                            agg_tags[tag] = []
                        agg_tags[tag].append(query.get_tag_value(tag))
            
            grouped_str = TSDBGraph._create_tag_value_str_with_aggs(None, last_tag_list, last_dict, agg_tags)
            tag_query_str = "%7B{}%7D".format(grouped_str)
            metric_str = TSDBGraph._create_metric_string(None, metric, agg_type, is_rate, query.get_rate_options())
            complete_query_str = "{}{}".format(metric_str, tag_query_str)
            query_str_list.append(complete_query_str)

        else:
            for query in tsdb_query_obj_list:
                #This part of the code is used to create url strings.
                #Each iteration will create a string like the following
                #&m=sum:rate:bsy.requests%7Bserver_id=4518,endpoint=fetch.rosetta.app.banner.jsonp.current%7Cfetch.jac.app.banner.jsonp.current%7Cfetch.ron.app.banner.jsonp.current%7Cfetch.html5.player.video.vast.current%7D
                #setup the tag value query
                grouped_tags_list = query.get_grouped_by_tag_names()
                not_grouped_tags_list = query.get_not_grouped_by_tag_names()
                tag_query_str = ""
                total_grouped = len(grouped_tags_list)
                grouped_str = TSDBGraph._create_tag_value_str_objs(None, grouped_tags_list, query)
                total_not_grouped = len(not_grouped_tags_list)
                not_grouped_str = TSDBGraph._create_tag_value_str_objs(None, not_grouped_tags_list, query)
                if((total_grouped > 0) and (total_not_grouped > 0)):
                    tag_query_str = "%7B{}%7D%7B{}%7D".format(grouped_str,not_grouped_str)
                elif(total_grouped > 0):
                    tag_query_str = "%7B{}%7D".format(grouped_str)
                elif(total_not_grouped > 0):
                    tag_query_str = "%7B%7D%7B{}%7D".format(grouped_str)
                
                #setup the metric 
                metric = query.get_metric()
                agg = query.get_aggregation().get_aggregation_value()
                is_rate = query.get_is_rate()
                if(is_rate == False):
                    has_all_rate = False
                
                
                metric_str = TSDBGraph._create_metric_string(None, metric,agg,is_rate, query.get_rate_options())
                complete_query_str = "{}{}".format(metric_str,tag_query_str)
                query_str_list.append(complete_query_str)
        #&o=&yrange=%5B0:%5D&wxh=1900x754&style=linespoint
        if(has_all_rate == True):
            query_str_list.append("&o=&yrange=%5B0:%5D&wxh=1900x754&style=linespoint")
        else:
            query_str_list.append("&o=&wxh=1900x754&style=linespoint")
        request_url_list.append("".join(query_str_list))
        request_url = "".join(request_url_list)
        
        return request_url
         
    def get_url(self):
        """ Used to create the url when the queries were added using the add_query method.
        
        Returns:
            A URL that contains all the queries configured by the add_query method.
        """
        request_url_list =[]
        request_url_list.append("http://")
        request_url_list.append(self.endpoint)
        request_url_list.append(self.endpoint_path)
        request_url_list.append(
            self._create_start_date_string(self.start_time)
        )
        request_url_list.append(
            self._create_end_date_string(self.end_time)
        )
        
        query_str_list = []
        if(self.is_one_graph):
            #assuming all the tags are the same except for 
            #the ones that will be aggregated.
            metric = None
            agg_type = None
            is_rate = None
            agg_tags = {}
            last_tag_dict = {}
            has_drop_resets = False
            for query in self.query_list:
                metric = query.get_metric()
                tag_dictionary = query.get_tag_dictionary()
                last_tag_dict = tag_dictionary
                agg_type = query.get_aggregation()
                is_rate = query.get_is_rate()
                has_drop_resets = query.get_drop_resets()
                print("has drop resets = {}".format(has_drop_resets))
                for tag in self.one_graph_tag_list:
                    if(tag in tag_dictionary):
                        if(tag not in agg_tags):
                            agg_tags[tag] = []
                        agg_tags[tag].append(tag_dictionary[tag])
                        
            #at this point the aggregated data is agg_tags dictionary
            tag_name_list = list(last_tag_dict.keys())
            grouped_str = self._create_tag_value_str_with_aggs(tag_name_list, last_tag_dict, agg_tags)
            tag_query_str = "%7B{}%7D".format(grouped_str)
            rate_options = QueryRateOptions()
            if(has_drop_resets == True):
                print("setting drop resets")
                rate_options.set_is_drop_resets(True)
            metric_str = self._create_metric_string(metric, agg_type, is_rate, rate_options)
            complete_query_str = "{}{}".format(metric_str, tag_query_str)
            request_url_list.append(complete_query_str)
            request_url_list.append("&o=&yrange=%5B0:%5D&wxh=1900x754&style=linespoint")
            request_url = "".join(request_url_list)
           
            return request_url
        
        
        query_str_list = []
        for query in self.query_list:
            metric = query.get_metric()
            tag_dictionary = query.get_tag_dictionary()
            agg_type = query.get_aggregation()
            is_rate = query.get_is_rate()
            has_drop_resets = query.get_drop_resets()
            
            tag_name_list = list(tag_dictionary.keys())
            grouped_str = self._create_tag_value_str(tag_name_list, tag_dictionary)
            tag_query_str = "%7B{}%7D".format(grouped_str)
            
            rate_options = QueryRateOptions()
            if(has_drop_resets == True):
                print("setting drop resets")
                rate_options.set_is_drop_resets(True)

            metric_str = self._create_metric_string(metric, agg_type, is_rate, rate_options)
            complete_query_str = "{}{}".format(metric_str, tag_query_str)
            query_str_list.append(complete_query_str)
        
        request_url_list.append("".join(query_str_list))
        request_url_list.append("&o=&yrange=%5B0:%5D&wxh=1900x754&style=linespoint")
        request_url = "".join(request_url_list)
        return request_url
        
    def _create_tag_value_str_objs(self, tag_names_list, tsdb_query_obj):
        """ Creates the tag value string for the url.
        Args:
            tag_names_list(List): A list of tag names.
            tsdb_query_obj(TSDBQuery): The query object.
        Returns:
            String: String containing the key values used to filter a graph.
        """
        kv_list = []
        for name in tag_names_list:
            val = tsdb_query_obj.get_tag_value(name)
            val_update = val.replace("|","%7C")
            kv_list.append(name+"="+val_update)
        return ",".join(kv_list)    
        
    def _create_tag_value_str(self, tag_names_list, tag_dictionary):
        """ Creates the tag value string for the url.
        Args:
            tag_names_list(List): A list of tag names.
            tag_dictionary(Dictionary): A dictionary containing tag name and values.
        Returns:
            String: String containing the key values used to filter a graph.
        """
        kv_list = []
        for name in tag_names_list:
            val = tag_dictionary[name]
            val_update = val.replace("|","%7C")
            kv_list.append(name+"="+val_update)
        return ",".join(kv_list)
          
    def _create_tag_value_str_with_aggs(self, tag_name_list, share_tags_dict, agg_tags_dict):
        """
        Args:
            tag_name_list(List): A list of strings.  These are key names to include in 
            the result string.
            share_tags_dict(Dictionary): A dictionary containg tags that have one key to one value.
            agg_tags_dict(Dictionary): A dictionary containing tags that have aggregated "or"
            values.
        Returns:
            String: String containing the key values used to filter a graph.
        """
        tag_value_list = []
        for tag in tag_name_list:
            tag_value = None
            if(tag in agg_tags_dict):
                value_list = agg_tags_dict[tag]
                value_str = "%7C".join(value_list)
                tag_value = "{}={}".format(tag,value_str)
            else:
                tag_value = "{}={}".format(tag, share_tags_dict[tag])
            tag_value_list.append(tag_value)
            
        return ",".join(tag_value_list)    
            
    def _create_start_date_string(self, start):
        """ Helper function for url string used to query TSDB
        Args:
            start(String): Date string.
        Returns:
            String: The string containg the start date key and value.
        """
        return "start={}".format(start)

    def _create_end_date_string(self, end):
        """ Helper function for url string used to query TSDB
        Args:
            end(String): Date string.
        Returns:
            String: The string containg the end date key and value.
        """
        return "&end={}".format(end)
        
    def _create_metric_string(self, metric, agg, is_rate, rate_options_obj=None):
        """ Helper function for url string used to query TSDB
        Args:
            metric(String): The metric
            agg(String): The aggregation method to be used.
            is_rate(Boolean): If True then obtain rate. If false then obtain count.
            rate_option_obj(QueryRateOptions) : Rate option configuration.
        Return:
            String: The metric configuration string.
        """
        return_str_list = []
        if((agg is None) or (agg == "")):
            agg = "sum"
        return_str_list.append(agg)
        if(is_rate):
            if(rate_options_obj is None):
                return_str_list.append("rate")
            else:
                rate_options_str = ""
                if(rate_options_obj.get_is_drop_resets() == True):
                    rate_options_str = "rate%7Bdropcounter,,0%7D"
                elif(rate_options_obj.get_is_counter()):
                    max_value = rate_options_obj.get_counter_max()
                    reset_value = rate_options_obj.get_reset_value()
                    rate_options_str = "rate%7Bcounter,{},{}%7D".format(max_value,reset_value)
                    return_str_list.append(rate_options_str)
                else:
                    pass
                return_str_list.append(rate_options_str)
        return_str_list.append(metric)
        return  "&m=" + ":".join(return_str_list)

class GraphQuery(object):
    """Used internally to hold metric-tag information for the graph.  
    """
    
    def __init__(self, metric, tag_dictionary, agg_value="sum", is_rate=True, drop_resets=False):
        """
        Args:
            metric(String): The metric
            tag_dictionary(Dictionary): Contains the tag and tag values.
            agg_value(String): The aggregation method to be used.
            is_rate(Boolean): If True then obtain rate. If false then obtain count.
        """
        self.metric = metric
        self.tag_dictionary = tag_dictionary
        self.agg_value = agg_value
        self.is_rate = is_rate
        self.drop_resets = drop_resets
        
    def get_metric(self):
        """
        Returns:
            String: The metric
        """
        return self.metric
        
    def get_tag_dictionary(self):
        """
        Returns:
            Dictionary: The tag and tag values
        """
        return self.tag_dictionary
        
    def get_aggregation(self):
        """
        Returns:
            String: The aggregation type.
        """
        return self.agg_value
        
    def get_is_rate(self):
        """
        Returns:
            Boolean: True if rate information.  False if count information.
        """
        return self.is_rate

    def get_drop_resets(self):
        return self.drop_resets
        
def main():
    tsdb_graph = TSDBGraph("2019/01/23-10:58:00","2019/01/23-11:08:49")
    tsdb_graph.add_query("rtb.requests",
        {
            "server_id":"1469",
            "response_type":"TIMEOUT"
        },
        True
    )
    tsdb_graph.add_query("rtb.requests",
        {
            "server_id":"1470",
            "response_type":"TIMEOUT"
        },
        True
    )
    tsdb_graph.set_one_graph(True,["server_id"])
    url = tsdb_graph.get_url()
    print(url)
    
if __name__ == '__main__':
    main()