import json
import traceback
import http.client
import logging


#http://opentsdb.net/docs/build/html/api_http/query/index.html
class TSDBClient(object):
    """ This is used to send a request to TSDB.
    
        Query configuration is not done with this object.  This
        object uses data configured in a TSDBRequest object
        to form the proper request.
        
        Please view opentsdb documentation for more information on the meaning
        of fields:
        http://opentsdb.net/docs/build/html/api_http/query/index.html
        
        Not all configuration points are supported.
    """
    logger = logging.getLogger(__name__)
    MAX_QUERY_URL_LENGTH = 3600
    def __init__(self): 
        #will be retrieved via settings module.
        #self.endpoint = "dtord01hts02p.dc.dotomi.net"
        self.endpoint = "tsdb2.dc.dotomi.net"
        self.endpoint_path = "/api/query?"
        self.timeout = 60 * 3
        
    def execute_request(self, tsdb_request_obj):
        """ Uses data in TSDBRequest object to send request to TSDB.
            
        No checks are currently done or planned to ensure that 
        request has been properly configured.
        
        Args:
            tsdb_request_obj (TSDBRequest): The request object containing the queries to perform.
            
        Returns:  List of QueryResponse objects. A single request can result in 1+ response
        objects.
        """
        query_list = tsdb_request_obj.get_queries()
        start_time = tsdb_request_obj.get_start_time()
        end_time = tsdb_request_obj.get_end_time()
        
        #each query may have 1+ results if they have "or" values
        #keep track of the keys that will help return the proper results
        #to the caller.
        temp_client_query_results = []

        #list holds the different components of the query that will
        #be made to TSDB
        query_str_list = []

        #used to hold the different strings that will make up
        #the query url
        request_url_list =[]
        request_url_length = 0
        request_url_list.append(self.endpoint_path)
        start_time_str = self._create_start_date_string(start_time)
        request_url_list.append(
            start_time_str
        )
        end_time_str = self._create_end_date_string(end_time)
        request_url_list.append(
            end_time_str
        )
        request_url_length = len(self.endpoint_path)
        request_url_length += len(start_time_str)
        request_url_length += len(end_time_str)

        total_queries = 0
        self.logger.debug("The total number of queries in request {}".format(len(query_list)))
        for query in query_list:
            #This part of the code is used to create url strings.
            #Each iteration will create a string like the following
            #&m=sum:rate:bsy.requests%7Bserver_id=4518,endpoint=fetch.rosetta.app.banner.jsonp.current%7Cfetch.jac.app.banner.jsonp.current%7Cfetch.ron.app.banner.jsonp.current%7Cfetch.html5.player.video.vast.current%7D
            #setup the tag value query
            grouped_tags_list = query.get_grouped_by_tag_names()
            not_grouped_tags_list = query.get_not_grouped_by_tag_names()
            tag_query_str = ""
            total_grouped = len(grouped_tags_list)
            grouped_str = self._create_tag_value_str(grouped_tags_list, query)
            total_not_grouped = len(not_grouped_tags_list)
            not_grouped_str = self._create_tag_value_str(not_grouped_tags_list, query)
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
            
            metric_str = self._create_metric_string(metric,agg,is_rate, query.get_rate_options())
            complete_query_str = "{}{}".format(metric_str,tag_query_str)

            if( (len(complete_query_str) + request_url_length) > TSDBClient.MAX_QUERY_URL_LENGTH):
                #exceeded url length
                #need to run query.
                self.logger.debug("Need to run query due to MAX url length.")
                request_url_list.append("".join(query_str_list))
                request_url = "".join(request_url_list)
                #if(tsdb_request_obj.get_show_query() == True):
                #in order to correlate query to query results show query
                #must always be set to true.
                self.logger.debug("Making a tsdb query request with {} queries".format(total_queries))
                json_data = self._make_tsdb_request(request_url)
                self.logger.debug("Query request completed")
                #self.logger.debug (json.dumps(json_data, indent=4))
                self._process_tsdb_results(temp_client_query_results, json_data)

                #re-init the tsdb url specific bookkeeping
                query_str_list = []
                request_url_list =[]
                request_url_length = 0
                request_url_list.append(self.endpoint_path)
                start_time_str = self._create_start_date_string(start_time)
                request_url_list.append(
                    start_time_str
                )
                end_time_str = self._create_end_date_string(end_time)
                request_url_list.append(
                    end_time_str
                )
                request_url_length = len(self.endpoint_path)
                request_url_length += len(start_time_str)
                request_url_length += len(end_time_str)

                #Now add the query that put everything over the edge.
                request_url_length += len(complete_query_str)
                query_str_list.append(complete_query_str)
                #done for bookeeping of query to 1 to many query results.
                tag_value_dict = query.get_tag_values()
                #This bookkeeping is done prior to executing the query.
                self._add_call_result(temp_client_query_results, metric, tag_value_dict, is_rate)
                total_queries = 1

            else:
                request_url_length += len(complete_query_str)
                query_str_list.append(complete_query_str)
                #done for bookeeping of query to 1 to many query results.
                tag_value_dict = query.get_tag_values()
                #This bookkeeping is done prior to executing the query.
                self._add_call_result(temp_client_query_results, metric, tag_value_dict, is_rate)
                total_queries += 1
        
        #more than likely there is a need to run the query at this point.
        if(len(query_str_list) > 0):
            request_url_list.append("".join(query_str_list))
            request_url = "".join(request_url_list)
            self.logger.debug("Making a tsdb query request with {} queries".format(total_queries))
            json_data = self._make_tsdb_request(request_url)
            self.logger.debug("Query request completed")
            #self.logger.debug(json.dumps(json_data, indent=4))
            self._process_tsdb_results(temp_client_query_results, json_data)

        return_list = []
        for bookeeping_dict in temp_client_query_results:
            parent_result = bookeeping_dict["resp_obj"]
            return_list.append(parent_result)
    
        self.logger.debug("Completed the query request")
        return return_list

    def _process_tsdb_results(self, temp_client_query_results, json_data):
        """ Process the results returned from a TSDB request.
        Args:
            temp_client_query_results (List): internal dictionary list containing book keeping data.
            json_data(Dictionary) : The JSON query results.
        """
        for result_dict in json_data:
            metric = result_dict["metric"]
            tags_dict = result_dict["tags"]
            data_dict = result_dict["dps"]
            filter_list = result_dict["query"]["filters"]
            is_rate = result_dict["query"]["rate"]
            key_dict = {}
            for filter_dict in filter_list:
                tag_name = filter_dict["tagk"]
                tag_value = filter_dict["filter"]
                key_dict[tag_name] = tag_value
                
            #Find parent query object.
            query_resp_obj = self._get_call_result_obj(temp_client_query_results, metric, key_dict, is_rate)
            if(query_resp_obj is None):
                self.logger.error("Something very wrong, no query for this result")
                
            #now add the result of the query to the parent.
            #that data is found in the tags section of the result.
            #the tag names are important here.
            tag_name_list = list(key_dict.keys())
            child_query_tags_dict = {}
            for tag_name in tag_name_list:
                child_query_tags_dict[tag_name] = tags_dict[tag_name]
                
            ts = TimeSeriesData(data_dict)
            sub_resp = QuerySubResponse(metric, child_query_tags_dict, ts, is_rate)
            query_resp_obj.add_query_response(sub_resp)

    def _make_tsdb_request(self, request_url):
        request_url = request_url + "&show_query=true"
        conn = http.client.HTTPConnection(self.endpoint,timeout=self.timeout)
        conn.request("GET", request_url)
        r1 = conn.getresponse()
        data1 = r1.read().decode("utf-8")
        json_data = json.loads(data1)
        conn.close()
        
        #check for errors
        if("error" in json_data):
            error_message = json_data["error"]["message"]
            self.logger.error("Issue found in tsdb response = {}".format(error_message))
            raise TSDBError(error_message)
        return json_data

    def _create_tag_value_str(self, tag_names_list, tsdb_query_obj):
        kv_list = []
        for name in tag_names_list:
            val = tsdb_query_obj.get_tag_value(name)
            val_update = val.replace("|","%7C")
            kv_list.append(name+"="+val_update)
        return ",".join(kv_list)
                
    def _create_start_date_string(self, start):
        """ Helper function for url string used to query TSDB"""
        return "start={}".format(start)

    def _create_end_date_string(self, start):
        """ Helper function for url string used to query TSDB"""
        return "&end={}".format(start)
        
    def _create_metric_string(self, metric, agg, is_rate, rate_options_obj=None):
        """ Helper function for url string used to query TSDB"""
        
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
                    rate_options_str = "rate%7Bdropcounter%7D"
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
    
    def _add_call_result(self, temp_client_result_list, metric, tag_dictionary, is_rate):
        """  Used for bookeeping of queries submitted by client.  This should be done
            prior to executing the query.  The temp_client_result_list will be
            updated with a bookkeeping dictionary if a bookkeeping object is not
            available for the metric, tag_dictionary, is_rate combination.

            Holds the query paremeters in dictionary and the QueryResponse object
            that will be returned to client.
        Args:
            temp_client_result_list(List): A list of bookkeeping dictionaries.
            metric(str): The metric.
            tag_dictionary(dictionary): The tag value dictionary.
            is_rate(bool): If true, the query is for rate information.  If False, the
            query is for count information.
        Returns:
            QueryResponse: A new QueryResponse object if this MTC is not currently
            being bookkept. The existing QueryResponse object if the MTC is being
            bookkept.
        """
        result_obj = self._get_call_result_obj(temp_client_result_list, metric, tag_dictionary, is_rate)
        if(result_obj is None): 
            result_obj = QueryResponse(metric, tag_dictionary, is_rate)
            key_dict = {
                "metric":metric,
                "tags":tag_dictionary,
                "rate":is_rate
            }
            bookeeping_dict = {
                "key_dict": key_dict,
                "resp_obj": result_obj
            }
            temp_client_result_list.append(bookeeping_dict)
            
        return result_obj
    
    def _get_call_result_obj(self, temp_client_result_list, metric, tag_dictionary, is_rate):
        """ Get the QueryResponse object given the parameters. 
        Args:
            temp_client_query_results (List): internal dictionary list containing book keeping data.
            metric (str): The metric.
            tag_dictionary (dictionary): The tag name and value dictionary.
            is_rate(bool):  Pass in True if the query was for rate.
        Returns:
            QueryResponse: The response object for the given parameters.  None if
            one doesn't exist for the MTC
        """
        for bookeeping_dict in temp_client_result_list:
            stored_metric = bookeeping_dict["key_dict"]["metric"]
            stored_tags = bookeeping_dict["key_dict"]["tags"]
            stored_is_rate = bookeeping_dict["key_dict"]["rate"]
            if(stored_metric == metric):
                if(stored_tags == tag_dictionary):
                    if(stored_is_rate == is_rate):
                        return bookeeping_dict["resp_obj"]
        return None
 
class TSDBError(Exception):

    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.tsdb_message = message

    def get_tsdb_message(self):
        return self.tsdb_message
 
class TSDBQuery(object):
    """ Used to configure metric, tagk - tagv, aggregation,
        downsample and rate.
        
        One or more of these objects need to be added to
        a TSDBRequest object.
    """
    
    def __init__(self):
        self.tag_values = {
            "gb":{},
            "ngb":{}
        }
        self.metric = ""
        self.is_rate = True
        self.rate_options = None
        self.aggregation_object = QueryAggregator()
        self.downsample = None
    
    def add_tag_value(self, tag, value, group_by=True):
        """ Add a tag name and value to the query.
        
        Args:
            tag (str): The name of the tag
            value (str): The value for the tag.
            group_by(bool):  True if this tag-value should be grouped with other tag-values.
            
        Returns:
            None
        
        """
        if(group_by == True):
            self.tag_values["gb"][tag] = value
        else:
            self.tag_values["ngb"][tag] = value
                   
    def get_tag_values(self):
        """ Returns a copy of the internal tag-value dictionary that contains
        grouped and ungrouped tag-values.
        
        Returns:
            dictionary: Key "gb" in dictionary contains grouped tag values.
            Key "ngb" in dictionary contains ungrouped tag-values.
        """
        temp_dict = {}
        temp_dict.update(self.tag_values["gb"])
        temp_dict.update(self.tag_values["ngb"])
        return temp_dict
        
    def get_key_representation_dict(self):
        """ Obtain a dictionary that contains metric, tag and rate settings for
        this query.
        
        Returns:
            dictionary: Containing all important query settings. Keys are "metric", "tags", and "rate"
        """
        return {
            "metric":self.metric,
            "tags":self.get_tag_values(),
            "rate":self.is_rate
        }
                        
    def get_grouped_by_tag_names(self):
        """ Returns the tag names that are grouped.
        
        Returns:
            list: A list of names.
        """
        return list(self.tag_values["gb"].keys())
        
    def get_not_grouped_by_tag_names(self):
        """ Returns the tag names that are not grouped.
        
        Returns:
            list: A list of names.
        """
        return list(self.tag_values["ngb"].keys())
        
    def get_tag_value(self, name):
        """ Returns the tag names that are not grouped.
        Args:
            name (str): The tag name.
        Returns:
            string: The value for the tag or None if tag name not found.
        """
        val = self._get_tag_value(name,True)
        if(val == None):
            val = self._get_tag_value(name,False)
        return val

    def get_tag_dictionary(self):
        temp_dict = {}
        for key,val in self.tag_values["gb"].items():
            temp_dict[key] = val
        
        for key,val in self.tag_values["ngb"].items():
            temp_dict[key] = val
        return temp_dict
        
    def _get_tag_value(self, name, group_by):
        temp_dict = None
        return_val = None
        if(group_by == True):
            temp_dict = self.tag_values["gb"]
        else:
            temp_dict = self.tag_values["ngb"]
        
        if(name in temp_dict):
            return_val = temp_dict[name]
        
        return return_val
        
    def set_metric(self, metric):
        """ Set the metric for the query.
        
        Args:
            metric (str): The metric for the query.
        Returns:
            None
        """
        self.metric = metric
        
    def get_metric(self):
        """  Returns the metric for this query.
        
        Returns:
            string: The metric for this query.
        """
        return self.metric
        
    def set_is_rate(self, is_rate):
        """Sets if the query is for rate information.
        Args:
            is_rate(bool): True if the query is a rate query.  False if the 
            query is a count query.
        Returns:
            None
        """
        self.is_rate = is_rate
        
    def get_is_rate(self):
        """ Returns is rate value.
        Returns:
            bool: True if the query is for rate information.  False if
            query is for count information.
        """
        return self.is_rate
        
    def set_aggregation(self, aggregation_object):
        """  Set the type of aggregation for the query.
        Args:
            aggregation_object(QueryAggregator): The object containing the aggregation 
            configuration.
        Returns:
            None
        """ 
        self.aggregation_object = aggregation_object
        
    def get_aggregation(self):
        """Returns the QueryAggregator object used to configure aggregation.
        Returns:
            QueryAggregator: Object used to configure aggregation
        """
        return self.aggregation_object
           
    def set_rate_options(self, rate_options_object):
        """Configure the rate options for the query.
        Args:
            rate_options_object (QueryRateOptions): The object containing
            the configuration for the rate.
        Returns:
            None
        """
        self.rate_options = rate_options_object
        
    def get_rate_options(self):
        """Get the rate options for the query. 
        Returns:
            QueryRateOptions: The object containing
            the configuration for the rate.
        """
        return self.rate_options
        
    def __str__(self):
        return "TSDBQuery: metric={}, tags={}, is_rate={}".format(self.metric, self.tag_values, self.is_rate)
            
    def __repr__(self):
        return self.__str__()
        
class QueryRateOptions(object):
    """Query rate options as defined here: http://opentsdb.net/docs/build/html/api_http/query/index.html#rate-options
        
    """
    counter_max_max_value = 9223372036854775807
    def __init__(self):
        self.counter = False
        self.counter_max = ""
        self.reset_value = None
        self.drop_resets = False
        
    def set_is_counter(self, is_counter):
        """
        Args:
            is_counter(Boolean): Set is counter.
        Returns:
            None
        """
        self.counter = is_counter
    
    def get_is_counter(self):
        """
        Returns:
            Boolean: is counter value.
        """
        return self.counter
        
    def set_counter_max(self, value):
        """
        Args:
            value(int): The max counter value.
        Returns:
            None
        """
        self.counter_max = value
        
    def get_counter_max(self):
        """
        Returns:
            int: The max counter value.
        """
        return self.counter_max
        
    def set_reset_value(self, value):
        """
        Args:
            value(int): The reset value.
        Returns:
            None
        """
        self.reset_value = value
        
    def get_reset_value(self):
        """
        Returns:
            int: The reset value.
        """
        return self.reset_value
        
    def set_is_drop_resets(self, is_drop):
        """
        Args:
            is_drop(Boolean): The drop resets value.
        Returns:
            None
        """
        self.drop_resets = is_drop
        
    def get_is_drop_resets(self):
        """
        Returns:
            Boolean: The drop resets value.
        """
        return self.drop_resets

class QueryAggregator(object):
    """ Used to configure the query aggregation.
    
    http://opentsdb.net/docs/build/html/api_http/aggregators.html
    
    The valid aggregators are hard coded.  Values were obtained from a call to: http://tsdb.dc.dotomi.net/api/aggregators
    This list will need to be updated if supported aggregators is modified.
    """
    logger = logging.getLogger(__name__)
    valid_values = [
      "mimmin",
      "ep95r3",
      "p999",
      "count",
      "dev",
      "ep95r7",
      "sum",
      "ep90r3",
      "ep90r7",
      "avg",
      "min",
      "ep50r7",
      "max",
      "mimmax",
      "p99",
      "ep99r7",
      "ep999r7",
      "ep50r3",
      "ep999r3",
      "ep75r3",
      "p90",
      "ep75r7",
      "p50",
      "p75",
      "p95",
      "ep99r3",
      "zimsum"
    ]
    
    def __init__(self, value="sum"):
        if(value not in self.valid_values):
            self.logger.warning("Invalid aggregation value {}, setting to \"sum\"".format(value))
            self.aggregator_value = "sum"
        else:
            self.aggregator_value = value
        
    def get_aggregation_value(self):
        """ Returns the aggregation value string.
        Returns:
            String: The aggregation value.
        """
        return self.aggregator_value
        
class TSDBRequest(object):
    """  Used to configure complete request that will be
        made to TSDB.
        
    Multiple TSDBQuery objects can be added to this object in order 
    to perform multiple queries in one network request.
    
    Defintions for request settings can be found here: http://opentsdb.net/docs/build/html/api_http/query/index.html#requests
    
    """
    def __init__(self):
        self.start_time = ""
        self.end_time = ""
        self.query_list = []
        #False are the default values
        self.no_annotations = False
        self.global_annotations = False
        self.ms_resolution = False
        self.show_tsuids = False
        self.show_summary = False
        self.show_stats = False
        self.show_query = True
        
    
    def set_start_time(self, start_time):
        """ Set the start time for all the queries in this
        request.
        
        Args:
            start_time (int): The start time in seconds after epoch
        Returns:
            None
        """
        self.start_time = start_time
        
    def get_start_time(self):
        """Returns the start time for this request.
        
        Returns:
            int: Start time in epoch
        """
        return self.start_time
        
    def set_end_time(self, end_time):
        """ Set the ent time for all the queries in this
        request.
        
        Args:
            start_time (str): The ent time in seconds after epoch
        Returns:
            None
        """
        self.end_time = end_time
        
    def get_end_time(self):
        """Returns the end time for this request.
        
        Returns:
            int: End time in epoch
        """
        return self.end_time
        
    def add_query(self, tsdb_query_object):
        """ Add a query to the request. One or more queries
            can be added to this object.
        Args:
            tsdb_query_obj (TSDBQuery): The query that should
            be added to the request.
        Returns:
            None
        """
        self.query_list.append(tsdb_query_object)
        
    def get_queries(self):
        """ Get all queries configured in this request.
        Returns:
            List: A list of TSDBQuery objects.
        """
        return self.query_list
        
    def set_no_annotations(self, value):
        self.no_annotations = value
        
    def get_no_annotations_value(self):
        return self.no_annotations
        
    def set_global_annotations(self, value):
        self.global_annotations = value
        
    def get_global_annotations(self):
        return self.global_annotations
        
    def set_ms_resolution(self, value):
        self.ms_resolution = value
        
    def get_ms_resolution(self):
        return self.ms_resolution
        
    def set_show_tsuids(self, value):
        self.show_tsuids = value
    
    def get_show_tsuids(self):
        return self.show_tsuids
        
    def set_show_summary(self, value):
        self.show_summary = value
        
    def get_show_summary(self):
        return self.show_summary
        
    def set_show_stats(self,value):
        self.show_stats = value
        
    def get_show_stats(self):
        return self.show_stats
        
class QueryResponse(object):
    """ This holds the original query submitted by a client.  Each query submitted by the client
        will have a corresponding QueryResponse object. 
    
        The result of a query may contain more than one result due to an 'or' statement
        in a tag value.  This is why this object contains sub query results.
       
    """
    
    def __init__(self, metric, tag_dictionary, is_rate):
        """ The values passed in are the values given in a query.
        
            A Query response can have multiple results b/c of "or"
            values in the filter.
        Args:
            metric(String): The metric
            tag_dictionary(Dictionary): The tag-value configuration.
            is_rate(Boolean): True if rate info. Fals if count.
        """
        self.metric = metric
        self.tag_dictionary = tag_dictionary
        self.sub_query_results = []
        self.is_rate = is_rate
            
    def add_query_response(self, sub_query_result_obj):
        """ Add the QuerySubResponse object. This object contains the 
            time series data.
            
        Args:
            sub_query_result_obj (QuerySubResponse): One of the results to 
        a query.
        Returns:
            None
        """
        self.sub_query_results.append(sub_query_result_obj)
        
    def get_query_results(self):
        """ Returns a list of QuerySubResponse objects 
        
        Returns:
            List: A list of QuerySubResponse objects.
        """
        return self.sub_query_results
        
    def get_metric(self):
        """ Returns the metric from the client query. 
        
        Returns:
            String: The metric.
        """
        return self.metric
        
    def get_tag_dictionary(self):
        """ Returns the tag_name tag_value dictionary for the query
        
        Returns:
            Dictionary: Containing the tag values for the query.
        """
        return self.tag_dictionary
        
    def get_is_rate(self):
        """ Returns the is_rate setting for the query.
        Returns:
            Boolean: True if the query is for rate information. False if the
            query is for count information.
        """
        return self.is_rate
        
    def get_key_representation_dict(self):
        """ Returns a dictionary containing information for the
        used query.
        Returns:
            Dictionary: The response representation in dictionary format.
        """
        return {
            "metric":self.metric,
            "tags":self.tag_dictionary,
            "rate":self.is_rate
        }
        
    def __str__(self):
        return "\nOriginal Query\nmetric={}\nTags={}\nIs_Rate={}\nTotal Results={}\n\n{}\n".format(
            self.metric,
            self.tag_dictionary,
            self.is_rate,
            len(self.sub_query_results),
            self.sub_query_results)
    
    def __repr__(self):
        return self.__str__()        
        
class QuerySubResponse(object):
    """ Contains the results for a metric-tag combination.
    
        This would implement the MetricQueryResult interface.
    """
    
    def __init__(self, metric, tag_dictionary, time_series_data_obj, is_rate):
        """
        Args:
            metric (str): The metric for this result.
            tag_dictionary(dictionary): The tag-value pairs for this result.
            time_series_data_obj (TimeSeriesData): The object containing the timeseries data.
            is_rate(Boolean): True if rate info. False if count info.
        """
        self.metric = metric
        self.tag_dictionary = tag_dictionary
        self.time_series_data_obj = time_series_data_obj
        self.is_rate = is_rate
         
    def get_metric(self):
        """ Returns the metric
        Returns:
            String: The metric for the query result.
        """
        return self.metric

    def get_is_rate(self):
        """
        Returns:
            Boolean: True if this is rate info.  False if this is count info.
        """
        return self.is_rate
        
    def get_tag_dictionary(self):
        """ Returns the tag_name tag_value dictionary. 
            The value will not contain 'or' statements.
            
        Returns:
            Dictionary: The tag-values for this result.
        """
        return self.tag_dictionary
        
    def get_time_series_data_dict(self):
        """ Returns a dictionary containing a key as a timestamp
            and a count/rate value as its value.
            
        Returns:
            Dictionary: The timeseries data.  Key is a timestamp and the
            value is a rate or a count.
        """
        return self.time_series_data_obj.get_time_data()
        
    def get_key_representation_dict(self):
        """Returns dictionary representation of this QuerySubResponse
        object.  The timeseries data is not included.
        Returns:
            dictionary:  Keys "metric" and "tags"
        """
        return {
            "metric":self.metric,
            "tags":self.tag_dictionary,
            "rate":self.is_rate
        }
        
    def __str__(self):
        return "Query Result\nmetric={}\nTags={}\nData={}".format(
            self.metric,self.tag_dictionary,
            self.get_time_series_data_dict()
        )
    
    def __repr__(self):
        return self.__str__()

class TimeSeriesData(object):
    """ Used to hold the timeseries data.
    """
    def __init__(self, time_data_dict):
        self.time_date_dict = time_data_dict
        
    def get_time_data(self):
        """Returns the dictionary that contains the
        timeseries data.
        Returns:
            dictionary: Key is timestamp and value is the rate or count value.
        """
        return self.time_date_dict
        
def main():
    from srelib.tsdb.visualization import TSDBGraph
    request = TSDBRequest()
    request.set_start_time(1596727531)
    request.set_end_time(1596731131)
    

    query = TSDBQuery()
    query.set_metric("convex.cost")
    #query.add_tag_value("server_id","4518")
    query.add_tag_value("partner","PUBMATIC")
    query.add_tag_value("dc","I")
    query.add_tag_value("operation","*")
    qra = QueryRateOptions()
    qra.set_is_drop_resets(True)
    query.set_rate_options(qra)
    request.add_query(query)

    query3 = TSDBQuery()
    query3.set_metric("convex.cost")
    query3.add_tag_value("partner","PUBMATIC")
    query3.add_tag_value("dc","*")
    query3.add_tag_value("operation","*")
    qra = QueryRateOptions()
    qra.set_is_drop_resets(True)
    request.add_query(query3)

    query_2 = TSDBQuery()
    query_2.set_metric("bsy.messaging.results")
    query_2.add_tag_value("endpoint","*")
    query_2.add_tag_value("dc","I")
    request.add_query(query_2)

    client = TSDBClient()
    result_list = client.execute_request(request)
    print("--Results---")
    for result in result_list:
        print("")
        print(result)
        print("")
    return 0


    
    query = TSDBQuery()
    query.set_metric("bsy.requests")
    #default is group by
    #query.set_is_rate(False)
    query.add_tag_value("server_id","4518")
    query.add_tag_value("endpoint","fetch.rosetta.app.banner.jsonp.current|fetch.jac.app.banner.jsonp.current|fetch.ron.app.banner.jsonp.current|fetch.html5.player.video.vast.current")
    qra = QueryRateOptions()
    qra.set_is_drop_resets(True)
    query.set_rate_options(qra)
    
    #create a second query
    query2 = TSDBQuery()
    query2.set_metric("bsy.requests")
    #default is group by
    query2.add_tag_value("server_id","4518")
    query2.add_tag_value("endpoint","fetch.rosetta.app.banner.jsonp.current|fetch.jac.app.banner.jsonp.current|fetch.ron.app.banner.jsonp.current|fetch.html5.player.video.vast.current")
    query2.set_is_rate(False)
    
    request = TSDBRequest()
    request.set_start_time(1535464800)
    request.set_end_time(1535472000)
    request.add_query(query)
    request.add_query(query2)
    
    client = TSDBClient()
    #result_list = client.execute_request(request)
    #print(result_list)
    #print (json.dumps(json_data, indent=4))
    
    graph_url = TSDBGraph.get_url_for_tsdb_request(request)
    print(graph_url)
    
    #just want one of the graphs 
    limited_graphs = [query]
    print(TSDBGraph.get_url_for_tsdb_queries(request, limited_graphs))
    
    
if __name__ == '__main__':
    main()
        